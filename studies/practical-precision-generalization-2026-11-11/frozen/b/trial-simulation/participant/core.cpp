#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>

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

int main(int argc, char** argv) {
  if (argc != 4) return 2;
  const std::uint64_t trials = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t steps = std::strtoull(argv[2], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[3], nullptr, 10);
  if (!trials || !steps) return 2;

  constexpr double decay = 0.9999;
  double mean = 0;
  double m2 = 0;
  for (std::uint64_t trial = 0; trial < trials; ++trial) {
    const auto bits = hash(seed + trial * 0x9e3779b97f4a7c15ULL);
    double state = (static_cast<int>(bits % 20001) - 10000) * 0.0001;
    const double bias = (static_cast<int>((bits >> 20) % 2001) - 1000) * 0.0000002;
    for (std::uint64_t t = 0; t < steps; ++t)
      state = decay * state + force(t) + bias;
    const double delta = state - mean;
    mean += delta / static_cast<double>(trial + 1);
    m2 += delta * (state - mean);
  }
  std::cout.precision(17);
  std::cout << mean << ' ' << m2 / static_cast<double>(trials) << '\n';
}
