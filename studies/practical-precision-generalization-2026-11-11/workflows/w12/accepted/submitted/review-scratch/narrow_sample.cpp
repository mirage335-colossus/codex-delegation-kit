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

static float input_sample_float(std::uint64_t frame, int channel, std::uint64_t seed) {
  std::uint64_t x = (frame + 1) * 6364136223846793005ULL +
                    (channel + 3) * 1442695040888963407ULL + seed;
  x ^= x >> 29;
  x *= 0x9e3779b97f4a7c15ULL;
  x ^= x >> 32;
  return (static_cast<int>(x % 2000001) - 1000000) * 0.000001f;
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

  // k is emitted exactly when k * input_rate is strictly before the last
  // input timestamp, so the number of outputs is ceil((frames-1)*out/in).
  const std::uint64_t span = (frames - 1) * output_rate;
  const std::uint64_t outputs = (span + input_rate - 1) / input_rate;

  std::cout.precision(audit ? 17 : 9);
  std::cout << outputs << '\n';
  for (std::uint64_t k = 0; k < outputs; ++k) {
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
      // The input range is bounded by +/-1. Each sample is quantized in
      // 1e-6 increments, so binary32 interpolation remains far inside the
      // 2e-6 output tolerance while avoiding unnecessary wide hot-loop math.
      const float fraction = static_cast<float>(remainder) / static_cast<float>(output_rate);
      for (int c = 0; c < channels; ++c) {
        const float a = input_sample_float(index, c, seed);
        const float b = input_sample_float(index + 1, c, seed);
        const float value = a + fraction * (b - a);
        std::cout << value << (c ? '\n' : ' ');
      }
    }
  }
}
