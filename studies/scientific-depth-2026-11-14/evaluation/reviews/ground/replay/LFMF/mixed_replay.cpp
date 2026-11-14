#include "LFMF.h"
#include <iomanip>
#include <iostream>

using namespace ITS::Propagation::LFMF;
double E(double f,double d,double eps,double sigma) {
    Result r{};
    auto rc=LFMF(0.0,0.0,f,1000.0,301.0,d,eps,sigma,1,r);
    if(rc!=SUCCESS) throw rc;
    return r.E_dBuVm;
}
int main() {
    constexpr double epsL=15.0,sigL=0.001,epsS=70.0,sigS=5.0,total=100.0;
    std::cout<<std::fixed<<std::setprecision(3);
    for(double f: {1.0,30.0}) for(double x: {10.0,50.0,90.0}) {
        const double y=total-x;
        const double fl=E(f,x,epsL,sigL)+E(f,total,epsS,sigS)-E(f,x,epsS,sigS);
        const double rf=E(f,y,epsS,sigS)+E(f,total,epsL,sigL)-E(f,y,epsL,sigL);
        std::cout<<f<<" MHz; land="<<x<<" km; sea="<<y
                 <<" km; forward="<<fl<<" reverse="<<rf
                 <<" reciprocal="<<(fl+rf)/2.0
                 <<" directional="<<fl-rf<<" dB\n";
    }
}
