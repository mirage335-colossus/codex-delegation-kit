#include "appraisal/channel.hpp"
#include <openssl/evp.h>
#include <bit>
#include <memory>
#include "datapump/execution_resources.hpp"
#include "datapump/triad_stream_receiver.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>

namespace {
using namespace datapump;
using namespace datapump::triad::v3;
using Clock = std::chrono::steady_clock;
constexpr auto seed = 9202U;
constexpr auto index = 0U;
constexpr auto cn0_db_hz = 12.;
constexpr auto public_delay_seconds = .021;
constexpr std::uint64_t memory_limit = 3ULL * 1024 * 1024 * 1024;
constexpr std::uint64_t maximum_samples = 270'000;

void require(bool accepted, const char* message) {
    if (!accepted) throw Error(message);
}
std::string digest(std::span<const Complex> iq) {
    static_assert(std::endian::native == std::endian::little);
    using Context = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    Context context(EVP_MD_CTX_new(), &EVP_MD_CTX_free);
    require(context && EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) == 1, "digest init");
    for (const auto sample : iq) {
        const std::array<double,2> row{sample.real(), sample.imag()};
        constexpr unsigned char valid = 1;
        require(EVP_DigestUpdate(context.get(), row.data(), sizeof(row)) == 1 &&
            EVP_DigestUpdate(context.get(), &valid, 1) == 1, "digest row");
    }
    std::array<unsigned char,EVP_MAX_MD_SIZE> hash{};
    unsigned size = 0;
    require(EVP_DigestFinal_ex(context.get(), hash.data(), &size) == 1, "digest finish");
    std::string result;
    constexpr char hex[] = "0123456789abcdef";
    for (unsigned i = 0; i < size; ++i) {
        result += hex[hash[i] >> 4];
        result += hex[hash[i] & 15];
    }
    return result;
}
}

int main(int argc, char** argv) {
    try {
        require(argc == 2, "expected one frozen delay case");
        const std::string_view test = argv[1];
        const bool noise_only = test == "noise";
        require(test == "15.75-0" || test == "5.25-0" || test == "10.5-0" ||
                test == "15.75-1" || noise_only, "unknown finite delay control");
        const auto actual_delay_seconds = test == "5.25-0" ? .00525 : test == "10.5-0" ? .0105 : .01575;
        const auto wanted_bit = static_cast<std::uint8_t>(test == "15.75-1");
        const auto began = Clock::now();
        const auto hardware = execution::host_resources();
        const unsigned workers = 2 * hardware.hardware_threads;
        const auto memory = std::min(memory_limit, hardware.available_memory_bytes.value_or(memory_limit));
        const auto key = Crypto::amateur();
        auto scenario = appraisal::make_scenario("hf-disturbed");
        require(scenario.waveform.sample_rate_hz == 1920 && scenario.waveform.rate_hz == 36 &&
            scenario.waveform.added_symbols == 10 && scenario.channel.paths.size() == 2 &&
            scenario.channel.paths[0].delay_seconds == 0 && scenario.channel.paths[1].delay_seconds == .007 &&
            scenario.bounds.doppler_width_hz == 30 && scenario.bounds.frequency_bound_hz == 0 &&
            scenario.bounds.atmospheric_hz == 90,
            "fixed hf-disturbed model fingerprint");

        // Hold the receiver declaration at 21 ms while moving only the actual
        // second path to an off-anchor point inside that public allowance.
        scenario.channel.paths[1].delay_seconds = actual_delay_seconds;
        scenario.bounds.spread_seconds = public_delay_seconds;
        PublicProfileConfig profile_config;
        profile_config.format.sample_rate = scenario.waveform.sample_rate_hz;
        profile_config.format.inner_rate_hz = scenario.waveform.rate_hz;
        profile_config.format.added_symbols = scenario.waveform.added_symbols;
        profile_config.format.bit_seconds = 128;
        profile_config.format.encrypt = true;
        profile_config.format.epoch = 1793404800;
        profile_config.format.symbol_ordinal = 0;
        profile_config.format.configured_carrier_hz = scenario.channel.rf_hz;
        profile_config.format.pulse_shape = PulseShape::Rrc;
        profile_config.data_if_hz = 240;
        profile_config.capture_lead_seconds = .25;
        profile_config.arrival_low_seconds = scenario.bounds.arrival_low_seconds;
        profile_config.arrival_high_seconds = scenario.bounds.arrival_high_seconds;
        profile_config.cfo_bound_hz = scenario.bounds.frequency_bound_hz + scenario.bounds.atmospheric_hz;
        profile_config.clock_bound_ppm = 0;
        profile_config.spread_delay_ms = 1000 * public_delay_seconds;
        profile_config.spread_doppler_hz = scenario.bounds.doppler_width_hz;
        const auto filter_tail = appraisal::channel_filter_tail_seconds(scenario.channel,
            profile_config.format.sample_rate);
        profile_config.receiver_filter_halo_samples = static_cast<std::uint64_t>(
            std::ceil(filter_tail * profile_config.format.sample_rate));
        const PublicProfile profile(profile_config);

        ReceiverConfig receiver;
        receiver.sample_rate_hz = profile.effective_sample_rate();
        receiver.data_if_hz = profile_config.data_if_hz;
        receiver.frequency_bound_hz = scenario.bounds.frequency_bound_hz;
        receiver.clock_bound_ppm = 0;
        receiver.time_varying_atmospheric_hz = scenario.bounds.atmospheric_hz;
        receiver.spread_delay_seconds = public_delay_seconds;
        receiver.random_doppler_width_hz = scenario.bounds.doppler_width_hz;
        receiver.time_varying_channel = scenario.bounds.varying;
        receiver.time_varying_common_doppler_hz = std::max(scenario.bounds.doppler_width_hz,
            scenario.bounds.atmospheric_hz);
        receiver.capture_tail_bound_seconds = filter_tail;
        receiver.noise_variance = receiver.sample_rate_hz / std::pow(10., cn0_db_hz / 10.);
        receiver.data_basis_gain = 1 / std::sqrt(data_power_reference(profile.config().format, key).mean_norm);
        const auto slot = make_receiver_slot_plan(profile, receiver, index);
        const auto count = slot.stop_sample - slot.first_sample;
        const auto duration = profile.geometry().bit_seconds;
        const auto source_first = profile.calendar().distance(profile.origin(), profile.transmit_slot(index).helper_begin);
        require(std::abs(duration - 139.2) < 1e-10 && slot.format.symbol_ordinal == index &&
            slot.format.epoch == 1793404800 && slot.format.bit_seconds == 128 &&
            slot.arrival_lower_seconds == 0 && slot.arrival_upper_seconds == .01 && count <= maximum_samples &&
            receiver.spread_delay_seconds == public_delay_seconds && receiver.clock_bound_ppm == 0 &&
            scenario.channel.paths[1].delay_seconds == actual_delay_seconds,
            "predeclared 139.2-second slot/public geometry changed");

        const auto lease = receiver_slot_workspace(receiver, slot, workers);
        const auto reserved = execution::process_footprint_bytes() + execution::worker_stack_bytes() * (workers - 1) +
            count * sizeof(Complex) + scenario.channel.maximum_workspace_bytes;
        require(reserved < memory && lease <= memory - reserved,
            "interior-delay aperture exceeds its explicit host resource budget");

        const std::array bits{wanted_bit};
        EmissionOptions options;
        options.first_slot = index;
        options.source_first_sample = source_first;
        options.bits = noise_only ? std::span<const std::uint8_t>() : bits;
        if (noise_only) { options.mode = EmissionMode::Quiet; options.slot_count = 1; }
        Emission emission(profile, key, options);
        auto channel_config = scenario.channel;
        channel_config.noise.white_variance = receiver.noise_variance;
        channel_config.noise_seed = seed;
        std::vector<Complex> iq(static_cast<std::size_t>(count));
        // Use the analytic channel's canonical emitted source: the public
        // capture preroll is supplied in source coordinates.
        const auto first_data_sample = emission.report().first_data_sample;
        const auto preroll = static_cast<std::uint64_t>(std::llround(profile_config.capture_lead_seconds *
            receiver.sample_rate_hz));
        require(preroll == 480 && first_data_sample == 0 && slot.first_sample == 0 &&
                slot.window_capture_lead_seconds == .25,
                "original direct source support and public lead are not the frozen slot-zero geometry");
        auto emitted = emission.source();
        const auto sample = emitted.sample_at;
        emitted.sample_at = [sample, preroll](std::uint64_t i) {
            return i < preroll ? Complex{} : sample(i - preroll);
        };
        emitted.geometry.source_samples += preroll;
        appraisal::Channel channel(emitted, channel_config, seed, count);
        require(channel.read(iq) == count, "full native channel aperture did not render");
        const auto signal_energy = channel.report().signal_energy;
        const auto noise_energy = channel.report().additive_noise_energy;
        const auto rendered = channel.report().samples;
        const auto source_gain = emission.report().data_gain;
        const auto score_start = Clock::now();
        const auto score = score_receiver_slot(receiver, slot, key, iq, {}, workers, lease);
        require(score.complete && score.all_valid && score.zero_h0_verified && score.consumed_samples == count,
            "native receiver did not score the complete interior-delay aperture");
        const char* decision = score.decision == SlotDecision::data ? "DATA" :
            score.decision == SlotDecision::quiet ? "QUIET" : "AMBIGUOUS";

        std::cout << std::setprecision(17)
            << "uncorrected_direct_origin_rows " << first_data_sample
            << " corrected_direct_origin_rows " << first_data_sample + preroll
            << " public_earliest_direct_rows " << slot.window_capture_lead_seconds * receiver.sample_rate_hz
            << " public_latest_direct_rows " <<
                (slot.window_capture_lead_seconds + slot.arrival_upper_seconds) * receiver.sample_rate_hz
            << " capture_sha256 " << digest(iq) << " control " << test
            << " scenario hf-disturbed actual_second_path_delay_seconds " << actual_delay_seconds
            << " public_spread_delay_seconds " << receiver.spread_delay_seconds
            << " public_arrival_seconds " << slot.arrival_lower_seconds << ',' << slot.arrival_upper_seconds
            << " per_ray_doppler_2sigma_hz " << receiver.random_doppler_width_hz
            << " common_frequency_bound_hz " << receiver.time_varying_atmospheric_hz
            << " relative_doppler_hz " << receiver.spread_doppler_hz
            << " cn0_db_hz " << cn0_db_hz << " seed " << seed
            << " slot " << slot.index << " epoch " << slot.format.epoch
            << " ordinal " << slot.format.symbol_ordinal << " actual_bit_seconds " << duration
            << " samples " << count << " rendered " << rendered << " source_gain " << source_gain
            << " received_signal_energy " << signal_energy << " additive_noise_energy " << noise_energy
            << " hardware_threads " << hardware.hardware_threads << " workers " << workers
            << " admitted_workspace_bytes " << lease << " explicit_memory_budget_bytes " << memory
            << " channel_render_seconds " << std::chrono::duration<double>(score_start - began).count()
            << " receiver_score_seconds " << std::chrono::duration<double>(Clock::now() - score_start).count()
            << " decision " << decision << " bit " << (score.bit ? int(*score.bit) : -1)
            << " expected_bit " << int(wanted_bit)
            << " operational_log_e " << score.operational_log_e
            << " operational_threshold " << score.operational_threshold
            << " gain_candidate_count " << score.nominal_independent_gain_candidates
            << " gain_frequency_states " << score.nominal_independent_gain_frequency_states
            << " gain_evidence0 " << score.nominal_independent_gain_bit_evidence[0]
            << " gain_evidence1 " << score.nominal_independent_gain_bit_evidence[1]
            << " gain_basis_rows " << score.nominal_independent_gain_basis_rows
            << " varying_basis_rows " << score.varying_basis_rows
            << " end_to_end_seconds " << std::chrono::duration<double>(Clock::now() - began).count()
            << '\n';

        return (noise_only ? score.decision == SlotDecision::quiet :
                            score.decision == SlotDecision::data && score.bit == wanted_bit) ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "interior-delay witness setup/validation: " << error.what() << '\n';
        return 1;
    }
}
