#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <complex>
#include <unordered_map>
#include <string>
#include <vector>

static double sample(int channel,int window,int i,int n){
    const double tau=6.283185307179586476925286766559;
    return 0.55*std::sin(tau*i*(3+channel%11)/n+0.07*window)
         + 0.22*std::cos(tau*i*(17+window%7)/n+0.03*channel)
         + 0.001*(int((i*17+channel*31+window*13)%101)-50);
}
static int direct(int channels,int windows,int n){
    const int bins=n/2+1;
    std::vector<double> all(std::size_t(channels)*windows*bins);
    using clock=std::chrono::steady_clock;const auto begin=clock::now();
    for(int c=0;c<channels;c++)for(int w=0;w<windows;w++){
        std::vector<double> frame(n);
        for(int i=0;i<n;i++)frame[i]=sample(c,w,i,n)*(0.5-0.5*std::cos(6.283185307179586476925286766559*i/(n-1)));
        for(int k=0;k<bins;k++){
            double re=0,im=0;
            for(int i=0;i<n;i++){
                const double a=-6.283185307179586476925286766559*k*i/n;
                re+=frame[i]*std::cos(a); im+=frame[i]*std::sin(a);
            }
            all[(std::size_t(c)*windows+w)*bins+k]=re*re+im*im;
        }
    }
    const double sec=std::chrono::duration<double>(clock::now()-begin).count();
    std::cout<<std::setprecision(17)<<"seconds="<<sec<<" algorithm=direct channels="<<channels
             <<" windows="<<windows<<" samples="<<n<<" outputs="<<all.size()<<" values=";
    for(double v:all)std::cout<<v<<',';
    std::cout<<'\n';return 0;
}
struct Plan {
    std::vector<int> reversed;
    std::vector<std::complex<float>> twiddles;
    std::vector<float> window;
    explicit Plan(int n):reversed(n),twiddles(n/2),window(n){
        int bits=0;while((1<<bits)<n)++bits;
        for(int i=0;i<n;i++){
            unsigned x=static_cast<unsigned>(i),r=0;
            for(int b=0;b<bits;b++){r=(r<<1)|(x&1u);x>>=1;}
            reversed[i]=static_cast<int>(r);
            window[i]=static_cast<float>(0.5-0.5*std::cos(6.283185307179586476925286766559*i/(n-1)));
        }
        for(int j=0;j<n/2;j++){
            const float a=static_cast<float>(-6.283185307179586476925286766559*j/n);
            twiddles[j]={std::cos(a),std::sin(a)};
        }
    }
};
static int automatic(int channels,int windows,int n){
    const int bins=n/2+1;
    using clock=std::chrono::steady_clock;
    const auto begin=clock::now();
    static std::unordered_map<int,Plan> plans;
    auto it=plans.find(n);
    if(it==plans.end())it=plans.emplace(n,Plan(n)).first;
    const Plan& p=it->second;
    std::vector<double> all(std::size_t(channels)*windows*bins);
    std::vector<std::complex<float>> data(n);
    for(int c=0;c<channels;c++)for(int w=0;w<windows;w++){
        for(int i=0;i<n;i++)data[p.reversed[i]]=static_cast<float>(sample(c,w,i,n))*p.window[i];
        for(int len=2;len<=n;len*=2){
            const int half=len/2,step=n/len;
            for(int base=0;base<n;base+=len)for(int j=0;j<half;j++){
                const auto u=data[base+j];
                const auto v=data[base+j+half]*p.twiddles[j*step];
                data[base+j]=u+v;data[base+j+half]=u-v;
            }
        }
        for(int k=0;k<bins;k++){
            const float re=data[k].real(),im=data[k].imag();
            all[(std::size_t(c)*windows+w)*bins+k]=double(re)*re+double(im)*im;
        }
    }
    const double sec=std::chrono::duration<double>(clock::now()-begin).count();
    std::cout<<std::setprecision(17)<<"seconds="<<sec<<" algorithm=fft-f32 channels="<<channels
             <<" windows="<<windows<<" samples="<<n<<" outputs="<<all.size()<<" values=";
    for(double v:all)std::cout<<v<<',';
    std::cout<<'\n';return 0;
}
static int run(int channels,int windows,int n,std::string mode){
    if(channels<1||channels>64||windows<1||windows>8||n<16||n>1024||(n&(n-1)))return 2;
    if(mode!="auto"&&mode!="direct"){std::cerr<<"mode must be auto or direct\n";return 2;}
    return mode=="direct"?direct(channels,windows,n):automatic(channels,windows,n);
}
int main(int argc,char**argv){
    if(argc>1&&std::string(argv[1])=="--sequence"){
        int c,w,n;std::string m;while(std::cin>>c>>w>>n>>m)if(run(c,w,n,m))return 2;return 0;
    }
    int channels=argc>1?std::atoi(argv[1]):4,windows=argc>2?std::atoi(argv[2]):2,n=argc>3?std::atoi(argv[3]):128;
    std::string mode=argc>4?argv[4]:"auto";
    return run(channels,windows,n,mode);
}
