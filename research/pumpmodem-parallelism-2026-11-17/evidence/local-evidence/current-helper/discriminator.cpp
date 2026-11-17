#include "datapump/triad_receiver.hpp"
#include "datapump/triad_stream.hpp"
#include "datapump/triad_stream_receiver.hpp"
#include "triad_receiver_executor.hpp"
#include "triad_receiver_helper.hpp"

#include <openssl/sha.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numbers>
#include <numeric>
#include <optional>
#include <sys/resource.h>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using namespace datapump;
using namespace datapump::triad::v3;
using namespace datapump::triad::v3::receiver_detail;
using Clock = std::chrono::steady_clock;
constexpr unsigned fs = 6000;
constexpr double arrival = .18;
constexpr double data_offset = 1.10;
constexpr double stale_offset = -.95;
constexpr double cn0_db_hz = 12;
constexpr double helper_voltage = .50;
constexpr double oscillator_bound = 1.5;
constexpr double atmospheric_bound = 3;
constexpr std::size_t lease_cap = 768 * 1024 * 1024;
constexpr std::size_t sample_cap = 360'000;

struct ProcessUsage {
    double user_seconds = 0, system_seconds = 0;
    long major_faults = 0, voluntary_switches = 0, involuntary_switches = 0;
};

ProcessUsage process_usage() {
    struct rusage usage{};
    if (getrusage(RUSAGE_SELF, &usage) != 0) throw std::runtime_error("getrusage failed");
    const auto seconds = [](const struct timeval& value) {
        return static_cast<double>(value.tv_sec) + 1e-6 * value.tv_usec;
    };
    return {seconds(usage.ru_utime), seconds(usage.ru_stime), usage.ru_majflt,
            usage.ru_nvcsw, usage.ru_nivcsw};
}

ProcessUsage usage_delta(const ProcessUsage& before, const ProcessUsage& after) {
    return {after.user_seconds - before.user_seconds, after.system_seconds - before.system_seconds,
            after.major_faults - before.major_faults, after.voluntary_switches - before.voluntary_switches,
            after.involuntary_switches - before.involuntary_switches};
}

void print_usage(const char* label, const ProcessUsage& usage) {
    std::cout << ' ' << label << "_user_cpu_seconds=" << usage.user_seconds
              << ' ' << label << "_system_cpu_seconds=" << usage.system_seconds
              << ' ' << label << "_major_faults=" << usage.major_faults
              << ' ' << label << "_voluntary_context_switches=" << usage.voluntary_switches
              << ' ' << label << "_involuntary_context_switches=" << usage.involuntary_switches;
}

void require_fixture(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

std::string digest(std::span<const Complex> samples) {
    const auto bytes = std::as_bytes(samples);
    std::array<unsigned char, SHA256_DIGEST_LENGTH> hash{};
    SHA256(reinterpret_cast<const unsigned char*>(bytes.data()), bytes.size(), hash.data());
    constexpr std::string_view digits = "0123456789abcdef";
    std::string result;
    for (const auto byte : hash) {
        result.push_back(digits[byte >> 4]);
        result.push_back(digits[byte & 15]);
    }
    return result;
}

std::vector<Complex> native_capture(const PublicProfile& profile, const Crypto& key,
        const ReceiverSlotPlan& slot, EmissionMode mode, double variance) {
    EmissionOptions options;
    options.mode = mode;
    Emission emission(profile, key, options);
    StreamChannelConfig config;
    config.effects.sample_rate = fs;
    config.effects.occupied_bandwidth_hz = profile.geometry().occupied_bandwidth_hz;
    config.effects.nominal_conversion_if_hz = profile.config().data_if_hz;
    config.effects.capture_lead_seconds = profile.config().capture_lead_seconds;
    config.effects.capture_trail_seconds = profile.config().capture_trail_seconds;
    config.effects.timing_offset_seconds = arrival;
    config.effects.seed = 37;
    config.complex_noise_variance = variance;
    config.minimum_capture_samples = slot.stop_sample;
    StreamingChannel channel(emission.source(), config);
    std::array<Complex, 4096> discard;
    while (channel.position() < slot.first_sample) {
        const auto rows = std::min<std::uint64_t>(discard.size(), slot.first_sample - channel.position());
        require_fixture(channel.read(std::span(discard).first(rows)) == rows, "short capture prefix");
    }
    std::vector<Complex> capture(slot.stop_sample - slot.first_sample);
    for (std::size_t first = 0; first < capture.size();) {
        const auto rows = std::min(discard.size(), capture.size() - first);
        require_fixture(channel.read(std::span(capture).subspan(first, rows)) == rows, "short capture");
        first += rows;
    }
    return capture;
}

double energy(std::span<const Complex> values) {
    return std::accumulate(values.begin(), values.end(), 0., [](auto sum, auto value) {
        return sum + std::norm(value);
    });
}

enum class Mode { weak_helper, canonical_helper, changing_common_frequency, six_db_data_common_frequency,
                  six_db_common_frequency_controls, six_db_quiet_timing };
constexpr double transition_begin = 58.6;
constexpr double transition_end = 59.7;

// One common CFO trajectory. Time coordinates here include the capture lead.
// Anchor the integrated phase at the end of the transition so later samples
// are identical to the aligned control.
double common_cycles(double t, double lead) {
    const auto begin = lead + transition_begin;
    const auto end = lead + transition_end;
    if (t >= end) return data_offset * t;
    const auto mid = (stale_offset + data_offset) / 2;
    if (t <= begin) return data_offset * end - mid * (end - begin) + stale_offset * (t - begin);
    const auto u = (t - begin) / (end - begin);
    return data_offset * end - mid * (end - t) -
        (data_offset - stale_offset) * (end - begin) / (2 * std::numbers::pi) * std::sin(std::numbers::pi * u);
}

double run(Mode mode, std::optional<std::uint8_t> bit = 1, bool compare_aligned = true,
           bool fixed_only = false, bool quiet_timing = false) {
    if (mode == Mode::six_db_data_common_frequency)
        require_fixture(bit && *bit == 1 && compare_aligned && !fixed_only,
                        "six-dB Helper discriminator requires the ordered bit-one pair");
    if (mode == Mode::six_db_common_frequency_controls)
        require_fixture((!bit || *bit == 0) && !compare_aligned && !fixed_only,
                        "six-dB controls require bit-zero and zero-DATA transition-only runs");
    if (mode == Mode::six_db_quiet_timing)
        require_fixture(!bit && !compare_aligned && !fixed_only && quiet_timing,
                        "six-dB quiet timing requires the single zero-DATA transition arm");
    PublicProfileConfig settings;
    settings.format.sample_rate = fs;
    settings.format.inner_rate_hz = 120;
    settings.format.added_symbols = 1;
    settings.format.bit_seconds = .001;
    settings.format.pulse_shape = PulseShape::TaperedRrc;
    settings.format.encrypt = true;
    settings.format.epoch = 1793850000;
    settings.format.symbol_ordinal = 15;
    settings.helper_enabled = true;
    settings.helper.data_power_w = 4;
    settings.helper.power_w = 8;
    settings.helper.callsign = "TRIAD";
    settings.capture_lead_seconds = 2;
    settings.capture_trail_seconds = .4;
    settings.arrival_low_seconds = -.4;
    settings.arrival_high_seconds = .4;
    settings.cfo_bound_hz = oscillator_bound + atmospheric_bound;
    settings.spread_delay_ms = 7;

    const auto key = Crypto::amateur();
    const PublicProfile profile(settings, key);
    ReceiverConfig config;
    config.sample_rate_hz = fs;
    config.data_if_hz = profile.data_if_hz();
    config.frequency_bound_hz = oscillator_bound;
    config.noise_variance = fs / std::pow(10., cn0_db_hz / 10);
    config.data_basis_gain = 1 / std::sqrt(data_power_reference(profile.config().format, key).mean_norm);
    config.helper_enabled = true;
    config.helper = profile.helper_plan();
    config.spread_delay_seconds = settings.spread_delay_ms / 1000;
    config.time_varying_channel = true;
    config.time_varying_atmospheric_hz = atmospheric_bound;
    config.time_varying_common_doppler_hz = atmospheric_bound;

    const auto slot = make_receiver_slot_plan(profile, config, 0);
    const auto rows = slot.stop_sample - slot.first_sample;
    std::cout << "capture_first=" << slot.first_sample << " capture_stop=" << slot.stop_sample
              << " rows=" << rows << " helper_begin=" << slot.helper_begin_seconds
              << " source_start=" << slot.source_start_seconds << std::endl;
    require_fixture(rows > 0 && rows <= sample_cap && slot.stop_sample <= 1'100'000,
                    "capture exceeds predeclared score or fixture horizon cap");
    const auto resources = resolve_stream_receiver_resources(StreamReceiverOptions{});
    if (mode == Mode::six_db_data_common_frequency || mode == Mode::six_db_common_frequency_controls ||
            mode == Mode::six_db_quiet_timing)
        require_fixture(resources.workers == 24, "six-dB Helper discriminator requires full W=24");
    const auto lease = receiver_slot_overlap_workspace(config, slot, resources.workers);
    require_fixture(lease <= lease_cap && lease <= resources.memory_limit_bytes, "slot exceeds predeclared memory cap");

    const auto noise = native_capture(profile, key, slot, EmissionMode::Quiet, config.noise_variance);
    const auto helper = native_capture(profile, key, slot, EmissionMode::HelperOnly, 0);
    std::vector<Complex> data(rows);
    if (bit) {
        PatternSource source(slot.format, key, *bit);
        Candidate truth;
        truth.arrival_seconds = static_cast<double>(slot.window_capture_lead_seconds + slot.source_start_seconds) + arrival;
        truth.frequency_hz = data_offset;
        std::vector<double> offsets(rows);
        std::iota(offsets.begin(), offsets.end(), 0.);
        shaped_basis_mapped(source, truth, fs, 0, offsets, data, config.data_if_hz);
        const auto data_attenuation_db = mode == Mode::changing_common_frequency ? -3. :
            (mode == Mode::six_db_data_common_frequency || mode == Mode::six_db_common_frequency_controls ||
             mode == Mode::six_db_quiet_timing) ? -6. : 0.;
        const auto amplitude = std::pow(10., data_attenuation_db / 20.);
        for (auto& sample : data) sample *= config.data_basis_gain * amplitude;
    }
    std::vector<Complex> base(rows);
    for (std::size_t i = 0; i < base.size(); ++i) base[i] = data[i] + noise[i];

    const auto voltage = mode == Mode::weak_helper ? helper_voltage : 1.;
    const auto changing_common = mode == Mode::changing_common_frequency ||
        mode == Mode::six_db_data_common_frequency || mode == Mode::six_db_common_frequency_controls ||
        mode == Mode::six_db_quiet_timing;
    const auto phase_begin = (settings.capture_lead_seconds + transition_begin) * fs;
    const auto phase_end = (settings.capture_lead_seconds + transition_end) * fs;
    if (changing_common) {
        const auto first = std::ranges::find_if(data, [](Complex sample) { return sample != Complex{}; });
        if (bit) require_fixture(first != data.end() && slot.first_sample + (first - data.begin()) > phase_end,
                                 "common trajectory must align before actual DATA support begins");
        else require_fixture(first == data.end(), "Helper-only control requires zero DATA voltage");
        require_fixture(slot.helper_begin_seconds + slot.arrival_upper_seconds + config.spread_delay_seconds + .02L + 36. < transition_begin,
                        "common trajectory moves inside the possible Helper fit aperture");
        double minimum = data_offset, maximum = stale_offset;
        for (auto row = static_cast<std::uint64_t>(phase_begin) - 2; row <= static_cast<std::uint64_t>(phase_end) + 2; ++row) {
            const auto a = row / static_cast<double>(fs);
            const auto b = (row + 1) / static_cast<double>(fs);
            const auto hz = (common_cycles(b, settings.capture_lead_seconds) - common_cycles(a, settings.capture_lead_seconds)) * fs;
            const auto u = std::clamp(((a + b) / 2 - settings.capture_lead_seconds - transition_begin) /
                                      (transition_end - transition_begin), 0., 1.);
            const auto expected = stale_offset + (data_offset - stale_offset) * .5 * (1 - std::cos(std::numbers::pi * u));
            require_fixture(std::abs(hz - expected) <= 1e-6 && std::abs(hz) < atmospheric_bound,
                            "common trajectory violates its continuous phase or frequency bound");
            minimum = std::min(minimum, hz);
            maximum = std::max(maximum, hz);
        }
        std::cout << std::setprecision(12) << "common_rate_min_hz=" << minimum << " common_rate_max_hz=" << maximum
                  << " transition_samples=[" << phase_begin << ',' << phase_end << "] first_data_sample="
                  << (bit ? static_cast<std::int64_t>(slot.first_sample + (first - data.begin())) : -1) << std::endl;
    }
    const auto data_attenuation_db = mode == Mode::changing_common_frequency ? -3. :
        (mode == Mode::six_db_data_common_frequency || mode == Mode::six_db_common_frequency_controls ||
         mode == Mode::six_db_quiet_timing) ? -6. : 0.;
    std::cout << std::setprecision(12) << "bit=" << (bit ? int(*bit) : -1) << " bit_seconds=" << profile.geometry().bit_seconds
              << " epoch=" << slot.format.epoch << " ordinal=" << slot.format.symbol_ordinal
              << " samples=" << rows << " quiet_begin=" << slot.quiet_first_sample << " quiet_end=" << slot.quiet_stop_sample
              << " H=" << resources.hardware_threads << " W=" << resources.workers << " lease=" << lease
              << " noise_variance=" << config.noise_variance
              << " data_present=" << bit.has_value()
              << " data_cn0_db_hz=" << (bit ? cn0_db_hz + data_attenuation_db : -1.)
              << " data_amplitude=" << (bit ? std::pow(10., data_attenuation_db / 20.) : 0.)
              << " arrival_prior_seconds=[" << slot.arrival_lower_seconds << ',' << slot.arrival_upper_seconds << ']'
              << " frequency_bound_hz=" << config.frequency_bound_hz
              << " atmospheric_bound_hz=" << config.time_varying_atmospheric_hz
              << " spread_delay_seconds=" << config.spread_delay_seconds
              << " data_energy_over_noise=" << energy(data) / config.noise_variance
              << " helper_voltage=" << voltage << " helper_energy_over_noise=" << voltage * voltage * energy(helper) / config.noise_variance
              << " data_sha256=" << digest(data) << " noise_sha256=" << digest(noise) << " base_sha256=" << digest(base)
              << std::endl;

    struct Arm { const char* name; double voltage; double offset; };
    const std::array arms{Arm{"aligned", voltage, data_offset},
                         Arm{changing_common ? "common-transition" : "stale", voltage, stale_offset},
                         Arm{"muted", 0, 0}};
    const auto helper_lease = helper_workspace(config, slot);
    require_fixture(helper_lease > 0 && helper_lease <= lease, "public Helper admission unsupported");
    std::string aligned_late_hash;
    double total_ordered_score_seconds = 0;
    unsigned scored_arms = 0;
    require_fixture(!quiet_timing || mode == Mode::six_db_quiet_timing,
                    "process timing is restricted to the dedicated zero-DATA run");
    for (const auto& arm : arms) {
        if (mode != Mode::weak_helper && arm.voltage == 0) continue;
        const auto transition = changing_common && arm.offset == stale_offset;
        if (!compare_aligned && !transition) continue;
        auto capture = base;
        if (arm.voltage != 0) {
            for (std::size_t i = 0; i < capture.size(); ++i) {
                const auto phase = transition && slot.first_sample + i < phase_end
                    ? 2 * std::numbers::pi * common_cycles((slot.first_sample + i) / static_cast<double>(fs),
                                                         settings.capture_lead_seconds)
                    : 2 * std::numbers::pi * (transition ? data_offset : arm.offset) *
                        (slot.first_sample + i) / fs;
                capture[i] += arm.voltage * helper[i] * std::polar(1., phase);
            }
        }
        if ((mode == Mode::six_db_common_frequency_controls || mode == Mode::six_db_quiet_timing) && !bit)
            require_fixture(digest(capture) == "4af2f6ae32d85d1006774d4e4a2905acb30c6c5a65f3513e346b725a25ac6fb8",
                            "zero-DATA quiet input differs from frozen fixed-only absence capture");
        if (changing_common) {
            const auto late_first = static_cast<std::size_t>(std::ceil(phase_end)) - slot.first_sample;
            const auto late_hash = digest(std::span<const Complex>(capture).subspan(late_first));
            if (transition && compare_aligned) require_fixture(late_hash == aligned_late_hash, "different IQ after common-phase alignment");
            else aligned_late_hash = late_hash;
            std::cout << arm.name << " same_late_first=" << late_first + slot.first_sample
                      << " late_sha256=" << late_hash << std::endl;
        }
        std::optional<ProcessUsage> manual_helper_before;
        std::optional<ProcessUsage> manual_helper_after;
        double manual_helper_wall = 0;
        {
            const auto began = Clock::now();
            if (quiet_timing) manual_helper_before = process_usage();
            ReceiverExecutor pool(resources.workers);
            const auto acquisition = score_helper(config, slot, capture, {}, helper_lease, {},
                                                   lane_wave(pool, slot.index, resources.workers, {}));
            const auto helper_elapsed = std::chrono::duration<double>(Clock::now() - began).count();
            manual_helper_wall = helper_elapsed;
            if (quiet_timing) manual_helper_after = process_usage();
            total_ordered_score_seconds += helper_elapsed;
            std::cout << arm.name << " capture_sha256=" << digest(capture)
                      << " helper=" << acquisition.reason << " intervals=";
            for (const auto& interval : acquisition.intervals)
                std::cout << '[' << interval.lower_hz << ',' << interval.upper_hz << ']';
            std::cout << " coarse_pilot_scores=" << acquisition.coarse_pilots[0].presence_score << ','
                      << acquisition.coarse_pilots[1].presence_score
                      << " onset_ratio=" << acquisition.onset_helper_level / acquisition.onset_noise_level
                      << " helper_seconds=" << helper_elapsed << std::endl;
        }
        if (quiet_timing) {
            std::cout << "manual_helper_process_timing helper_wall_seconds=" << manual_helper_wall;
            print_usage("helper", usage_delta(*manual_helper_before, *manual_helper_after));
            std::cout << std::endl;
        }
        const auto began = Clock::now();
        const auto receiver_usage_before = quiet_timing ? std::optional<ProcessUsage>(process_usage()) : std::nullopt;
        const auto score = score_receiver_slot(config, slot, key, capture, {}, resources.workers, lease);
        const auto elapsed = std::chrono::duration<double>(Clock::now() - began).count();
        const auto receiver_usage_after = quiet_timing ? std::optional<ProcessUsage>(process_usage()) : std::nullopt;
        const auto receiver_usage = quiet_timing ?
            std::optional<ProcessUsage>(usage_delta(*receiver_usage_before, *receiver_usage_after)) : std::nullopt;
        total_ordered_score_seconds += elapsed;
        ++scored_arms;
        const char* decision = score.decision == SlotDecision::data ? "DATA" :
            score.decision == SlotDecision::quiet ? "QUIET" : "AMBIGUOUS";
        std::cout << arm.name << " decision=" << decision << " bit=" << (score.bit ? int(*score.bit) : -1)
                  << " expected_bit=" << (bit ? int(*bit) : -1)
                  << " reason=" << score.reason << " helper=" << score.helper_status
                  << " operational=" << score.operational_log_e << "/" << score.operational_threshold
                  << " affine=" << score.bit_evidence[0] << ',' << score.bit_evidence[1]
                  << " ordinary=" << score.varying_bit_evidence[0] << ',' << score.varying_bit_evidence[1]
                  << " operational_bits=" << score.operational_bit_evidence[0] << ',' << score.operational_bit_evidence[1]
                  << " selected_prior_mass=" << score.selected_prior_mass
                  << " operational_separation=" << score.operational_bit_log_separation
                  << " minimum_bit_separation=" << score.operational_minimum_bit_log_separation
                  << " noise_statistics_valid=" << score.noise_statistics_valid
                  << " gain=" << score.nominal_independent_gain_bit_evidence[0] << ',' << score.nominal_independent_gain_bit_evidence[1]
                  << " gain_states=" << score.nominal_independent_gain_frequency_states << " gain_atoms=" << score.nominal_independent_gain_candidates
                  << " gain_emission_cells=" << score.independent_gain_emission_cells
                  << " coherent=" << score.coherent_gain_status << ':' << score.coherent_gain_bit_evidence[0] << ','
                  << score.coherent_gain_bit_evidence[1] << " drift=" << score.drift_status << ':'
                  << score.drift_bit_evidence[0] << ',' << score.drift_bit_evidence[1]
                  << " coarse_points=" << score.coarse_frequency_points << " full_varying_points=" << score.varying_timing_frequencies
                  << " fine_rows=" << score.basis_rows << " varying_rows=" << score.varying_basis_rows
                  << " complete=" << score.complete << " all_valid=" << score.all_valid
                  << " zero_h0=" << score.zero_h0_verified << " consumed_samples=" << score.consumed_samples
                  << " adaptive_diagnostics=" << score.adaptive_diagnostics << " adaptive_blocks=" << score.adaptive_blocks
                  << " adaptive_edges=" << score.adaptive_transition_edges << " adaptive_peak=" << score.adaptive_peak_states
                  << " workspace=" << score.workspace_peak_bytes << " wall_seconds=" << elapsed << std::endl;
        if (quiet_timing) {
            std::cout << "receiver_stage_timing helper_seconds=" << score.helper_seconds
                      << " helper_overlapped=" << score.helper_overlapped
                      << " coarse_seconds=" << score.coarse_seconds
                      << " fine_seconds=" << score.fine_seconds
                      << " varying_coarse_seconds=" << score.varying_coarse_seconds
                      << " varying_fine_seconds=" << score.varying_fine_seconds
                      << " coherent_gain_seconds=" << score.coherent_gain_seconds
                      << " drift_seconds=" << score.drift_seconds
                      << " drift_timing_atoms=" << score.drift_timing_atoms
                      << " drift_slopes=" << score.drift_slopes
                      << " drift_frequency_bins=" << score.drift_frequency_bins
                      << " drift_observation_rows=" << score.drift_observation_rows
                      << " drift_proposal_stride=" << score.drift_proposal_stride
                      << " line_frequency_hz=" << score.varying_line_frequency_hz
                      << " line_log_evidence=" << score.varying_line_log_evidence;
            print_usage("receiver", *receiver_usage);
            std::cout << std::endl;
        }
        require_fixture(score.complete && score.all_valid && score.zero_h0_verified && score.consumed_samples == rows,
                        "native slot did not preserve its full valid aperture");
        if (mode == Mode::six_db_common_frequency_controls || mode == Mode::six_db_quiet_timing)
            require_fixture(score.noise_statistics_valid,
                            "six-dB control did not report valid noise statistics");
        if ((mode == Mode::six_db_common_frequency_controls || mode == Mode::six_db_quiet_timing) && !bit)
            require_fixture(score.decision == SlotDecision::quiet,
                            "zero-DATA control did not produce a quiet decision");
        if (fixed_only)
            require_fixture(!score.adaptive_diagnostics && !score.adaptive_blocks && !score.adaptive_transition_edges &&
                            !score.adaptive_peak_states, "production score executed adaptive diagnostics");
    }
    if (mode == Mode::six_db_data_common_frequency) {
        require_fixture(scored_arms == 2, "six-dB Helper discriminator must score exactly two wanted arms");
        require_fixture(total_ordered_score_seconds <= 45., "six-dB ordered scores exceeded the 45-second budget");
        std::cout << "ordered_scores=2 total_ordered_score_seconds=" << total_ordered_score_seconds << std::endl;
    }
    if (mode == Mode::six_db_common_frequency_controls)
        require_fixture(scored_arms == 1, "each six-dB control run must score only the common-transition arm");
    if (mode == Mode::six_db_quiet_timing)
        require_fixture(scored_arms == 1 && total_ordered_score_seconds <= 45.,
                        "six-dB quiet timing must score exactly one arm within its 45-second budget");
    return total_ordered_score_seconds;
}
}

int main(int argc, char** argv) {
    try {
        require_fixture(argc <= 2, "invalid discriminator mode");
        const std::string_view mode = argc == 2 ? argv[1] : "";
        if (mode.empty()) run(Mode::weak_helper);
        else if (mode == "canonical-helper-power") run(Mode::canonical_helper);
        else if (mode == "lower-data-common-frequency") run(Mode::changing_common_frequency);
        else if (mode == "six-db-data-common-frequency") run(Mode::six_db_data_common_frequency);
        else if (mode == "six-db-common-frequency-controls") {
            const auto bit_zero_seconds = run(Mode::six_db_common_frequency_controls, 0, false);
            const auto zero_data_seconds = run(Mode::six_db_common_frequency_controls, {}, false);
            const auto total = bit_zero_seconds + zero_data_seconds;
            require_fixture(total <= 45., "six-dB ordered controls exceeded the 45-second budget");
            std::cout << "control_scores=2 total_ordered_score_seconds=" << total << std::endl;
        }
        else if (mode == "six-db-quiet-timing")
            run(Mode::six_db_quiet_timing, {}, false, false, true);
        else if (mode == "lower-data-common-frequency-controls") {
            run(Mode::changing_common_frequency, 0, false);
            run(Mode::changing_common_frequency, {}, false);
        }
        else if (mode == "fixed-only-common-frequency") {
            run(Mode::changing_common_frequency, 1, false, true);
            run(Mode::changing_common_frequency, 0, false, true);
            run(Mode::changing_common_frequency, {}, false, true);
        }
        else throw std::runtime_error("invalid discriminator mode");
    }
    catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
