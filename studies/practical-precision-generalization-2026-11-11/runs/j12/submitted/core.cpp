#include <cstdint>
#include <cstdlib>
#include <iostream>

static constexpr float weight[8] = {
    0.5f, 0.75f, 1.0f, 1.25f, 1.5f, 1.75f, 2.0f, 2.25f};

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::uint64_t events = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
  constexpr unsigned categories = 8;
  if (!events || events > 6000000) return 2;

  std::uint64_t count[categories];
  float score[categories];
  const unsigned seed_class = static_cast<unsigned>(seed % categories);
  for (unsigned c = 0; c < categories; ++c) {
    // 13 is 5 modulo 8, and 5 is its own inverse modulo 8. Find
    // the first event index belonging to this category.
    const std::uint64_t first =
        (((c + categories - seed_class) % categories) * 5) % categories;
    const std::uint64_t n = first < events ? (events - 1 - first) / 8 + 1 : 0;
    const std::uint64_t prior = (1ULL << 53) + c * 4096 + seed % 31;
    count[c] = prior + n;

    // The category's event indices are first, first+8, ... . Sum their
    // (index+1) intensities exactly as an integer progression, then apply
    // the published score scale and weight in float. The score tolerance
    // is much wider than float rounding error, while exact counts stay integer.
    const std::uint64_t sum_indices_plus_one =
        n ? n * (2 * (first + 1) + 8 * (n - 1)) / 2 : 0;
    score[c] = weight[c] * 0.001f * static_cast<float>(sum_indices_plus_one);
  }

  std::cout.precision(17);
  for (unsigned c = 0; c < categories; ++c)
    std::cout << count[c] << ' ' << score[c]
              << (c + 1 == categories ? '\n' : ' ');
}
