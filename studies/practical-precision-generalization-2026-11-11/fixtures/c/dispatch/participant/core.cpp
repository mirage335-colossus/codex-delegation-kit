#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
static bool has_avx2(){
#if defined(__x86_64__) || defined(__i386__)
    __builtin_cpu_init(); return __builtin_cpu_supports("avx2");
#else
    return false;
#endif
}
template<class T> int process(std::size_t n,bool deny){
    std::vector<std::int16_t> source(n);
    std::vector<T> widened(n), output(n);
    for(std::size_t i=0;i<n;i++){
        const std::uint32_t h=std::uint32_t(i)*1664525u+1013904223u;
        source[i]=std::int16_t(int(h%60001u)-30000);
        widened[i]=T(float(source[i])*(1.0f/32768.0f));
    }
    const bool avx=has_avx2()&&!deny; (void)avx;
    const auto begin=std::chrono::steady_clock::now();
    for(std::size_t i=0;i<n;i++) output[i]=widened[i]*T(0.75f)+T(0.125f);
    const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    double sum=0,weighted=0;
    for(std::size_t i=0;i<n;i++){sum+=double(output[i]);weighted+=double(output[i])*double(i%97+1);}
    std::cout<<std::setprecision(17)<<"checksum="<<sum<<" weighted="<<weighted<<" samples="<<n
             <<" seconds="<<sec<<" buffer_bytes="<<(source.capacity()*sizeof(source[0])+(widened.capacity()+output.capacity())*sizeof(T))
             <<" storage=fp32-widened compute=fp32 accumulator=fp64 selected=portable cpu_avx2="<<(has_avx2()?"true":"false")
             <<" gpu_backend=absent outputs="<<n<<'\n';
    return 0;
}
int main(int argc,char**argv){
    bool deny=false; std::size_t n=1000000;
    for(int i=1;i<argc;i++){
        std::string a=argv[i]; if(a=="--deny-avx2") deny=true;
        else if(a.rfind("--",0)==0){std::cerr<<"unknown option: "<<a<<'\n';return 2;}
        else n=std::strtoull(a.c_str(),nullptr,10);
    }
    if(n<1||n>10000000)return 2;
    return process<float>(n,deny);
}
