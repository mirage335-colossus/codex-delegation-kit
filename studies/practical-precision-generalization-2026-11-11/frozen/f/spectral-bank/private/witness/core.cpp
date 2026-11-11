#include <chrono>
#include <cmath>
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
struct Plan{std::vector<std::size_t> reverse;std::vector<double> wr,wi,window;};
static Plan make_plan(int n){
    Plan p;p.reverse.resize(n);p.wr.resize(n/2);p.wi.resize(n/2);p.window.resize(n);
    unsigned bits=0;while((1u<<bits)<unsigned(n))++bits;
    for(int i=0;i<n;i++){unsigned v=i,r=0;for(unsigned b=0;b<bits;b++){r=(r<<1)|(v&1);v>>=1;}p.reverse[i]=r;}
    const double tau=6.283185307179586476925286766559;
    for(int k=0;k<n/2;k++){p.wr[k]=std::cos(tau*k/n);p.wi[k]=-std::sin(tau*k/n);}
    for(int i=0;i<n;i++)p.window[i]=0.5-0.5*std::cos(tau*i/(n-1));
    return p;
}
static void transform(std::vector<double>&re,std::vector<double>&im,const Plan&p){
    const int n=int(re.size());
    for(int len=2;len<=n;len*=2){const int half=len/2,step=n/len;
        for(int base=0;base<n;base+=len)for(int j=0;j<half;j++){
            const int t=j*step;const double vr=re[base+j+half]*p.wr[t]-im[base+j+half]*p.wi[t];
            const double vi=re[base+j+half]*p.wi[t]+im[base+j+half]*p.wr[t];
            const double ur=re[base+j],ui=im[base+j];re[base+j]=ur+vr;im[base+j]=ui+vi;
            re[base+j+half]=ur-vr;im[base+j+half]=ui-vi;
        }
    }
}
static int fft_bank(int channels,int windows,int n){
    const int bins=n/2+1;std::vector<double> all(std::size_t(channels)*windows*bins);
    const auto begin=std::chrono::steady_clock::now();const Plan plan=make_plan(n);
    std::vector<double> re(n),im(n);
    for(int c=0;c<channels;c++)for(int w=0;w<windows;w++){
        for(int i=0;i<n;i++){re[plan.reverse[i]]=sample(c,w,i,n)*plan.window[i];im[plan.reverse[i]]=0;}
        transform(re,im,plan);
        for(int k=0;k<bins;k++)all[(std::size_t(c)*windows+w)*bins+k]=re[k]*re[k]+im[k]*im[k];
    }
    const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    std::cout<<std::setprecision(17)<<"seconds="<<sec<<" algorithm=fft-plan channels="<<channels
             <<" windows="<<windows<<" samples="<<n<<" outputs="<<all.size()<<" values=";
    for(double v:all)std::cout<<v<<',';std::cout<<'\n';return 0;
}
static int run(int channels,int windows,int n,std::string mode){
    if(channels<1||channels>64||windows<1||windows>8||n<16||n>1024||(n&(n-1)))return 2;
    if(mode!="auto"&&mode!="direct"){std::cerr<<"mode must be auto or direct\n";return 2;}
    return mode=="direct"?direct(channels,windows,n):fft_bank(channels,windows,n);
}
int main(int argc,char**argv){
    if(argc>1&&std::string(argv[1])=="--sequence"){
        int c,w,n;std::string m;while(std::cin>>c>>w>>n>>m)if(run(c,w,n,m))return 2;return 0;
    }
    int channels=argc>1?std::atoi(argv[1]):4,windows=argc>2?std::atoi(argv[2]):2,n=argc>3?std::atoi(argv[3]):128;
    std::string mode=argc>4?argv[4]:"auto";
    return run(channels,windows,n,mode);
}
