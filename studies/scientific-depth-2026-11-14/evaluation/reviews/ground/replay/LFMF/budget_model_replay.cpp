#include "LFMF.h"
#include <iomanip>
#include <iostream>
using namespace ITS::Propagation::LFMF;
int main(){
  for(double f:{1.0,30.0}){
    Result r{};
    const auto rc=LFMF(0,0,f,1.0,301,100,15,0.001,1,r);
    if(rc!=SUCCESS)return 2;
    std::cout<<std::fixed<<std::setprecision(3)<<f<<"MHz E="<<r.E_dBuVm
             <<" dBuV/m P_rx="<<r.P_rx__dbm<<"dBm Lb="<<r.A_btl__db<<"dB\n";
  }
}
