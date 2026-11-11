#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
  if (argc < 4 || argc > 5) return 2;
  const std::size_t n = std::strtoull(argv[1], nullptr, 10);
  const long double origin = std::strtold(argv[2], nullptr);
  const long double step = std::strtold(argv[3], nullptr);
  const bool minimum = argc == 5 && std::string(argv[4]) == "--minimum-precision";
  const bool ticks = argc == 5 && std::string(argv[4]) == "--ticks";
  if (!n) return 2;

  if (ticks) {
    const auto base = std::strtoull(argv[2], nullptr, 10);
    const long long tick = std::strtoll(argv[3], nullptr, 10);
    long long sum = 0;
    long double square_sum = 0;
    for (std::size_t i = 0; i < n; ++i) {
      const long long displacement =
          (static_cast<long long>((i * 17) % 1001) - 500) * tick;
      const __int128 coordinate = static_cast<__int128>(base) + displacement;
      const long long delta = static_cast<long long>(
          coordinate - static_cast<__int128>(base));
      sum += delta;
      square_sum += static_cast<long double>(delta) * delta;
    }
    std::cout.precision(17);
    std::cout << static_cast<double>(sum) / n << ' '
              << std::sqrt(static_cast<double>(square_sum / n)) << '\n';
    return 0;
  }

  long double sum = 0;
  long double square_sum = 0;
  if (minimum) {
    for (std::size_t i = 0; i < n; ++i) {
      const long double delta = step * (static_cast<int>((i * 17) % 1001) - 500);
      sum += delta;
      square_sum += delta * delta;
    }
  } else {
    std::vector<long double> absolute(n);
    for (std::size_t i = 0; i < n; ++i) {
      const int k = static_cast<int>((i * 17) % 1001) - 500;
      absolute[i] = origin + step * k;
    }
    for (long double value : absolute) {
      const long double delta = value - origin;
      sum += delta;
      square_sum += delta * delta;
    }
  }
  std::cout.precision(17);
  std::cout << static_cast<double>(sum / n) << ' '
            << std::sqrt(static_cast<double>(square_sum / n)) << '\n';
}
