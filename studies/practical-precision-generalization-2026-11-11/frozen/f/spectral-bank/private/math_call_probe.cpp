#include <cstdio>
#include <dlfcn.h>
#include <atomic>
namespace { using fn=double(*)(double); std::atomic<fn> real_sin{nullptr},real_cos{nullptr}; std::atomic<unsigned long long> calls{0}; }
using sincos_fn=void(*)(double,double*,double*);
static std::atomic<sincos_fn> real_pair{nullptr};
extern "C" double sin(double x){auto f=real_sin.load();if(!f){f=reinterpret_cast<fn>(dlsym(RTLD_NEXT,"sin"));real_sin.store(f);}calls.fetch_add(1);return f(x);}
extern "C" double cos(double x){auto f=real_cos.load();if(!f){f=reinterpret_cast<fn>(dlsym(RTLD_NEXT,"cos"));real_cos.store(f);}calls.fetch_add(1);return f(x);}
extern "C" void sincos(double x,double*s,double*c){auto f=real_pair.load();if(!f){f=reinterpret_cast<sincos_fn>(dlsym(RTLD_NEXT,"sincos"));real_pair.store(f);}calls.fetch_add(2);f(x,s,c);}
__attribute__((destructor)) static void report(){std::fprintf(stderr,"math_calls=%llu\n",calls.load());}
