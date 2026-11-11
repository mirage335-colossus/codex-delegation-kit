#include <cstdint>
#include <cstdlib>
#include <iostream>

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::uint64_t events = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
  constexpr unsigned categories = 8;
  constexpr double weight[categories] = {
      0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25};
  if (!events || events > 6000000) return 2;

  std::uint64_t count[categories];
  double score[categories];
  for (unsigned c = 0; c < categories; ++c) {
    const std::uint64_t prior = (1ULL << 53) + c * 4096 + seed % 31;

    // The category rule advances by 13 modulo 8, or 5 modulo 8.  Since
    // 5 is its own inverse modulo 8, indices for each class form one
    // arithmetic progression with stride 8.
    const std::uint64_t first =
        (5 * ((c + categories - seed % categories) % categories)) % categories;
    const std::uint64_t occurrences = first >= events
        ? 0
        : (events - 1 - first) / categories + 1;
    count[c] = prior + occurrences;

    // Intensities are 0.001 * (index + 1); sum that progression exactly
    // as an integer before applying the display-scale floating operations.
    const std::uint64_t sum_indices_plus_one = occurrences == 0
        ? 0
        : occurrences * (2 * (first + 1) + categories * (occurrences - 1)) / 2;
    score[c] = weight[c] * 0.001 * static_cast<double>(sum_indices_plus_one);
  }

  std::cout.precision(17);
  for (unsigned c = 0; c < categories; ++c)
    std::cout << count[c] << ' ' << score[c]
              << (c + 1 == categories ? '\n' : ' ');
}
