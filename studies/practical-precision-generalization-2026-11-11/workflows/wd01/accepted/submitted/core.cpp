#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <vector>

static float pixel_value(int x,int y,int w,int h,int seed) {
    const double gx=double(x)/std::max(1,w-1),gy=double(y)/std::max(1,h-1);
    double v=0.16+0.44*gx+0.18*gy+0.05*std::sin(0.025*x+0.13*seed)*std::cos(0.031*y-0.07*seed);
    const bool mark=((x+seed*23)%211<5)&&((y+seed*17)%173<4);
    if(mark)v+=((x/211+y/173+seed)&1)?0.24:-0.20;
    return float(std::max(0.02,std::min(0.95,v)));
}

template<class T>
static int run_direct(int w,int h,int seed,int radius) {
    const size_t n=size_t(w)*h;
    std::vector<float> image(n);
    for(int y=0;y<h;++y)for(int x=0;x<w;++x)image[size_t(y)*w+x]=pixel_value(x,y,w,h,seed);
    std::vector<T> score(n);
    for(int y=0;y<h;++y)for(int x=0;x<w;++x){
        const int y0=std::max(0,y-radius),y1=std::min(h-1,y+radius);
        const int x0=std::max(0,x-radius),x1=std::min(w-1,x+radius);
        double sum=0.0,squares=0.0;size_t count=0;
        for(int yy=y0;yy<=y1;++yy)for(int xx=x0;xx<=x1;++xx){double q=image[size_t(yy)*w+xx];sum+=q;squares+=q*q;++count;}
        const double mean=sum/count;const double variance=std::max(1e-4,squares/count-mean*mean);
        score[size_t(y)*w+x]=T((double(image[size_t(y)*w+x])-mean)/std::sqrt(variance));
    }
    double bins[32][3]={};for(size_t i=0;i<n;++i){double q=score[i];int b=int(i%32);bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=std::abs(q)>=2.5?1.0:0.0;}
    size_t ids[8]={0,size_t(w-1),size_t((h/3)*w+w/5),size_t((h/2)*w+w/2),size_t((h-1)*w),size_t((h/2)*w+w-1),n/2,n-1};
    size_t storage=image.capacity()*sizeof(float)+score.capacity()*sizeof(T);
    std::cout<<std::setprecision(13)<<"{\"storage_bytes\":"<<storage<<",\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int i=0;i<8;++i){if(i)std::cout<<',';std::cout<<double(score[ids[i]]);}std::cout<<"]}\n";
    return 0;
}

static int run_sliding(int w,int h,int seed,int radius) {
    const size_t n=size_t(w)*h;
    std::vector<float> image(n);
    for(int y=0;y<h;++y)for(int x=0;x<w;++x)
        image[size_t(y)*w+x]=pixel_value(x,y,w,h,seed);

    // Reuse each row's float horizontal window sums, then slide those sums
    // down columns. Keep the normal hot path in float arithmetic.
    std::vector<float> horizontal(n), horizontal_squares(n);
    for(int y=0;y<h;++y){
        const size_t row=size_t(y)*w;
        float sum=0.0f,squares=0.0f;
        const int initial_end=std::min(w-1,radius);
        for(int x=0;x<=initial_end;++x){
            const float q=image[row+x];sum+=q;squares+=q*q;
        }
        for(int x=0;x<w;++x){
            horizontal[row+x]=sum;horizontal_squares[row+x]=squares;
            const int leaving=x-radius;
            const int entering=x+radius+1;
            if(leaving>=0){const float q=image[row+leaving];sum-=q;squares-=q*q;}
            if(entering<w){const float q=image[row+entering];sum+=q;squares+=q*q;}
        }
    }

    std::vector<double> score(n);
    for(int x=0;x<w;++x){
        float sum=0.0f,squares=0.0f;
        const int initial_end=std::min(h-1,radius);
        for(int y=0;y<=initial_end;++y){
            const size_t i=size_t(y)*w+x;sum+=horizontal[i];squares+=horizontal_squares[i];
        }
        for(int y=0;y<h;++y){
            const int y0=std::max(0,y-radius),y1=std::min(h-1,y+radius);
            const int x0=std::max(0,x-radius),x1=std::min(w-1,x+radius);
            const float count=float((y1-y0+1)*(x1-x0+1));
            const float mean=sum/count;
            const float variance=std::max(1e-4f,squares/count-mean*mean);
            const size_t i=size_t(y)*w+x;
            score[i]=(image[i]-mean)/std::sqrt(variance);
            const int leaving=y-radius;
            const int entering=y+radius+1;
            if(leaving>=0){const size_t j=size_t(leaving)*w+x;sum-=horizontal[j];squares-=horizontal_squares[j];}
            if(entering<h){const size_t j=size_t(entering)*w+x;sum+=horizontal[j];squares+=horizontal_squares[j];}
        }
    }

    double bins[32][3]={};
    for(size_t i=0;i<n;++i){double q=score[i];int b=int(i%32);bins[b][0]+=q;bins[b][1]+=q*q;bins[b][2]+=std::abs(q)>=2.5?1.0:0.0;}
    size_t ids[8]={0,size_t(w-1),size_t((h/3)*w+w/5),size_t((h/2)*w+w/2),size_t((h-1)*w),size_t((h/2)*w+w-1),n/2,n-1};
    size_t storage=image.capacity()*sizeof(float)
        +horizontal.capacity()*sizeof(float)+horizontal_squares.capacity()*sizeof(float)
        +score.capacity()*sizeof(double);
    std::cout<<std::setprecision(13)<<"{\"storage_bytes\":"<<storage<<",\"checksums\":[";
    for(int b=0;b<32;++b){if(b)std::cout<<',';std::cout<<'['<<bins[b][0]<<','<<bins[b][1]<<','<<bins[b][2]<<']';}
    std::cout<<"],\"samples\":[";for(int i=0;i<8;++i){if(i)std::cout<<',';std::cout<<score[ids[i]];}std::cout<<"]}\n";
    return 0;
}

int main(int argc,char**argv){
    int w=argc>1?std::atoi(argv[1]):64,h=argc>2?std::atoi(argv[2]):48,seed=argc>3?std::atoi(argv[3]):11,radius=argc>4?std::atoi(argv[4]):15;
    bool audit=argc>5&&std::strcmp(argv[5],"--audit")==0;
    if(w<1||h<1||w>4096||h>2160||radius<0||radius>127)return 2;
    return audit?run_direct<double>(w,h,seed,radius):run_sliding(w,h,seed,radius);
}
