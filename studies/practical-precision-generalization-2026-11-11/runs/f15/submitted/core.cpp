#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>
#ifndef VALUE
#define VALUE float
#endif
int main(int argc,char**argv){int w=argc>1?atoi(argv[1]):256,h=argc>2?atoi(argv[2]):192,steps=argc>3?atoi(argv[3]):40,seed=argc>4?atoi(argv[4]):31;if(w<3||h<3||w>2048||h>2048||steps<1||steps>500)return 2;size_t n=(size_t)w*h;std::vector<VALUE>a(n),b(n);
 for(int y=0;y<h;++y)for(int x=0;x<w;++x){size_t i=(size_t)y*w+x; a[i]=(x==0||y==0||x==w-1||y==h-1)?0.125:(((x*17+y*29+seed*13)%97)==0?1.0:0.0);}
 for(int s=0;s<steps;++s){b=a;for(int y=1;y<h-1;++y)for(int x=1;x<w-1;++x){size_t i=(size_t)y*w+x;b[i]=VALUE(0.25)*(a[i-1]+a[i+1]+a[i-w]+a[i+w]);}a.swap(b);}
  double checksum_sum[16]={0},checksum_sq[16]={0};for(size_t i=0;i<a.size();++i){double v=(double)a[i];checksum_sum[i%16]+=v;checksum_sq[i%16]+=v*v;}
size_t ids[6]={0,(size_t)w-1,(size_t)(h/3)*w+w/4,(size_t)(h/2)*w+w/2,(size_t)(h-2)*w+w/2,n-1};std::cout<<std::setprecision(10)<<"{\"storage_bytes\":"<<a.size()*sizeof(VALUE)+b.size()*sizeof(VALUE)<<",\"checksums\":[";for(int b=0;b<16;++b){if(b)std::cout<<",";std::cout<<"["<<checksum_sum[b]<<","<<checksum_sq[b]<<"]";}std::cout<<"],\"samples\":[";for(int j=0;j<6;++j){if(j)std::cout<<",";std::cout<<(double)a[ids[j]];}std::cout<<"]}\n";}
