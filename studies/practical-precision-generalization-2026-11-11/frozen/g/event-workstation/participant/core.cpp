#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>

static unsigned category(std::uint64_t index, std::uint64_t seed) {
  return static_cast<unsigned>((index * 13 + seed) % 8);
}
static float intensity(std::uint64_t index) {
  return static_cast<float>((index + 1) * 0.001f);
}
static constexpr double weight[8] = {0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25};

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::uint64_t events = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
  constexpr unsigned categories = 8;
  if (!events || events > 6000000) return 2;

  // Retain the event intensities for the risk-score pass.
  std::vector<double> intensities(events);
  for (std::uint64_t i = 0; i < events; ++i)
    intensities[i] = intensity(i);

  // Imported counts and new event totals share one floating-point counter.
  double count[categories];
  double score[categories] = {};
  for (unsigned c = 0; c < categories; ++c) {
    const std::uint64_t prior = (1ULL << 53) + c * 4096 + seed % 31;
    count[c] = static_cast<double>(prior);
  }
  for (std::uint64_t i = 0; i < events; ++i) {
    const unsigned c = category(i, seed);
    count[c] += 1.0;
    score[c] += intensities[i] * weight[c];
  }

  std::cout.precision(17);
  for (unsigned c = 0; c < categories; ++c)
    std::cout << static_cast<std::uint64_t>(count[c]) << ' ' << score[c]
              << (c + 1 == categories ? '\n' : ' ');
}
