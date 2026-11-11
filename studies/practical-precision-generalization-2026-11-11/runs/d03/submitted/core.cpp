#include <cerrno>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>

namespace {
constexpr std::size_t kChannels = 8;
constexpr std::size_t kMaxSamples = 600000;

double sample(std::uint64_t i, int c) {
  std::uint64_t x = (i + 1) * 6364136223846793005ULL +
                    (c + 7) * 1442695040888963407ULL;
  x ^= x >> 29;
  x *= 0x9e3779b97f4a7c15ULL;
  x ^= x >> 32;
  return (static_cast<int>(x % 200001) - 100000) * 0.01;
}

bool parse_size(const char* text, std::size_t* value) {
  if (!text || !*text || *text == '-') return false;
  errno = 0;
  char* end = nullptr;
  const unsigned long long parsed = std::strtoull(text, &end, 10);
  if (errno || end == text || *end != '\0' ||
      parsed > static_cast<unsigned long long>(kMaxSamples)) {
    return false;
  }
  *value = static_cast<std::size_t>(parsed);
  return true;
}
}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  std::size_t n = 0;
  std::size_t w = 0;
  if (!parse_size(argv[1], &n) || !parse_size(argv[2], &w) || n == 0 ||
      w == 0 || w > n) {
    return 2;
  }

  // The generated stream is deterministic, so the outgoing item can be
  // regenerated instead of retaining a full batch or a window-sized ring.
  double window_sum[kChannels] = {};
  double output[kChannels] = {};
  for (std::size_t i = 0; i < n; ++i) {
    for (std::size_t c = 0; c < kChannels; ++c) {
      window_sum[c] += sample(i, static_cast<int>(c));
      if (i >= w) window_sum[c] -= sample(i - w, static_cast<int>(c));
      if (i + 1 >= w) output[c] += window_sum[c] / static_cast<double>(w);
    }
  }

  std::cout.precision(17);
  for (std::size_t c = 0; c < kChannels; ++c) {
    if (!std::isfinite(output[c])) return 3;
    std::cout << output[c] << (c + 1 == kChannels ? '\n' : ' ');
  }
  return 0;
}
