#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
#if defined(__x86_64__) || defined(__i386__)
#include <immintrin.h>
#endif
static bool has_avx2(){
#if defined(__x86_64__) || defined(__i386__)
    __builtin_cpu_init(); return __builtin_cpu_supports("avx2");
#else
    return false;
#endif
}
#if defined(__x86_64__) || defined(__i386__)
__attribute__((target("avx2"))) static void kernel_avx2(const std::int16_t*in,float*out,std::size_t n){
    const __m256 scale=_mm256_set1_ps(0.75f/32768.0f),bias=_mm256_set1_ps(0.125f);
    std::size_t i=0;
    for(;i+8<=n;i+=8){
        __m128i small=_mm_loadu_si128(reinterpret_cast<const __m128i*>(in+i));
        __m256 values=_mm256_cvtepi32_ps(_mm256_cvtepi16_epi32(small));
        _mm256_storeu_ps(out+i,_mm256_add_ps(_mm256_mul_ps(values,scale),bias));
    }
    for(;i<n;i++)out[i]=(float(in[i])*(1.0f/32768.0f))*0.75f+0.125f;
}
#endif
static void kernel_portable(const std::int16_t*in,float*out,std::size_t n){
    for(std::size_t i=0;i<n;i++)out[i]=(float(in[i])*(1.0f/32768.0f))*0.75f+0.125f;
}
static int process(std::size_t n,bool deny){
    std::vector<std::int16_t> source(n);std::vector<float> output(n);
    for(std::size_t i=0;i<n;i++){const std::uint32_t h=std::uint32_t(i)*1664525u+1013904223u;source[i]=std::int16_t(int(h%60001u)-30000);}
    const bool use=has_avx2()&&!deny;const auto begin=std::chrono::steady_clock::now();
#if defined(__x86_64__) || defined(__i386__)
    if(use)kernel_avx2(source.data(),output.data(),n);else kernel_portable(source.data(),output.data(),n);
#else
    kernel_portable(source.data(),output.data(),n);
#endif
    const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    double sum=0,weighted=0;for(std::size_t i=0;i<n;i++){sum+=output[i];weighted+=double(output[i])*double(i%97+1);}
    std::cout<<std::setprecision(17)<<"checksum="<<sum<<" weighted="<<weighted<<" samples="<<n<<" seconds="<<sec
             <<" buffer_bytes="<<source.capacity()*sizeof(source[0])+output.capacity()*sizeof(output[0])
             <<" storage=signed16-normalized compute=fp32 accumulator=fp64 selected="<<(use?"avx2":"portable")
             <<" cpu_avx2="<<(has_avx2()?"true":"false")<<" gpu_backend=absent outputs="<<n<<'\n';return 0;
}
int main(int argc,char**argv){bool deny=false;std::size_t n=1000000;for(int i=1;i<argc;i++){std::string a=argv[i];if(a=="--deny-avx2")deny=true;else if(a.rfind("--",0)==0)return 2;else n=std::strtoull(a.c_str(),nullptr,10);}if(!n||n>10000000)return 2;return process(n,deny);}
