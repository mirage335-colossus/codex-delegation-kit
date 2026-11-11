#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#if defined(__x86_64__) || defined(__i386__)
#include <immintrin.h>
#define REVIEW_WORKER_X86 1
#else
#define REVIEW_WORKER_X86 0
#endif

static bool has_avx2() {
#if REVIEW_WORKER_X86 && (defined(__GNUC__) || defined(__clang__))
    __builtin_cpu_init();
    return __builtin_cpu_supports("avx2");
#else
    return false;
#endif
}

struct Totals {
    double sum = 0.0;
    double weighted = 0.0;
};

static float transform(std::int16_t sample) {
    const float normalized = static_cast<float>(sample) * (1.0f / 32768.0f);
    return normalized * 0.75f + 0.125f;
}

static Totals process_portable(const std::vector<std::int16_t>& source) {
    Totals totals;
    for (std::size_t i = 0; i < source.size(); ++i) {
        const double value = static_cast<double>(transform(source[i]));
        totals.sum += value;
        totals.weighted += value * static_cast<double>(i % 97 + 1);
    }
    return totals;
}

#if REVIEW_WORKER_X86 && (defined(__GNUC__) || defined(__clang__))
__attribute__((target("avx2")))
static Totals process_avx2(const std::vector<std::int16_t>& source) {
    Totals totals;
    const __m256 scale = _mm256_set1_ps(1.0f / 32768.0f);
    const __m256 gain = _mm256_set1_ps(0.75f);
    const __m256 bias = _mm256_set1_ps(0.125f);
    alignas(32) float values[8];
    std::size_t i = 0;
    for (; i + 8 <= source.size(); i += 8) {
        const __m128i packed = _mm_loadu_si128(
            reinterpret_cast<const __m128i*>(source.data() + i));
        const __m256i ints = _mm256_cvtepi16_epi32(packed);
        const __m256 normalized = _mm256_mul_ps(_mm256_cvtepi32_ps(ints), scale);
        const __m256 result = _mm256_add_ps(_mm256_mul_ps(normalized, gain), bias);
        _mm256_store_ps(values, result);
        for (unsigned lane = 0; lane < 8; ++lane) {
            const double value = static_cast<double>(values[lane]);
            const std::size_t index = i + lane;
            totals.sum += value;
            totals.weighted += value * static_cast<double>(index % 97 + 1);
        }
    }
    for (; i < source.size(); ++i) {
        const double value = static_cast<double>(transform(source[i]));
        totals.sum += value;
        totals.weighted += value * static_cast<double>(i % 97 + 1);
    }
    return totals;
}
#endif

int main(int argc, char** argv) {
    bool deny_avx2 = false;
    std::size_t n = 1000000;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--deny-avx2") {
            deny_avx2 = true;
        } else if (arg.rfind("--", 0) == 0) {
            std::cerr << "unknown option: " << arg << '\n';
            return 2;
        } else {
            char* end = nullptr;
            const unsigned long long parsed = std::strtoull(arg.c_str(), &end, 10);
            if (end == arg.c_str() || *end != '\0') {
                std::cerr << "invalid sample count: " << arg << '\n';
                return 2;
            }
            n = static_cast<std::size_t>(parsed);
        }
    }
    if (n < 1 || n > 10000000) {
        std::cerr << "sample count must be in [1, 10000000]\n";
        return 2;
    }

    std::vector<std::int16_t> source(n);
    for (std::size_t i = 0; i < n; ++i) {
        const std::uint32_t h = std::uint32_t(i) * 1664525u + 1013904223u;
        source[i] = static_cast<std::int16_t>(static_cast<int>(h % 60001u) - 30000);
    }

    const bool cpu_avx2 = has_avx2();
    const bool use_avx2 = cpu_avx2 && !deny_avx2;
    const auto begin = std::chrono::steady_clock::now();
    Totals totals;
#if REVIEW_WORKER_X86 && (defined(__GNUC__) || defined(__clang__))
    if (use_avx2) {
        totals = process_avx2(source);
    } else {
        totals = process_portable(source);
    }
#else
    (void)use_avx2;
    totals = process_portable(source);
#endif
    const double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - begin).count();

    const std::size_t buffer_bytes = source.capacity() * sizeof(source[0]);
    std::cout << std::setprecision(17)
              << "checksum=" << totals.sum << " weighted=" << totals.weighted
              << " samples=" << n << " seconds=" << seconds
              << " buffer_bytes=" << buffer_bytes
              << " storage=int16 compute=fp32 accumulator=fp64"
              << " selected=" << (use_avx2 ? "avx2" : "portable")
              << " cpu_avx2=" << (cpu_avx2 ? "true" : "false")
              << " gpu_backend=absent outputs=" << n << '\n';
    return 0;
}
