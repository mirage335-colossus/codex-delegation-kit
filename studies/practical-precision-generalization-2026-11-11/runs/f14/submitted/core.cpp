#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <cstdint>

int main(int argc, char** argv) {
  if (argc < 4 || argc > 5) return 2;
  const std::size_t n = std::strtoull(argv[1], nullptr, 10);
  const long double origin = std::strtold(argv[2], nullptr);
  const long double step = std::strtold(argv[3], nullptr);
  const bool minimum = argc == 5 && std::string(argv[4]) == "--minimum-precision";
  const bool ticks = argc == 5 && std::string(argv[4]) == "--ticks";
  if (!n) return 2;

  if (ticks) {
    const long long tick = std::strtoll(argv[3], nullptr, 10);
    // The sequence is periodic with period 1001. Aggregate integer moments
    // before converting to floating point, so neither a large frame origin
    // nor a large integral tick can corrupt the displacement or its square.
    long long remainder_sum = 0;
    long long remainder_square_sum = 0;
    const std::size_t remainder = n % 1001;
    for (std::size_t i = 0; i < remainder; ++i) {
      const long long k = static_cast<long long>((i * 17) % 1001) - 500;
      remainder_sum += k;
      remainder_square_sum += k * k;
    }
    const __int128 exact_sum = static_cast<__int128>(tick) * remainder_sum;
    const unsigned long long k_square_sum =
        static_cast<unsigned long long>(n / 1001) * 83583500ULL + remainder_square_sum;
    const unsigned __int128 abs_tick = tick < 0
        ? static_cast<unsigned __int128>(-static_cast<__int128>(tick))
        : static_cast<unsigned __int128>(tick);
    const unsigned __int128 tick_square = abs_tick * abs_tick;
    const unsigned __int128 low_product =
        static_cast<unsigned __int128>(static_cast<std::uint64_t>(tick_square)) * k_square_sum;
    const unsigned __int128 high_product =
        static_cast<unsigned __int128>(static_cast<std::uint64_t>(tick_square >> 64)) * k_square_sum;
    const unsigned __int128 middle = (low_product >> 64) +
        static_cast<std::uint64_t>(high_product);
    const std::uint64_t limb0 = static_cast<std::uint64_t>(low_product);
    const std::uint64_t limb1 = static_cast<std::uint64_t>(middle);
    const std::uint64_t limb2 = static_cast<std::uint64_t>(high_product >> 64) +
        static_cast<std::uint64_t>(middle >> 64);
    const long double mean = static_cast<long double>(exact_sum) / n;
    // Three limbs retain the full exact moment (the maximum supported batch
    // and signed 64-bit tick require fewer than 192 bits) until rendering.
    const long double exact_square_sum =
        std::ldexp(static_cast<long double>(limb2), 128) +
        std::ldexp(static_cast<long double>(limb1), 64) + limb0;
    const long double mean_square = exact_square_sum / n;
    std::cout.precision(17);
    std::cout << static_cast<double>(mean) << ' '
              << static_cast<double>(std::sqrt(mean_square)) << '\n';
    return 0;
  }

  long double sum = 0;
  long double square_sum = 0;
  // Displacements are defined in the selected frame. Keep them local rather
  // than forming origin + displacement, which can round away small offsets.
  // Streaming also avoids an O(n) temporary buffer in the large-batch path.
  (void)origin;
  (void)minimum;
  for (std::size_t i = 0; i < n; ++i) {
    const long double delta = step * (static_cast<int>((i * 17) % 1001) - 500);
    sum += delta;
    square_sum += delta * delta;
  }
  std::cout.precision(17);
  std::cout << static_cast<double>(sum / n) << ' '
            << std::sqrt(static_cast<double>(square_sum / n)) << '\n';
}
