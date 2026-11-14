// Standalone authorized research probe of two existing native helpers.
// Does not build PumpModem, instantiate StreamingChannel, or run a receiver.
#include "triad_gaussian_fading.hpp"
#include "triad_random_process.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numbers>
#include <string_view>

using datapump::triad::v3::detail::FixedGaussianProcess;
using datapump::triad::v3::detail::GaussianRayFading;

int failures = 0;
int assertions = 0;
void check(bool pass, std::string_view why) {
    ++assertions;
    if (!pass) {
        std::cout << "FAIL: " << why << '\n';
        ++failures;
    }
}

int main() {
    std::cout << std::setprecision(10);
    try {
        const auto unexpected = GaussianRayFading::tap_count(.1,1./960);
        std::cout << "rx-clock taps unexpectedly accepted: " << unexpected << '\n';
        check(false, "960 Hz/B=.1 Hz should exceed 8193-tap native bound");
    } catch (const datapump::Error& e) {
        check(std::string_view(e.what()).find("8193-tap") != std::string_view::npos,
              "right native tap-cap rejection");
        std::cout << "rx-clock B=.1Hz at Fs=960 rejected: " << e.what() << '\n';
    }

    for (const double width : {.5,30.}) {
        constexpr double fs = 960.;
        GaussianRayFading h(width,1/fs,1234);
        const auto coefficients = h.coefficients();
        long double norm = 0;
        for (const auto coefficient : coefficients) norm += coefficient*coefficient;
        check(std::abs(norm-1) < 1e-12, "native finite FIR unit variance");
        long double e_max = 0;
        for (const double z : {.0625,.125,.25,.45,.5,.75,1.,1.5,2.}) {
            const auto lag = static_cast<std::uint64_t>(std::llround(z*fs/width));
            const auto w = std::numbers::pi_v<long double>*width*lag/fs;
            const auto target = std::exp(-w*w/2);
            e_max = std::max(e_max,std::abs(h.covariance(lag)-target));
        }
        check(e_max < 1e-11, "finite native covariance for these grid lags");
        std::cout << "rx-clock B=" << width << " Hz taps=" << coefficients.size()
                  << " max sampled covariance error=" << e_max << '\n';
    }

    for (const double width : {.1,30.}) {
        // at every 1/16 sec exactly, one direct query and two different
        // dense sampling rates (640 and 960) must return same field value,
        // independent of how many noncommon times and knots were queried.
        FixedGaussianProcess sparse(width,9876543), a(width,9876543), b(width,9876543);
        std::cout << "fixed-time B=" << width << " Hz: " << sparse.coefficients().size()
                  << " taps, " << sparse.knot_rate_hz() << " knots/s";
        check(sparse.coefficients().size() == 53, "fixed-grid FIR support");
        check(std::abs(sparse.knot_rate_hz()-16*width) < 1e-12, "fixed physical knot rate");
        constexpr int periods = 64;
        int agreements = 0;
        for (int w = 0; w < periods; ++w) {
            const auto target = static_cast<long double>(w)/16;
            const auto reference = sparse.value(target);
            for (int k = 0; k < 40; ++k) a.value(target+static_cast<long double>(k-40)/640);
            for (int k = 0; k < 60; ++k) b.value(target+static_cast<long double>(k-60)/960);
            agreements += reference == a.value(target) && reference == b.value(target);
        }
        check(agreements == periods, "counter-based field matches exactly at common physical times");
        std::cout << "; exact common positions=" << agreements << '/' << periods << '\n';
    }

    constexpr std::uint64_t roots = 8192;
    constexpr double width=.1;
    constexpr long double lag=4.5L;
    long double sx=0, sy=0, px=0, py=0, sxy=0, psxy=0;
    for (std::uint64_t seed=0; seed<roots; ++seed) {
        FixedGaussianProcess process(width,seed);
        const auto x=process.value(0), y=process.value(lag);
        sx+=x; sy+=y; px+=x*x; py+=y*y;
        const auto z=x*y;
        sxy+=z; psxy+=z*z;
    }
    const auto mxy=sxy/roots;
    const auto se=std::sqrt((psxy/roots-mxy*mxy)/(roots-1));
    constexpr double desk_fixed_avg=.3682454874;
    const auto gap=mxy-desk_fixed_avg;
    std::cout << "fixed-grid across " << roots << " deterministic seed roots, normalized lag .45: means="
              << sx/roots << ',' << sy/roots << " second moments=" << px/roots << ',' << py/roots
              << " E[XY]=" << mxy << " estimated IID SE=" << se << " gap to desk=" << gap
              << " (" << gap/se << " apparent SEs)\n";
    // Roots of one deterministic generator are a useful sampling check,
    // not measured link episodes or a proof of seed IID/exact covariance.
    check(std::abs(gap)<5*se, "coarse seed check within 5 apparent IID SEs");
    std::cout << assertions << " checks, " << failures << " failures\n";
    return failures != 0;
}
