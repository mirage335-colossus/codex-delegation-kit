#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

template<class T> int run(int batches, std::size_t n, const char* name) {
    using clock = std::chrono::steady_clock;
    constexpr std::size_t buffer_budget = 64u * 1024u * 1024u;
    std::vector<double> scores(batches, 0.0);
    const std::size_t fixed_bytes = scores.capacity()*sizeof(double);
    const std::size_t chunk_size = std::min(n, (buffer_budget-fixed_bytes)/(2*sizeof(T)));
    std::vector<T> x(chunk_size), w(chunk_size);
    const auto start=clock::now();
    for (std::size_t base=0;base<n;base+=chunk_size) {
        const std::size_t count=std::min(chunk_size,n-base);
        for (std::size_t j=0;j<count;j++) {
            const std::size_t i=base+j;
            x[j] = T(std::sin(double(i)*0.0017)*0.7 + double(int(i%31)-15)*0.003);
            w[j] = T(std::cos(double(i)*0.0009)*0.4 + double(int(i%19)-9)*0.002);
        }
        for (int b=0;b<batches;b++) {
            const T bias=T((b-1)*0.0001);
            double sum=scores[b];
            for (std::size_t j=0;j<count;j++) sum += double((x[j]+bias)*w[j]);
            scores[b]=sum;
        }
    }
    const double sec=std::chrono::duration<double>(clock::now()-start).count();
    double checksum=0;
    for (int b=0;b<batches;b++) { std::cout << "score" << b << '=' << std::setprecision(17) << scores[b] << ' '; checksum+=scores[b]; }
    std::cout << "checksum=" << std::setprecision(17) << checksum << " seconds=" << sec
              << " buffer_bytes=" << (x.capacity()+w.capacity())*sizeof(T)+scores.capacity()*sizeof(double)
              << " mode=" << name << " outputs=" << batches << '\n';
    return 0;
}
int main(int argc,char**argv) {
    std::string p="auto"; int arg=1;
    if(argc>1 && std::string(argv[1]).rfind("--precision=",0)==0) { p=std::string(argv[1]).substr(12); arg++; }
    int batches=arg<argc?std::atoi(argv[arg++]):4; std::size_t n=arg<argc?std::strtoull(argv[arg],nullptr,10):200000;
    if(batches<1||batches>16||n<1||n>10000000) return 2;
    if(p=="double") return run<double>(batches,n,"double");
    if(p=="float") return run<float>(batches,n,"float");
    if(p=="auto") return run<float>(batches,n,"float");
    std::cerr << "precision must be auto, float, or double\n"; return 2;
}
