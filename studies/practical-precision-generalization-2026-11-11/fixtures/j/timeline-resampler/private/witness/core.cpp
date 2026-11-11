#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

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
  if (!frames || frames > 500000 || (argc == 4 && !audit) || (audit && frames > 65536)) return 2;

  std::vector<float> compact;
  std::vector<double> reference;
  if (audit) {
    reference.resize(frames * channels);
    for (std::uint64_t i = 0; i < frames; ++i)
      for (int c = 0; c < channels; ++c)
        reference[i * channels + c] = input_sample(i, c, seed);
  } else {
    compact.resize(frames * channels);
    for (std::uint64_t i = 0; i < frames; ++i)
      for (int c = 0; c < channels; ++c)
        compact[i * channels + c] = static_cast<float>(input_sample(i, c, seed));
  }

  const std::uint64_t limit = (frames - 1) * output_rate;
  const std::uint64_t outputs = frames > 1 ? (limit + input_rate - 1) / input_rate : 0;
  std::cout.precision(audit ? 17 : 9);
  std::cout << outputs << '\n';
  for (std::uint64_t k = 0; k < outputs; ++k) {
    const std::uint64_t position = k * input_rate;
    const std::uint64_t index = position / output_rate;
    if (audit) {
      const double fraction = static_cast<double>(position % output_rate) / output_rate;
      for (int c = 0; c < channels; ++c) {
        const double a = reference[index * channels + c];
        const double b = reference[(index + 1) * channels + c];
        std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
      }
    } else {
      const float fraction = static_cast<float>(position % output_rate) / output_rate;
      for (int c = 0; c < channels; ++c) {
        const float a = compact[index * channels + c];
        const float b = compact[(index + 1) * channels + c];
        const float output = a + fraction * (b - a);
        std::cout << output << (c ? '\n' : ' ');
      }
    }
  }
}
