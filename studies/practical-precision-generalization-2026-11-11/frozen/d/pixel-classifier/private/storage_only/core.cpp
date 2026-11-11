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
    std::vector<float> input(n * 8);
    for (size_t p = 0; p < n; ++p)
        for (int c = 0; c < 8; ++c) input[p * 8 + c] = sensor_value(p, c, seed);

    std::vector<float> feature_a(n), feature_b(n), score(n);
    const T one = T(1);
    for (size_t p = 0; p < n; ++p) {
        const float* x = &input[p * 8];
        double u = double(x[0]) * double(x[1]) + 0.35 * double(x[2]) * double(x[3]) - 0.20 * double(x[4]) - 0.17;
        double v = double(x[5]) * double(x[6]) - 0.25 * double(x[7]) + 0.10 * double(x[0]) - 0.13;
        feature_a[p] = float(u / (1.0 + std::abs(u)));
        feature_b[p] = float(v / (1.0 + std::abs(v)));
    }
    for (size_t p = 0; p < n; ++p) {
        const float* x = &input[p * 8];
        double d0 = double(x[3]) - double(x[7]);
        double d1 = double(x[1]) - double(x[6]);
        double z = 0.12 + 0.66 * double(x[0]) - 0.39 * double(x[1])
            + 0.31 * double(x[2]) * double(x[4]) - 0.27 * double(x[5])
            + 0.45 * double(feature_a[p]) - 0.26 * double(feature_b[p])
            + 0.13 * double(feature_a[p]) * double(feature_b[p])
            + 0.17 * d0 * d0 - 0.08 * d1 * d1;
        score[p] = float(0.5 + 0.5 * z / (1.0 + std::abs(z)));
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
        + (feature_a.capacity() + feature_b.capacity() + score.capacity()) * sizeof(float);
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
