// Bounded matched-input desk comparison for the published 1.242-MHz route.
#include "LFMF.h"
#include <iomanip>
#include <iostream>
#include <cstdlib>
using ITS::Propagation::LFMF::LFMF;
using ITS::Propagation::LFMF::Result;
struct Ground { double e,s; };
double E(double d, Ground g) {
  Result r{};
  auto rc=LFMF(0,0,1.242,1000,301,d,g.e,g.s,1,r);
  if(rc!=ITS::Propagation::LFMF::SUCCESS) std::exit(2);
  return r.E_dBuVm;
}
int main(){
  const Ground land{15,0.001}, sea{70,5};
  std::cout<<std::fixed<<std::setprecision(3);
  std::cout<<"LFMF v10, 1.242 MHz, 1 kW, 0m/0m, Ns=301, vertical, smooth homogeneous inputs; field dBuV/m\n";
  for(double d: {19.,90.}) std::cout<<"homogeneous d="<<d<<" land="<<E(d,land)<<" sea="<<E(d,sea)<<"\n";
  const double total=90,x=19,y=total-x;
  const double forward=E(x,land)+E(total,sea)-E(x,sea);
  const double reverse=E(y,sea)+E(total,land)-E(y,land);
  std::cout<<"path=19km land+71km sea; Millington forward="<<forward<<" reverse="<<reverse<<" reciprocal="<<(forward+reverse)/2<<" directional_delta="<<forward-reverse<<" dB\n";
}
