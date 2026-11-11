#include <atomic>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <new>
namespace { struct alignas(std::max_align_t) Header { std::size_t n; };
std::atomic<std::size_t> live{0}, peak{0};
void account(std::size_t n){auto v=live.fetch_add(n)+n;auto p=peak.load();while(v>p&&!peak.compare_exchange_weak(p,v)){} }
void release(std::size_t n){live.fetch_sub(n);} }
void* operator new(std::size_t n){if(!n)n=1;auto*h=static_cast<Header*>(std::malloc(sizeof(Header)+n));if(!h)throw std::bad_alloc();h->n=n;account(n);return h+1;}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void*p) noexcept {if(p){auto*h=static_cast<Header*>(p)-1;release(h->n);std::free(h);}}
void operator delete[](void*p) noexcept {::operator delete(p);}
void operator delete(void*p,std::size_t) noexcept {::operator delete(p);}
void operator delete[](void*p,std::size_t) noexcept {::operator delete(p);}
__attribute__((destructor)) static void report_peak(){std::fprintf(stderr,"heap_peak_bytes=%zu\n",peak.load());}
