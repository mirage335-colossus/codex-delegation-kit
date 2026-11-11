#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

using Calc = double;
static constexpr size_t kCurveSize = 8193;

static float measurement(size_t i,int seed) {
    if(i%65536==0)return 0.0f;
    if(i%65536==1)return 1.0f;
    uint32_t a=uint32_t(i*1664525u+uint32_t(seed)*1013904223u);
    a^=a>>16;a*=2246822519u;a^=a>>13;a*=3266489917u;a^=a>>16;
    const uint32_t code=uint32_t(256u+(a%65280u));
    const float fraction=float((a>>16)&0xffffu)/65536.0f;
    const float raw=(float(code)+fraction)/65535.0f;
    return std::min(1.0f,raw);
}
static double calibration(double x) {
    return -std::log1p(-0.97*x)/0.85+0.20*std::log1p(0.30*x)+0.03+0.02*x*x;
}

template<class T>
static int run_direct(int w,int h,int seed,bool audit) {
    const size_t n=size_t(w)*size_t(h);
    std::vector<T> output(n);
    size_t lookup_bytes=0;
    if (audit) {
        for(size_t i=0;i<n;++i)output[i]=T(calibration(double(measurement(i,seed))));
    } else {
        // Measurements are floats in [0,1].  A dense uniform table keeps the
        // expensive logarithms out of the per-reading production loop; linear
        // interpolation is far more accurate than the normal-mode tolerance.
        static const std::vector<float> table=[] {
            constexpr size_t intervals=65536;
            std::vector<float> values(intervals+1);
            for(size_t j=0;j<=intervals;++j)
                values[j]=float(calibration(double(j)/double(intervals)));
            return values;
        }();
        lookup_bytes=table.capacity()*sizeof(float);
        constexpr float scale=65536.0f;
        for(size_t i=0;i<n;++i) {
            const float position=measurement(i,seed)*scale;
            const size_t index=std::min(size_t(position),size_t(65535));
            const float fraction=position-float(index);
            output[i]=T(table[index]+(table[index+1]-table[index])*fraction);
        }
    }
    T bins[32][3]={};
    for(size_t i=0;i<n;++i){T q=output[i];int b=int(i%32);bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=q>=3.8?1.0:0.0;}
    size_t ids[8]={0,size_t(size_t(n>1?1:0)),n/7,n/3,n/2,(2*n)/3,size_t(size_t(n>1?n-2:0)),n-1};
    size_t bytes=output.capacity()*sizeof(T)+lookup_bytes;
    std::cout<<std::setprecision(13)<<"{\"storage_bytes\":"<<bytes<<",\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int j=0;j<8;++j){if(j)std::cout<<',';std::cout<<double(output[ids[j]]);}std::cout<<"]}\n";
    return 0;
}

int main(int argc,char**argv){
    int w=argc>1?std::atoi(argv[1]):4096,h=argc>2?std::atoi(argv[2]):2048,seed=argc>3?std::atoi(argv[3]):13;
    bool audit=argc>4&&std::strcmp(argv[4],"--audit")==0;
    if(w<1||h<1||w>8192||h>8192)return 2;
    return audit ? run_direct<double>(w,h,seed,true)
                 : run_direct<float>(w,h,seed,false);
}
