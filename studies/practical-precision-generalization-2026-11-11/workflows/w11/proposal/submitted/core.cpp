#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

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

static int run_audit(int w,int h,int seed) {
    const size_t n=size_t(w)*size_t(h);
    double bins[32][3]={};
    size_t ids[8]={0,size_t(size_t(n>1?1:0)),n/7,n/3,n/2,(2*n)/3,size_t(size_t(n>1?n-2:0)),n-1};
    for(size_t i=0;i<n;++i){double q=calibration(double(measurement(i,seed)));int b=int(i%32);bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=q>=3.8?1.0:0.0;}
    double samples[8];for(int j=0;j<8;++j)samples[j]=calibration(double(measurement(ids[j],seed)));
    std::cout<<std::setprecision(13)<<"{\"storage_bytes\":0,\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int j=0;j<8;++j){if(j)std::cout<<',';std::cout<<samples[j];}std::cout<<"]}\n";
    return 0;
}

static int run_fast(int w,int h,int seed) {
    const size_t n=size_t(w)*size_t(h);
    // Calibration is smooth throughout [0, 1]. 8192 linear segments keep
    // interpolation error below the per-reading contract; only the narrow
    // decision boundary is sent through the exact function.
    static float table[kCurveSize];
    for(size_t j=0;j<kCurveSize;++j)table[j]=float(calibration(double(j)/double(kCurveSize-1)));
    double bins[32][3]={};
    size_t ids[8]={0,size_t(size_t(n>1?1:0)),n/7,n/3,n/2,(2*n)/3,size_t(size_t(n>1?n-2:0)),n-1};
    for(size_t i=0;i<n;++i){
        const float x=measurement(i,seed);
        const float pos=x*float(kCurveSize-1);
        const size_t lo=std::min(size_t(pos),kCurveSize-2);
        const float frac=pos-float(lo);
        float q=table[lo]+(table[lo+1]-table[lo])*frac;
        if(std::abs(double(q)-3.8)<0.001)q=float(calibration(double(x)));
        const int b=int(i%32);
        bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=q>=3.8?1.0:0.0;
    }
    float samples[8];
    for(int j=0;j<8;++j){
        const float x=measurement(ids[j],seed);
        const float pos=x*float(kCurveSize-1);
        const size_t lo=std::min(size_t(pos),kCurveSize-2);
        const float frac=pos-float(lo);
        float q=table[lo]+(table[lo+1]-table[lo])*frac;
        if(std::abs(double(q)-3.8)<0.001)q=float(calibration(double(x)));
        samples[j]=q;
    }
    std::cout<<std::setprecision(13)<<"{\"storage_bytes\":"<<kCurveSize*sizeof(float)<<",\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int j=0;j<8;++j){if(j)std::cout<<',';std::cout<<samples[j];}std::cout<<"]}\n";
    return 0;
}

int main(int argc,char**argv){
    int w=argc>1?std::atoi(argv[1]):4096,h=argc>2?std::atoi(argv[2]):2048,seed=argc>3?std::atoi(argv[3]):13;
    bool audit=argc>4&&std::strcmp(argv[4],"--audit")==0;
    if(w<1||h<1||w>8192||h>8192)return 2;
    return audit?run_audit(w,h,seed):run_fast(w,h,seed);
}
