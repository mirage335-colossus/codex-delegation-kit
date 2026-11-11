#include <chrono>
#include <cmath>
#include <complex>
#include <cstdlib>
#include <iomanip>
#include <iostream>
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
static int automatic(int channels,int windows,int n){
    const int bins=n/2+1;
    const double tau=6.283185307179586476925286766559;
    // These tables are invariant across every channel and window in this run.
    std::vector<double> taper(n);
    for(int i=0;i<n;i++)taper[i]=0.5-0.5*std::cos(tau*i/(n-1));
    std::vector<std::complex<double>> roots(n/2);
    for(int j=0;j<n/2;j++){
        const double a=-tau*j/n;
        roots[j]={std::cos(a),std::sin(a)};
    }
    std::vector<std::complex<double>> frame(n);
    std::vector<double> all(std::size_t(channels)*windows*bins);
    using clock=std::chrono::steady_clock;const auto begin=clock::now();
    for(int c=0;c<channels;c++)for(int w=0;w<windows;w++){
        for(int i=0;i<n;i++)frame[i]={sample(c,w,i,n)*taper[i],0.0};
        // In-place iterative radix-2 Cooley-Tukey transform.
        for(unsigned i=1,j=0;i<unsigned(n);i++){
            unsigned bit=unsigned(n)>>1;
            for(;j&bit;bit>>=1)j^=bit;
            j^=bit;
            if(i<j)std::swap(frame[i],frame[j]);
        }
        for(int len=2;len<=n;len<<=1){
            const int half=len/2, stride=n/len;
            for(int base=0;base<n;base+=len)for(int j=0;j<half;j++){
                const auto u=frame[base+j];
                const auto v=frame[base+j+half]*roots[j*stride];
                frame[base+j]=u+v;
                frame[base+j+half]=u-v;
            }
        }
        const std::size_t offset=(std::size_t(c)*windows+w)*bins;
        for(int k=0;k<bins;k++)all[offset+k]=std::norm(frame[k]);
    }
    const double sec=std::chrono::duration<double>(clock::now()-begin).count();
    std::cout<<std::setprecision(17)<<"seconds="<<sec<<" algorithm=fft channels="<<channels
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
