#include <cmath>
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

  std::vector<double> input(frames * channels);
  for (std::uint64_t i = 0; i < frames; ++i)
    for (int c = 0; c < channels; ++c)
      input[i * channels + c] = input_sample(i, c, seed);

  std::cout.precision(audit ? 17 : 9);
  if (audit) {
    std::uint64_t outputs = 0;
    for (std::uint64_t k = 0; k * input_rate < (frames - 1) * output_rate; ++k)
      ++outputs;
    std::cout << outputs << '\n';
    for (std::uint64_t k = 0; k < outputs; ++k) {
      const std::uint64_t position = k * input_rate;
      const std::uint64_t index = position / output_rate;
      const double fraction = static_cast<double>(position % output_rate) / output_rate;
      for (int c = 0; c < channels; ++c) {
        const double a = input[index * channels + c];
        const double b = input[(index + 1) * channels + c];
        std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
      }
    }
  } else {
    const float step = static_cast<float>(input_rate) / output_rate;
    float phase = 0;
    std::uint64_t outputs = 0;
    while (phase < static_cast<float>(frames - 1)) {
      ++outputs;
      phase += step;
    }
    std::cout << outputs << '\n';
    phase = 0;
    for (std::uint64_t k = 0; k < outputs; ++k) {
      const auto index = static_cast<std::uint64_t>(phase);
      const double fraction = phase - static_cast<float>(index);
      for (int c = 0; c < channels; ++c) {
        const double a = input[index * channels + c];
        const double b = input[(index + 1) * channels + c];
        std::cout << a + fraction * (b - a) << (c ? '\n' : ' ');
      }
      phase += step;
    }
  }
}
