#include <cmath>
#include <charconv>
#include <cstdint>
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

// Neumaier summation retains small readings when they follow large transient
// pulses, while requiring only one accumulator and correction per channel.
static void add_compensated(double value, double& sum, double& correction) {
  const double next = sum + value;
  if (std::abs(sum) >= std::abs(value))
    correction += (sum - next) + value;
  else
    correction += (value - next) + sum;
  sum = next;
}

static bool parse_u64(const char* text, std::uint64_t& value) {
  const char* end = text;
  while (*end) ++end;
  const auto result = std::from_chars(text, end, value, 10);
  return result.ec == std::errc{} && result.ptr == end;
}

int main(int argc, char** argv) {
  if (argc != 4) return 2;
  std::uint64_t blocks = 0;
  std::uint64_t seed = 0;
  if (!parse_u64(argv[1], blocks) || blocks < 1 || blocks > 12000 ||
      !parse_u64(argv[2], seed)) return 2;
  const std::string profile = argv[3];
  const bool transient = profile == "transient";
  constexpr int channels = 8;
  constexpr int records_per_block = 130;
  if (!transient && profile != "normal") return 2;

  double total[channels] = {};
  double total_correction[channels] = {};
  double squares[channels] = {};
  double squares_correction[channels] = {};
  for (std::uint64_t b = 0; b < blocks; ++b)
    for (int slot = 0; slot < records_per_block; ++slot)
      for (int c = 0; c < channels; ++c) {
        const double value = reading(slot, c, seed, transient);
        add_compensated(value, total[c], total_correction[c]);
        add_compensated(value * value, squares[c], squares_correction[c]);
      }

  const double record_count = static_cast<double>(blocks) * records_per_block;
  std::cout.precision(17);
  for (int c = 0; c < channels; ++c) {
    const double integrated = total[c] + total_correction[c];
    const double rms = std::sqrt((squares[c] + squares_correction[c]) / record_count);
    std::cout << integrated << ' ' << rms << (c + 1 == channels ? '\n' : ' ');
  }
}
