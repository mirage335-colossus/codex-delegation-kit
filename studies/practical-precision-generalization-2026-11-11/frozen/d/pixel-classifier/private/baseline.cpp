#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

using DefaultCalc = double;

static float sensor_value(size_t pixel, int channel, int seed) {
    uint32_t v = uint32_t(pixel * 747796405u + uint32_t(channel) * 2891336453u + uint32_t(seed) * 277803737u);
    v = ((v >> ((v >> 28) + 4)) ^ v) * 277803737u;
    v = (v >> 22) ^ v;
    return float(v & 0x00ffffffu) / 16777215.0f;
}

template<class T>
static int run_case(int width, int height, int seed) {
    const size_t n = size_t(width) * size_t(height);
    std::vector<float> input(n * 8);
    for (size_t p = 0; p < n; ++p)
        for (int c = 0; c < 8; ++c) input[p * 8 + c] = sensor_value(p, c, seed);

    std::vector<T> feature_a(n), feature_b(n), score(n);
    const T one = T(1);
    for (size_t p = 0; p < n; ++p) {
        const float* x = &input[p * 8];
        T u = T(x[0]) * T(x[1]) + T(0.35) * T(x[2]) * T(x[3]) - T(0.20) * T(x[4]) - T(0.17);
        T v = T(x[5]) * T(x[6]) - T(0.25) * T(x[7]) + T(0.10) * T(x[0]) - T(0.13);
        feature_a[p] = u / (one + std::abs(u));
        feature_b[p] = v / (one + std::abs(v));
    }
    for (size_t p = 0; p < n; ++p) {
        const float* x = &input[p * 8];
        T d0 = T(x[3]) - T(x[7]);
        T d1 = T(x[1]) - T(x[6]);
        T z = T(0.12) + T(0.66) * T(x[0]) - T(0.39) * T(x[1])
            + T(0.31) * T(x[2]) * T(x[4]) - T(0.27) * T(x[5])
            + T(0.45) * feature_a[p] - T(0.26) * feature_b[p]
            + T(0.13) * feature_a[p] * feature_b[p]
            + T(0.17) * d0 * d0 - T(0.08) * d1 * d1;
        score[p] = T(0.5) + T(0.5) * z / (one + std::abs(z));
    }

    double bins[32][3] = {};
    for (size_t i = 0; i < n; ++i) {
        const double q = static_cast<double>(score[i]);
        const int b = int(i % 32);
        bins[b][0] += q;
        bins[b][1] += q * q;
        bins[b][2] += q >= 0.5 ? 1.0 : 0.0;
    }
    const size_t ids[7] = {0, n / 17, n / 5, n / 2, (3 * n) / 4, (16 * n) / 17, n - 1};
    const size_t storage = input.capacity() * sizeof(float)
        + (feature_a.capacity() + feature_b.capacity() + score.capacity()) * sizeof(T);
    std::cout << std::setprecision(12) << "{\"storage_bytes\":" << storage << ",\"checksums\":[";
    for (int b = 0; b < 32; ++b) {
        if (b) std::cout << ',';
        std::cout << '[' << bins[b][0] << ',' << bins[b][1] << ',' << bins[b][2] << ']';
    }
    std::cout << "],\"samples\":[";
    for (int i = 0; i < 7; ++i) {
        if (i) std::cout << ',';
        std::cout << static_cast<double>(score[ids[i]]);
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
