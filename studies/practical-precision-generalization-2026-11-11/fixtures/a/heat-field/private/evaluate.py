import math,json,pathlib,subprocess,sys,tempfile,time
base=pathlib.Path(__file__).resolve().parents[1]
src=(pathlib.Path(sys.argv[1])/'core.cpp' if len(sys.argv)>1 and pathlib.Path(sys.argv[1]).is_dir() else (pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'participant/core.cpp'))
def expected(w,h,steps,seed):
 a=[0.]*(w*h)
 for y in range(h):
  for x in range(w):a[y*w+x]=.125 if x==0 or y==0 or x==w-1 or y==h-1 else (1. if (x*17+y*29+seed*13)%97==0 else 0.)
 for _ in range(steps):
  b=a.copy()
  for y in range(1,h-1):
   q=y*w
   for x in range(1,w-1):i=q+x;b[i]=.25*(a[i-1]+a[i+1]+a[i-w]+a[i+w])
  a=b
 ids=[0,w-1,(h//3)*w+w//4,(h//2)*w+w//2,(h-2)*w+w//2,w*h-1];s=[[0.,0.] for _ in range(16)]
 for i,v in enumerate(a):b=i%16;s[b][0]+=v;s[b][1]+=v*v
 return [a[i] for i in ids],s

def evaluate(path):
 with tempfile.TemporaryDirectory() as td:
  td=pathlib.Path(td);tracker=td/'tracker.hpp';tracker.write_text(TRACKER)
  exe=td/'candidate';refexe=td/'reference'
  compile_cmd=['c++','-O2','-std=c++17','-include',str(tracker),str(path),'-o',str(exe)]
  ref_cmd=['c++','-O2','-std=c++17','-include',str(tracker),'-DVALUE=double',str(base/'private/witness/core.cpp'),'-o',str(refexe)]
  subprocess.run(compile_cmd,check=True);subprocess.run(ref_cmd,check=True)
  cases=[(1024,512,160,31),(83,67,29,997),(117,91,51,3)];rows=[]
  for case in cases:
   w,h,steps,seed=case
   run_cmd=[str(exe),str(w),str(h),str(steps),str(seed)];t=time.perf_counter();r=subprocess.run(run_cmd,capture_output=True,text=True,check=True);elapsed=time.perf_counter()-t;x=json.loads(r.stdout);tracked=int(r.stderr.split('TRACKED_PEAK_BYTES=')[-1].strip())
   rr=subprocess.run([str(refexe),str(w),str(h),str(steps),str(seed)],capture_output=True,text=True,check=True);rx=json.loads(rr.stdout)
   cap_bytes=5*1024*1024;assert x['storage_bytes']<=cap_bytes,f"reported storage {x['storage_bytes']} > {cap_bytes}";assert tracked<=cap_bytes,f"tracked allocation peak {tracked} > {cap_bytes}"
   assert len(x['samples'])==len(rx['samples'])==6 and len(x['checksums'])==len(rx['checksums'])==16 and all(len(v)==2 for v in x['checksums']+rx['checksums']);assert all(math.isfinite(v) for v in x['samples']+x['checksums'] for v in ([v] if not isinstance(v,list) else v))
   sample_err=max(abs(a-b) for a,b in zip(x['samples'],rx['samples']))
   counts=[(w*h+15-b)//16 for b in range(16)]
   checksum_err=max(max(abs(x['checksums'][b][0]-rx['checksums'][b][0]),abs(x['checksums'][b][1]-rx['checksums'][b][1]))/counts[b] for b in range(16))
   assert sample_err<=3e-4,f"sample quality error {sample_err}";assert checksum_err<=9e-4,f"full-output checksum quality error {checksum_err}"
   rows.append({'w*h':list(case),'storage_bytes_reported':x['storage_bytes'],'tracked_allocation_peak_bytes':tracked,'max_sample_error':sample_err,'full_output_checksum_error_per_element':checksum_err,'elapsed_seconds':elapsed,'compile_command':compile_cmd,'run_command':run_cmd})
  result={'passed':True,'checks':['actual tracked C++ heap peak','reported element storage','sample values','16-bin full-output sum and square aggregates'],'cases':rows}
  return result
TRACKER=r'''
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <new>
#include <malloc.h>
namespace { std::atomic<size_t> live_bytes{0}, peak_bytes{0}; inline void add_bytes(size_t n){size_t v=live_bytes.fetch_add(n)+n, p=peak_bytes.load();while(v>p&&!peak_bytes.compare_exchange_weak(p,v)){} } inline void sub_bytes(void*p){if(p)live_bytes.fetch_sub(malloc_usable_size(p));} }
void* operator new(size_t n){if(void*p=std::malloc(n?n:1)){add_bytes(malloc_usable_size(p));return p;}throw std::bad_alloc();}
void* operator new[](size_t n){return ::operator new(n);}
void operator delete(void*p) noexcept{sub_bytes(p);std::free(p);}
void operator delete[](void*p) noexcept{::operator delete(p);}
void operator delete(void*p,size_t) noexcept{::operator delete(p);}
void operator delete[](void*p,size_t) noexcept{::operator delete(p);}
__attribute__((destructor)) static void report_peak(){std::fprintf(stderr,"TRACKED_PEAK_BYTES=%zu\n",peak_bytes.load());}
'''
if __name__=='__main__':
 try:
  result=evaluate(src);print(json.dumps(result,indent=2))
 except Exception as e:
  print(json.dumps({'passed':False,'failure':str(e),'checks':'compile/run/tracked-memory/sample/full-output-quality'}));sys.exit(1)
