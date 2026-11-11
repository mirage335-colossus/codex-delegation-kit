#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>

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
    double bins[32][3] = {};
    const size_t ids[7] = {0, n / 17, n / 5, n / 2, (3 * n) / 4, (16 * n) / 17, n - 1};
    double samples[7] = {};
    const T one = T(1);

    // Pixels are independent, so generate their eight sensor values and score
    // them in place instead of retaining image, feature, and score planes.
    for (size_t p = 0; p < n; ++p) {
        T x[8];
        for (int c = 0; c < 8; ++c) x[c] = T(sensor_value(p, c, seed));
        const T u = x[0] * x[1] + T(0.35) * x[2] * x[3] - T(0.20) * x[4] - T(0.17);
        const T v = x[5] * x[6] - T(0.25) * x[7] + T(0.10) * x[0] - T(0.13);
        const T a = u / (one + std::abs(u));
        const T b = v / (one + std::abs(v));
        const T d0 = x[3] - x[7];
        const T d1 = x[1] - x[6];
        const T z = T(0.12) + T(0.66) * x[0] - T(0.39) * x[1]
            + T(0.31) * x[2] * x[4] - T(0.27) * x[5]
            + T(0.45) * a - T(0.26) * b + T(0.13) * a * b
            + T(0.17) * d0 * d0 - T(0.08) * d1 * d1;
        const T score = T(0.5) + T(0.5) * z / (one + std::abs(z));
        const double q = static_cast<double>(score);
        const int bucket = int(p % 32);
        bins[bucket][0] += q;
        bins[bucket][1] += q * q;
        bins[bucket][2] += q >= 0.5 ? 1.0 : 0.0;
        for (int i = 0; i < 7; ++i) if (p == ids[i]) samples[i] = q;
    }

    std::cout << std::setprecision(12) << "{\"storage_bytes\":0,\"checksums\":[";
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
