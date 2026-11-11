#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

static double input_sample(std::uint64_t frame, int channel, std::uint64_t seed) {
  std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
                    (channel + 3) * 1442695040888963407ULL + seed;
  x ^= x >> 29;
  x *= 0x9e3779b97f4a7c15ULL;
  x ^= x >> 32;
  return (static_cast<int>(x % 2000001) - 1000000) * 0.000001;
}

int main(int argc, char** argv) {
  if (argc < 3 || argc > 4) return 2;
  const std::uint64_t frames = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
  const bool audit = argc == 4 && std::string(argv[3]) == "--audit";
  constexpr std::uint64_t input_rate = 44100;
  constexpr std::uint64_t output_rate = 48000;
  constexpr int channels = 2;
  if (!frames || frames > 500000 || (argc == 4 && !audit) ||
      (audit && frames > 65536)) return 2;

  // Count k with k*input_rate < (frames-1)*output_rate. Integer arithmetic
  // keeps the output-clock boundary exact, including at the final timestamp.
  const std::uint64_t count = frames > 1
      ? (((frames - 1) * output_rate + input_rate - 1) / input_rate)
      : 0;
  std::cout.precision(audit ? 17 : 9);
  std::cout << count << '\n';

  for (std::uint64_t k = 0; k < count; ++k) {
    const std::uint64_t position = k * input_rate;
    const std::uint64_t index = position / output_rate;
    const std::uint64_t remainder = position % output_rate;
    if (audit) {
      const double fraction = static_cast<double>(remainder) / output_rate;
      for (int c = 0; c < channels; ++c) {
        const double a = input_sample(index, c, seed);
        const double b = input_sample(index + 1, c, seed);
        std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
      }
    } else {
      // Float operands and arithmetic are sufficient for the 2e-6 public
      // sample tolerance. Exact integer coordinates avoid phase drift.
      const float fraction = static_cast<float>(remainder) /
                             static_cast<float>(output_rate);
      for (int c = 0; c < channels; ++c) {
        const float a = static_cast<float>(input_sample(index, c, seed));
        const float b = static_cast<float>(input_sample(index + 1, c, seed));
        std::cout << (a + fraction * (b - a)) << (c ? '\n' : ' ');
      }
    }
  }
}
