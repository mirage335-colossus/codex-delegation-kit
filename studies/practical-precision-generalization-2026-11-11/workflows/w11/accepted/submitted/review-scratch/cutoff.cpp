#define main production_main
#include "../core.cpp"
#undef main
#include <limits>
int main() {
  double a=0,b=1;
  for(int k=0;k<80;++k){double m=(a+b)*0.5;if(calibration(m)<3.8)a=m;else b=m;}
  float below=float(a);
  while(calibration(double(below))>=3.8)below=std::nextafter(below,0.0f);
  while(calibration(double(std::nextafter(below,1.0f)))<3.8)below=std::nextafter(below,1.0f);
  const float above=std::nextafter(below,1.0f);
  float table[kCurveSize];
  for(size_t j=0;j<kCurveSize;++j)table[j]=float(calibration(double(j)/double(kCurveSize-1)));
  auto lookup=[&](float x){const float pos=x*float(kCurveSize-1);const size_t lo=std::min(size_t(pos),kCurveSize-2);const float frac=pos-float(lo);return table[lo]+(table[lo+1]-table[lo])*frac;};
  float x=below;for(int i=0;i<4096;++i)x=std::nextafter(x,0.0f);
  int mismatch=0;double maxerr=0;
  for(int i=0;i<8194;++i){const double exact=calibration(double(x));const float fast=lookup(x);mismatch+=(exact>=3.8)!=(fast>=3.8);maxerr=std::max(maxerr,std::abs(exact-double(fast)));x=std::nextafter(x,1.0f);}
  std::cout<<std::setprecision(17)<<"cutoff="<<a<<"\nbelow_x="<<below<<" below_exact="<<calibration(double(below))<<" below_lookup="<<lookup(below)<<"\nabove_x="<<above<<" above_exact="<<calibration(double(above))<<" above_lookup="<<lookup(above)<<"\nnear_cutoff_inputs=8194 mismatches="<<mismatch<<" max_error="<<maxerr<<"\n";
  return mismatch!=0;
}
