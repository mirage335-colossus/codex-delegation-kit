#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

using DefaultCalc = float;

static float sensor_value(size_t pixel, int channel, int seed) {
    uint32_t v = uint32_t(pixel * 747796405u + uint32_t(channel) * 2891336453u + uint32_t(seed) * 277803737u);
    v = ((v >> ((v >> 28) + 4)) ^ v) * 277803737u;
    v = (v >> 22) ^ v;
    return float(v & 0x00ffffffu) / 16777215.0f;
}

template<class T>
static int run_case(int width, int height, int seed) {
    const size_t n = size_t(width) * size_t(height);
    const T one = T(1);
    double bins[32][3] = {};
    const size_t ids[7] = {0, n / 17, n / 5, n / 2, (3 * n) / 4, (16 * n) / 17, n - 1};
    double samples[7] = {};
    for (size_t p = 0; p < n; ++p) {
        float xf[8];
        for (int c = 0; c < 8; ++c) xf[c] = sensor_value(p, c, seed);
        const T x0 = T(xf[0]), x1 = T(xf[1]), x2 = T(xf[2]), x3 = T(xf[3]);
        const T x4 = T(xf[4]), x5 = T(xf[5]), x6 = T(xf[6]), x7 = T(xf[7]);
        T u = x0 * x1 + T(0.35) * x2 * x3 - T(0.20) * x4 - T(0.17);
        T v = x5 * x6 - T(0.25) * x7 + T(0.10) * x0 - T(0.13);
        const T feature_a = u / (one + std::abs(u));
        const T feature_b = v / (one + std::abs(v));
        T d0 = x3 - x7;
        T d1 = x1 - x6;
        T z = T(0.12) + T(0.66) * x0 - T(0.39) * x1
            + T(0.31) * x2 * x4 - T(0.27) * x5
            + T(0.45) * feature_a - T(0.26) * feature_b
            + T(0.13) * feature_a * feature_b
            + T(0.17) * d0 * d0 - T(0.08) * d1 * d1;
        const T score = T(0.5) + T(0.5) * z / (one + std::abs(z));
        const double q = static_cast<double>(score);
        const int b = int(p % 32);
        bins[b][0] += q;
        bins[b][1] += q * q;
        bins[b][2] += q >= 0.5 ? 1.0 : 0.0;
        for (int i = 0; i < 7; ++i)
            if (p == ids[i]) samples[i] = q;
    }
    const size_t storage = 0;
    std::cout << std::setprecision(12) << "{\"storage_bytes\":" << storage << ",\"checksums\":[";
    for (int b = 0; b < 32; ++b) {
        if (b) std::cout << ',';
        std::cout << '[' << bins[b][0] << ',' << bins[b][1] << ',' << bins[b][2] << ']';
    }
    std::cout << "],\"samples\":[";
    for (int i = 0; i < 7; ++i) {
        if (i) std::cout << ',';
        std::cout << samples[i];
    }
    std::cout << "]}\n";
    return 0;
}

int main(int argc, char** argv) {
    const int width = argc > 1 ? std::atoi(argv[1]) : 64;
    const int height = argc > 2 ? std::atoi(argv[2]) : 48;
    const int seed = argc > 3 ? std::atoi(argv[3]) : 19;
    const bool audit = argc > 4 && std::strcmp(argv[4], "--audit") == 0;
    if (width < 1 || height < 1 || width > 4096 || height > 2160) return 2;
    return audit ? run_case<double>(width, height, seed) : run_case<DefaultCalc>(width, height, seed);
}
