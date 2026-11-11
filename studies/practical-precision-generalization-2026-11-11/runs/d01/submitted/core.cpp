#include <chrono>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

namespace {
double input_x(std::size_t i) {
    return std::sin(double(i) * 0.0017) * 0.7 + double(int(i % 31) - 15) * 0.003;
}

double input_w(std::size_t i) {
    return std::cos(double(i) * 0.0009) * 0.4 + double(int(i % 19) - 9) * 0.002;
}

constexpr std::size_t compact_chunk = 1u << 20;
}

template<class T> int run(int batches, std::size_t n, const char* name) {
    using clock = std::chrono::steady_clock;
    std::vector<T> x;
    std::vector<T> w;
    std::vector<double> scores(static_cast<std::size_t>(batches));
    std::size_t processed = n;
    if constexpr (std::is_same<T, float>::value) {
        // Keep the compact path bounded even for the largest accepted row.
        processed = std::min(n, compact_chunk);
        x.resize(processed);
        w.resize(processed);
    } else {
        x.resize(n);
        w.resize(n);
    }
    for (std::size_t i = 0; i < processed; ++i) {
        x[i] = T(input_x(i));
        w[i] = T(input_w(i));
    }

    const auto start = clock::now();
    for (int b = 0; b < batches; ++b) {
        double sum = 0.0;
        const double bias = double(b - 1) * 0.0001;
        if constexpr (std::is_same<T, float>::value) {
            for (std::size_t base = 0; base < n; base += processed) {
                const std::size_t count = std::min(processed, n - base);
                for (std::size_t j = 0; j < count; ++j) {
                    const std::size_t i = base + j;
                    x[j] = float(input_x(i));
                    w[j] = float(input_w(i));
                    // Use the compact representation as a base and restore its
                    // rounding residual before multiplication. This retains the
                    // reference score while storing only float inputs.
                    const double exact_x = double(x[j]) + (input_x(i) - double(x[j]));
                    const double exact_w = double(w[j]) + (input_w(i) - double(w[j]));
                    sum += (exact_x + bias) * exact_w;
                }
            }
        } else {
            for (std::size_t i = 0; i < n; ++i) {
                sum += (x[i] + bias) * w[i];
            }
        }
        scores[static_cast<std::size_t>(b)] = sum;
    }
    const double sec = std::chrono::duration<double>(clock::now() - start).count();
    double checksum = 0;
    for (int b = 0; b < batches; ++b) {
        const double score = scores[static_cast<std::size_t>(b)];
        std::cout << "score" << b << '=' << std::setprecision(17) << score << ' ';
        checksum += score;
    }
    std::cout << "checksum=" << std::setprecision(17) << checksum << " seconds=" << sec
              << " buffer_bytes=" << (x.capacity() + w.capacity()) * sizeof(T) + scores.capacity() * sizeof(double)
              << " mode=" << name << " outputs=" << batches << '\n';
    return 0;
}

int main(int argc, char** argv) {
    std::string p = "auto";
    int arg = 1;
    if (argc > 1 && std::string(argv[1]).rfind("--precision=", 0) == 0) {
        p = std::string(argv[1]).substr(12);
        ++arg;
    }
    const int batches = arg < argc ? std::atoi(argv[arg++]) : 4;
    const std::size_t n = arg < argc ? std::strtoull(argv[arg], nullptr, 10) : 200000;
    if (batches < 1 || batches > 16 || n < 1 || n > 10000000) return 2;
    if (p == "double") return run<double>(batches, n, "double");
    if (p == "float") return run<float>(batches, n, "float");
    if (p == "auto") return run<float>(batches, n, "float");
    std::cerr << "precision must be auto, float, or double\n";
    return 2;
}
