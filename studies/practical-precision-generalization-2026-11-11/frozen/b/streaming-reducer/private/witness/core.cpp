#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
static double sample(std::uint64_t i,int c){std::uint64_t x=(i+1)*6364136223846793005ULL+(c+7)*1442695040888963407ULL;x^=x>>29;x*=0x9e3779b97f4a7c15ULL;x^=x>>32;return (static_cast<int>(x%200001)-100000)*0.01;}
int main(int argc,char**argv){if(argc!=3)return 2;std::size_t n=strtoull(argv[1],0,10),w=strtoull(argv[2],0,10);constexpr int C=8;if(!n||!w||w>n)return 2;std::vector<float> ring(w*C);double sums[C]={},out[C]={};for(std::size_t i=0;i<n;++i){int slot=(i%w)*C;if(i>=w)for(int c=0;c<C;++c)sums[c]-=ring[slot+c];for(int c=0;c<C;++c){float v=static_cast<float>(sample(i,c));ring[slot+c]=v;sums[c]+=v;}if(i+1>=w)for(int c=0;c<C;++c)out[c]+=sums[c]/w;}std::cout.precision(17);for(int c=0;c<C;++c)std::cout<<out[c]<<(c+1==C?'\n':' ');}
