#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

static float reading(int slot, int channel, std::uint64_t seed, bool transient) {
  const float level = 0.125f * (channel + 1) + 0.03125f * (seed % 5);
  if (!transient) {
    const int phase = (slot % 5) - 2;
    return level + phase * 0.03125f;
  }
  const float peak = 10000000.0f + channel * 1024.0f + static_cast<float>(seed % 17);
  if (slot == 0) return peak;
  if (slot <= 128) return level;
  return -peak;
}

int main(int argc, char** argv) {
  if (argc != 4) return 2;
  const std::uint64_t blocks = std::strtoull(argv[1], nullptr, 10);
  const std::uint64_t seed = std::strtoull(argv[2], nullptr, 10);
  const std::string profile = argv[3];
  const bool transient = profile == "transient";
  constexpr int channels = 8;
  constexpr int records_per_block = 130;
  if (!blocks || (!transient && profile != "normal")) return 2;

  double total[channels] = {};
  double squares[channels] = {};
  for (std::uint64_t block = 0; block < blocks; ++block) {
    for (int slot = 0; slot < records_per_block; ++slot) {
      for (int c = 0; c < channels; ++c) {
        const float value = reading(slot, c, seed, transient);
        total[c] += value;
        squares[c] += static_cast<double>(value) * value;
      }
    }
  }

  std::cout.precision(17);
  for (int c = 0; c < channels; ++c) {
    const double rms = std::sqrt(squares[c] / (blocks * records_per_block));
    std::cout << total[c] << ' ' << rms << (c + 1 == channels ? '\n' : ' ');
  }
}
