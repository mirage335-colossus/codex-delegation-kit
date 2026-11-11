#include <cmath>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <string_view>

static double force(std::uint64_t t) {
  std::uint64_t x = (t + 1) * 2862933555777941757ULL + 3037000493ULL;
  x ^= x >> 31;
  x *= 0x9e3779b97f4a7c15ULL;
  x ^= x >> 27;
  return (static_cast<int>(x % 200001) - 100000) * 0.00001;
}
static std::uint64_t hash(std::uint64_t x) {
  x ^= x >> 30;
  x *= 0xbf58476d1ce4e5b9ULL;
  x ^= x >> 27;
  x *= 0x94d049bb133111ebULL;
  x ^= x >> 31;
  return x;
}

static bool parse_u64(const char* text, std::uint64_t& value) {
  const std::string_view input(text);
  if (input.empty()) return false;
  const auto result = std::from_chars(input.data(), input.data() + input.size(), value);
  return result.ec == std::errc{} && result.ptr == input.data() + input.size();
}

int main(int argc, char** argv) {
  if (argc != 4) return 2;
  std::uint64_t trials, steps, seed;
  if (!parse_u64(argv[1], trials) || !parse_u64(argv[2], steps) ||
      !parse_u64(argv[3], seed) || trials < 1 || trials > 120000 ||
      steps < 1 || steps > 1024)
    return 2;

  constexpr double decay = 0.9999;
  double force_sum = 0;
  double bias_gain = 0;
  double decay_power = 1;
  for (std::uint64_t t = 0; t < steps; ++t) {
    force_sum = decay * force_sum + force(t);
    bias_gain = decay * bias_gain + 1.0;
    decay_power *= decay;
  }

  double mean = 0;
  double m2 = 0;
  for (std::uint64_t trial = 0; trial < trials; ++trial) {
    const auto bits = hash(seed + trial * 0x9e3779b97f4a7c15ULL);
    const double initial = (static_cast<int>(bits % 20001) - 10000) * 0.0001;
    const double bias = (static_cast<int>((bits >> 20) % 2001) - 1000) * 0.0000002;
    const double state = decay_power * initial + force_sum + bias_gain * bias;
    const double delta = state - mean;
    mean += delta / static_cast<double>(trial + 1);
    m2 += delta * (state - mean);
  }
  std::cout.precision(17);
  std::cout << mean << ' ' << m2 / static_cast<double>(trials) << '\n';
}
