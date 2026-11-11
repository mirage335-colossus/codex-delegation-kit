#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>

#ifndef VALUE
#define VALUE float
#endif

int main(int argc, char **argv) {
  const int channels = argc > 1 ? std::atoi(argv[1]) : 4;
  const int samples = argc > 2 ? std::atoi(argv[2]) : 8192;
  const int tap_count = argc > 3 ? std::atoi(argv[3]) : 63;
  const int seed = argc > 4 ? std::atoi(argv[4]) : 9;
  if (channels < 1 || channels > 32 || samples < 128 || samples > 500000 ||
      tap_count < 3 || tap_count > 255 || !(tap_count & 1)) {
    return 2;
  }

  std::vector<VALUE> input(static_cast<size_t>(channels) * samples);
  std::vector<VALUE> coefficients(tap_count);
  std::vector<VALUE> output(static_cast<size_t>(channels) * samples);

  double coefficient_l1_norm = 0.0;
  for (int k = 0; k < tap_count; ++k) {
    const double z = (k - (tap_count - 1) * 0.5) / (tap_count * 0.5);
    const double value = (0.5 + 0.5 * std::cos(3.141592653589793 * z)) *
                         std::cos(0.23 * k);
    coefficients[k] = static_cast<VALUE>(value);
    coefficient_l1_norm += std::abs(value);
  }
  for (auto &coefficient : coefficients) {
    coefficient = static_cast<VALUE>(static_cast<double>(coefficient) /
                                     coefficient_l1_norm);
  }

  for (int channel = 0; channel < channels; ++channel) {
    for (int i = 0; i < samples; ++i) {
      const double value =
          std::sin((i + seed * 7 + channel * 13) * 0.017) +
          0.35 * std::cos((i * 3 + seed + channel * 5) * 0.009);
      input[static_cast<size_t>(channel) * samples + i] =
          static_cast<VALUE>(value);
    }
  }

  const int radius = tap_count / 2;
  for (int channel = 0; channel < channels; ++channel) {
    const size_t channel_offset = static_cast<size_t>(channel) * samples;
    for (int i = 0; i < samples; ++i) {
      double accumulator = 0.0;
      for (int k = 0; k < tap_count; ++k) {
        const int source = i + k - radius;
        if (source >= 0 && source < samples) {
          accumulator += static_cast<double>(input[channel_offset + source]) *
                         static_cast<double>(coefficients[k]);
        }
      }
      output[channel_offset + i] = static_cast<VALUE>(accumulator);
    }
  }

  double checksum_sum[16] = {};
  double checksum_square[16] = {};
  for (size_t i = 0; i < output.size(); ++i) {
    const double value = static_cast<double>(output[i]);
    checksum_sum[i % 16] += value;
    checksum_square[i % 16] += value * value;
  }

  const size_t ids[6] = {
      0,
      static_cast<size_t>(samples) / 11,
      static_cast<size_t>(samples) / 3,
      static_cast<size_t>(samples) / 2,
      static_cast<size_t>(samples - 1),
      (static_cast<size_t>(channels) - 1) * samples + samples / 4};
  std::cout << std::setprecision(10)
            << "{\"storage_bytes\":"
            << (input.size() + coefficients.size() + output.size()) *
                   sizeof(VALUE)
            << ",\"checksums\":[";
  for (int bucket = 0; bucket < 16; ++bucket) {
    if (bucket) std::cout << ",";
    std::cout << "[" << checksum_sum[bucket] << ","
              << checksum_square[bucket] << "]";
  }
  std::cout << "],\"samples\":[";
  for (int i = 0; i < 6; ++i) {
    if (i) std::cout << ",";
    std::cout << static_cast<double>(output[ids[i]]);
  }
  std::cout << "]}\n";
}
