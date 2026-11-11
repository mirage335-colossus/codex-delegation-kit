#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
#ifndef VALUE
#define VALUE float
#endif
int main(int argc,char**argv){
 int w=argc>1?std::atoi(argv[1]):512, h=argc>2?std::atoi(argv[2]):256, seed=argc>3?std::atoi(argv[3]):17;
 if(w<2||h<2||w>4096||h>2160) return 2; size_t n=(size_t)w*h;
 std::vector<VALUE> bg(n*4),fg(n*4),out(n*4);
 for(size_t p=0;p<n;++p){ unsigned k=(unsigned)(p*1664525u+seed*1013904223u);
  bg[4*p+0]=((k>>3)&1023)/1023.0; bg[4*p+1]=((k>>13)&1023)/1023.0; bg[4*p+2]=((k>>23)&255)/255.0; bg[4*p+3]=1;
  fg[4*p+0]=((k>>7)&511)/511.0; fg[4*p+1]=((k>>17)&511)/511.0; fg[4*p+2]=((k>>27)&31)/31.0; fg[4*p+3]=((k>>10)&255)/255.0;
  VALUE a=fg[4*p+3]; for(int c=0;c<3;++c) out[4*p+c]=fg[4*p+c]*a+bg[4*p+c]*(1-a); out[4*p+3]=1;
 }
 double checksum_sum[16]={0},checksum_sq[16]={0};for(size_t i=0;i<out.size();++i){double v=(double)out[i];checksum_sum[i%16]+=v;checksum_sq[i%16]+=v*v;}
 size_t ids[5]={0,n/7,n/2,(n*5)/7,n-1}; std::cout<<std::setprecision(10)<<"{\"storage_bytes\":"<< (bg.size()+fg.size()+out.size())*sizeof(VALUE)<<",\"checksums\":[";for(int b=0;b<16;++b){if(b)std::cout<<",";std::cout<<"["<<checksum_sum[b]<<","<<checksum_sq[b]<<"]";}std::cout<<"],\"samples\":[";
 for(int j=0;j<5;++j){if(j)std::cout<<",";size_t p=ids[j];std::cout<<"[";for(int c=0;c<4;++c){if(c)std::cout<<",";std::cout<<(double)out[4*p+c];}std::cout<<"]";} std::cout<<"]}\n";
}
