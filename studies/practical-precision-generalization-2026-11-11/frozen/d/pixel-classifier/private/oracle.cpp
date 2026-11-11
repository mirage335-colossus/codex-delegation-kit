#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>

static float sensor_value(size_t pixel, int channel, int seed) {
    uint32_t v = uint32_t(pixel * 747796405u + uint32_t(channel) * 2891336453u + uint32_t(seed) * 277803737u);
    v = ((v >> ((v >> 28) + 4)) ^ v) * 277803737u;
    v = (v >> 22) ^ v;
    return float(v & 0x00ffffffu) / 16777215.0f;
}
static double score_pixel(size_t p, int seed) {
    double x[8];
    for (int c=0;c<8;++c) x[c]=sensor_value(p,c,seed);
    const double u=x[0]*x[1]+0.35*x[2]*x[3]-0.20*x[4]-0.17;
    const double v=x[5]*x[6]-0.25*x[7]+0.10*x[0]-0.13;
    const double a=u/(1.0+std::abs(u)), b=v/(1.0+std::abs(v));
    const double d0=x[3]-x[7],d1=x[1]-x[6];
    const double z=0.12+0.66*x[0]-0.39*x[1]+0.31*x[2]*x[4]-0.27*x[5]
        +0.45*a-0.26*b+0.13*a*b+0.17*d0*d0-0.08*d1*d1;
    return 0.5+0.5*z/(1.0+std::abs(z));
}
int main(int argc,char**argv) {
    int w=argc>1?std::atoi(argv[1]):64,h=argc>2?std::atoi(argv[2]):48,seed=argc>3?std::atoi(argv[3]):19;
    if(w<1||h<1||w>4096||h>2160)return 2;
    size_t n=size_t(w)*h;double bins[32][3]={};
    for(size_t p=0;p<n;++p){double q=score_pixel(p,seed);int b=int(p%32);bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=q>=0.5?1.0:0.0;}
    size_t ids[7]={0,n/17,n/5,n/2,(3*n)/4,(16*n)/17,n-1};
    std::cout<<std::setprecision(15)<<"{\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int i=0;i<7;++i){if(i)std::cout<<',';std::cout<<score_pixel(ids[i],seed);}std::cout<<"]}\n";
}
