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
    std::vector<T> x(n), w(n);
    std::vector<double> scores(batches);
    for (std::size_t i=0;i<n;i++) {
        x[i] = T(std::sin(double(i)*0.0017)*0.7 + double(int(i%31)-15)*0.003);
        w[i] = T(std::cos(double(i)*0.0009)*0.4 + double(int(i%19)-9)*0.002);
    }
    const auto start=clock::now();
    for (int b=0;b<batches;b++) {
        double sum=0;
        const double bias=(b-1)*0.0001;
        for (std::size_t i=0;i<n;i++) sum += double((x[i]+T(bias))*w[i]);
        scores[b]=sum;
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
    if(p=="float"||p=="auto") return run<float>(batches,n,"float");
    std::cerr << "precision must be auto, float, or double\n"; return 2;
}
