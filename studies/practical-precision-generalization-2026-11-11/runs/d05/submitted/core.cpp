#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>
#ifndef VALUE
#define VALUE float
#endif
int main(int argc,char**argv){int ch=argc>1?atoi(argv[1]):4,n=argc>2?atoi(argv[2]):8192,taps=argc>3?atoi(argv[3]):63,seed=argc>4?atoi(argv[4]):9;if(ch<1||ch>32||n<128||n>500000||taps<3||taps>255||!(taps&1))return 2;std::vector<VALUE>x((size_t)ch*n),h(taps),y((size_t)ch*n);
 double hs=0;for(int k=0;k<taps;++k){double z=(k-(taps-1)*0.5)/(taps*0.5);double v=(0.5+0.5*std::cos(3.141592653589793*z))*std::cos(0.23*k);h[k]=v;hs+=std::abs(v);}for(auto&v:h)v/=hs;
 for(int c=0;c<ch;++c)for(int i=0;i<n;++i)x[(size_t)c*n+i]=std::sin((i+seed*7+c*13)*0.017)+0.35*std::cos((i*3+seed+c*5)*0.009);
 int r=taps/2;for(int c=0;c<ch;++c)for(int i=0;i<n;++i){VALUE acc=0;for(int k=0;k<taps;++k){int q=i+k-r;if(q>=0&&q<n)acc+=x[(size_t)c*n+q]*h[k];}y[(size_t)c*n+i]=acc;}
  double checksum_sum[16]={0},checksum_sq[16]={0};for(size_t i=0;i<y.size();++i){double v=(double)y[i];checksum_sum[i%16]+=v;checksum_sq[i%16]+=v*v;}
size_t ids[6]={0,(size_t)n/11,(size_t)n/3,(size_t)n/2,(size_t)(n-1),((size_t)ch-1)*n+n/4};std::cout<<std::setprecision(10)<<"{\"storage_bytes\":"<<(x.size()+h.size()+y.size())*sizeof(VALUE)<<",\"checksums\":[";for(int b=0;b<16;++b){if(b)std::cout<<",";std::cout<<"["<<checksum_sum[b]<<","<<checksum_sq[b]<<"]";}std::cout<<"],\"samples\":[";for(int j=0;j<6;++j){if(j)std::cout<<",";std::cout<<(double)y[ids[j]];}std::cout<<"]}\n";}
