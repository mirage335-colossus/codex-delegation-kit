#include <iostream>
int main(){
#if defined(__x86_64__) || defined(__i386__)
    __builtin_cpu_init();std::cout<<"avx2="<<(__builtin_cpu_supports("avx2")?"true":"false")<<'\n';
#else
    std::cout<<"avx2=false\n";
#endif
    std::cout<<"gpu_backend=absent\n";
}
