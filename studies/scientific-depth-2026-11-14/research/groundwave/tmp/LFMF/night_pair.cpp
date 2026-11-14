#include "LFMF.h"
#include <iostream>
#include <iomanip>
using ITS::Propagation::LFMF::LFMF; using ITS::Propagation::LFMF::Result;
int main(){for(auto g:{std::pair<double,double>{15,.001},{70,5}}){Result r{}; LFMF(0,0,1,1000,301,419,g.first,g.second,1,r); std::cout<<std::fixed<<std::setprecision(3)<<"f=1MHz d=419km epsilon="<<g.first<<" sigma="<<g.second<<" E="<<r.E_dBuVm<<" dBuV/m\n";}}
