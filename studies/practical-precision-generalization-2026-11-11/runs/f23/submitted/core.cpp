#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

template<class T> int render(int frames,int ew,int eh,int dw,int dh,int layers,const char*arith,bool compact){
    using clock=std::chrono::steady_clock;
    std::vector<double> energy(frames+1);
    const std::size_t budget=4u*1024u*1024u;
    const std::size_t largest=std::max(std::size_t(ew)*eh,std::size_t(dw)*dh);
    const std::size_t budget_pixels=compact?(budget-energy.capacity()*sizeof(double))/sizeof(T):largest;
    std::vector<T> image(std::min(largest,budget_pixels));
    const auto start=clock::now();
    for(int f=0;f<=frames;f++){
        const bool detail=(f==frames); const int w=detail?dw:ew,h=detail?dh:eh;
        double total=0;
        std::size_t image_index=0;
        for(int y=0;y<h;y++) for(int x=0;x<w;x++){
                T signal=T(((x*17+y*29+f*13)%997-498))*T(0.001);
                T pixel=0;
                for(int k=0;k<layers;k++){
                    const T tint=T((k*31+x*3+y*7)%251-125)*T(0.0007);
                    pixel += (signal+tint)*(T(1)/T(k+1));
                }
                image[image_index]=pixel;
                total+=double(image[image_index]);
                if(++image_index==image.size()) image_index=0;
        }
        energy[f]=total;
    }
    const double sec=std::chrono::duration<double>(clock::now()-start).count();
    double checksum=0; for(int f=0;f<=frames;f++){std::cout<<"frame"<<f<<'='<<std::setprecision(17)<<energy[f]<<' ';checksum+=energy[f];}
    std::cout<<"checksum="<<std::setprecision(17)<<checksum<<" seconds="<<sec
             <<" buffer_bytes="<<image.capacity()*sizeof(T)+energy.capacity()*sizeof(double)
             <<" arithmetic="<<arith<<" outputs="<<(frames+1)<<" heavy_frame_pixels="<<std::size_t(dw)*dh<<'\n';
    return 0;
}
int main(int argc,char**argv){
    int frames=argc>1?std::atoi(argv[1]):12,ew=argc>2?std::atoi(argv[2]):320,eh=argc>3?std::atoi(argv[3]):180;
    int dw=argc>4?std::atoi(argv[4]):1280,dh=argc>5?std::atoi(argv[5]):720,layers=argc>6?std::atoi(argv[6]):8;
    std::string p=argc>7?argv[7]:"auto";
    if(frames<0||frames>40||ew<1||eh<1||dw<1||dh<1||std::size_t(dw)*dh>4000000||layers<1||layers>32)return 2;
    if(p=="double")return render<double>(frames,ew,eh,dw,dh,layers,"fp64",false);
    if(p=="float")return render<float>(frames,ew,eh,dw,dh,layers,"fp32-layer-products+fp64-frame-energy",true);
    if(p=="auto")return render<float>(frames,ew,eh,dw,dh,layers,"fp32-layer-products+fp64-frame-energy",true);
    std::cerr<<"mode must be auto, float, or double\n";return 2;
}
