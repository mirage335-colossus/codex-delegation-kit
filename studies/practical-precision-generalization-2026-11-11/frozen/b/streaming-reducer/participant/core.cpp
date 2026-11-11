#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <vector>

static double sample(std::uint64_t i, int c) {
  std::uint64_t x = (i + 1) * 6364136223846793005ULL + (c + 7) * 1442695040888963407ULL;
  x ^= x >> 29; x *= 0x9e3779b97f4a7c15ULL; x ^= x >> 32;
  return (static_cast<int>(x % 200001) - 100000) * 0.01;
}
int main(int argc, char** argv) {
  if (argc != 3) return 2;
  const std::size_t n = std::strtoull(argv[1], nullptr, 10);
  const std::size_t w = std::strtoull(argv[2], nullptr, 10);
  constexpr int channels = 8;
  if (!n || !w || w > n) return 2;
  std::vector<double> data(n * channels);
  for (std::size_t i=0; i<n; ++i) for (int c=0; c<channels; ++c) data[i*channels+c]=sample(i,c);
  double out[channels] = {};
  for (std::size_t i=0; i+w<=n; ++i)
    for (int c=0; c<channels; ++c) {
      double s=0; for (std::size_t j=0; j<w; ++j) s += data[(i+j)*channels+c];
      out[c] += s / static_cast<double>(w);
    }
  std::cout.precision(17);
  for (int c=0;c<channels;++c) std::cout << out[c] << (c+1==channels?'\n':' ');
}
