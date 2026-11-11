#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <string>

using WideUnsigned = unsigned __int128;
using WideSigned = __int128;

static void add_square_times_count(uint32_t total[8], WideUnsigned value,
                                   uint32_t count) {
  uint32_t limbs[4] = {};
  for (unsigned i = 0; i < 4; ++i) {
    limbs[i] = static_cast<uint32_t>(value);
    value >>= 32;
  }
  uint32_t square[8] = {};
  for (unsigned i = 0; i < 4; ++i) {
    uint64_t carry = 0;
    for (unsigned j = 0; j < 4; ++j) {
      const uint64_t product = static_cast<uint64_t>(limbs[i]) * limbs[j] +
                               square[i + j] + carry;
      square[i + j] = static_cast<uint32_t>(product);
      carry = product >> 32;
    }
    unsigned at = i + 4;
    while (carry && at < 8) {
      const uint64_t next = static_cast<uint64_t>(square[at]) + carry;
      square[at++] = static_cast<uint32_t>(next);
      carry = next >> 32;
    }
  }
  uint64_t carry = 0;
  for (unsigned i = 0; i < 8; ++i) {
    const uint64_t product = static_cast<uint64_t>(square[i]) * count +
                             total[i] + carry;
    total[i] = static_cast<uint32_t>(product);
    carry = product >> 32;
  }
}

static long double as_long_double(const uint32_t limbs[8]) {
  long double value = 0;
  for (int i = 7; i >= 0; --i)
    value = std::ldexp(value, 32) + limbs[i];
  return value;
}

int main(int argc, char** argv) {
  if (argc < 4 || argc > 5) return 2;
  const std::size_t n = std::strtoull(argv[1], nullptr, 10);
  const long double origin = std::strtold(argv[2], nullptr);
  const long double step = std::strtold(argv[3], nullptr);
  const bool minimum = argc == 5 && std::string(argv[4]) == "--minimum-precision";
  const bool ticks = argc == 5 && std::string(argv[4]) == "--ticks";
  if (!n || n > 3200000) return 2;

  if (ticks) {
    const auto base = std::strtoull(argv[2], nullptr, 10);
    const long long tick = std::strtoll(argv[3], nullptr, 10);
    (void)base;
    WideSigned sum = 0;
    uint32_t square_sum[8] = {};
    std::size_t counts[1001];
    for (std::size_t k = 0; k < 1001; ++k) counts[k] = n / 1001;
    for (std::size_t i = 0; i < n % 1001; ++i)
      ++counts[(i * 17) % 1001];
    for (std::size_t k = 0; k < 1001; ++k) {
      const long long centered = static_cast<long long>(k) - 500;
      const WideSigned signed_delta = static_cast<WideSigned>(centered) * tick;
      const WideUnsigned delta = signed_delta < 0
          ? static_cast<WideUnsigned>(-signed_delta)
          : static_cast<WideUnsigned>(signed_delta);
      const std::size_t count = counts[k];
      sum += signed_delta * count;
      add_square_times_count(square_sum, delta, static_cast<uint32_t>(count));
    }
    std::cout.precision(17);
    const long double mean = static_cast<long double>(sum) / n;
    const long double mean_square = as_long_double(square_sum) / n;
    std::cout << static_cast<double>(mean) << ' '
              << static_cast<double>(std::sqrt(mean_square)) << '\n';
    return 0;
  }

  long double sum = 0;
  long double square_sum = 0;
  (void)origin;
  (void)minimum;
  for (std::size_t i = 0; i < n; ++i) {
    const long double delta = step * (static_cast<int>((i * 17) % 1001) - 500);
    sum += delta;
    square_sum += delta * delta;
  }
  std::cout.precision(17);
  std::cout << static_cast<double>(sum / n) << ' '
            << std::sqrt(static_cast<double>(square_sum / n)) << '\n';
}
