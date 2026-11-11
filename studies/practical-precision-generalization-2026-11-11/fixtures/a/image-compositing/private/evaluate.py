import math,json,pathlib,subprocess,sys,tempfile,time
base=pathlib.Path(__file__).resolve().parents[1]
src=(pathlib.Path(sys.argv[1])/'core.cpp' if len(sys.argv)>1 and pathlib.Path(sys.argv[1]).is_dir() else (pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'participant/core.cpp'))
def expected(w,h,seed):
 n=w*h; ids=[0,n//7,n//2,(n*5)//7,n-1];out=[];s=[[0.,0.] for _ in range(16)]
 for p in range(n):
  k=(p*1664525+seed*1013904223)&0xffffffff;bg=[((k>>3)&1023)/1023.,((k>>13)&1023)/1023.,((k>>23)&255)/255.];fg=[((k>>7)&511)/511.,((k>>17)&511)/511.,((k>>27)&31)/31.];a=((k>>10)&255)/255.
  vals=[fg[c]*a+bg[c]*(1-a) for c in range(3)]+[1.]
  for c,v in enumerate(vals):b=(4*p+c)%16;s[b][0]+=v;s[b][1]+=v*v
  if p in ids:out.append(vals)
 return out,s

def evaluate(path):
 with tempfile.TemporaryDirectory() as td:
  td=pathlib.Path(td);tracker=td/'tracker.hpp';tracker.write_text(TRACKER)
  exe=td/'candidate';refexe=td/'reference'
  compile_cmd=['c++','-O2','-std=c++17','-include',str(tracker),str(path),'-o',str(exe)]
  ref_cmd=['c++','-O2','-std=c++17','-include',str(tracker),'-DVALUE=double',str(base/'private/witness/core.cpp'),'-o',str(refexe)]
  subprocess.run(compile_cmd,check=True);subprocess.run(ref_cmd,check=True)
  cases=[(1920,1080,17),(733,517,201),(257,191,0)];rows=[]
  for case in cases:
   w,h,seed=case
   run_cmd=[str(exe),str(w),str(h),str(seed)];t=time.perf_counter();r=subprocess.run(run_cmd,capture_output=True,text=True,check=True);elapsed=time.perf_counter()-t;x=json.loads(r.stdout);tracked=int(r.stderr.split('TRACKED_PEAK_BYTES=')[-1].strip())
   rr=subprocess.run([str(refexe),str(w),str(h),str(seed)],capture_output=True,text=True,check=True);rx=json.loads(rr.stdout)
   cap_bytes=110*1024*1024;assert x['storage_bytes']<=cap_bytes,f"reported storage {x['storage_bytes']} > {cap_bytes}";assert tracked<=cap_bytes,f"tracked allocation peak {tracked} > {cap_bytes}"
   assert len(x['samples'])==len(rx['samples'])==5 and all(len(v)==4 for v in x['samples']+rx['samples']);assert len(x['checksums'])==len(rx['checksums'])==16 and all(len(v)==2 for v in x['checksums']+rx['checksums']);assert all(math.isfinite(v) for row in x['samples']+x['checksums'] for v in row)
   sample_err=max(abs(a-b) for row,refrow in zip(x['samples'],rx['samples']) for c,(a,b) in enumerate(zip(row,refrow)) if c<3);alpha_err=max(abs(row[3]-1.) for row in x['samples']);assert alpha_err<=1e-7,f'alpha output error {alpha_err}'
   counts=[(4*w*h+15-b)//16 for b in range(16)]
   checksum_err=max(max(abs(x['checksums'][b][0]-rx['checksums'][b][0]),abs(x['checksums'][b][1]-rx['checksums'][b][1]))/counts[b] for b in range(16))
   assert sample_err<=2e-5,f"sample quality error {sample_err}";assert checksum_err<=6e-5,f"full-output checksum quality error {checksum_err}"
   rows.append({'4*w*h':list(case),'storage_bytes_reported':x['storage_bytes'],'tracked_allocation_peak_bytes':tracked,'max_sample_error_rgb':sample_err,'max_alpha_error':alpha_err,'full_output_checksum_error_per_element':checksum_err,'elapsed_seconds':elapsed,'compile_command':compile_cmd,'run_command':run_cmd})
  result={'passed':True,'checks':['actual tracked C++ heap peak','reported element storage','sample values','16-bin full-output sum and square aggregates'],'cases':rows}
  # Exercise the public diagnostic double override outside the float storage cap.
  override_exe=td/'candidate-double';override_cmd=['c++','-O2','-std=c++17','-include',str(tracker),'-DVALUE=double',str(path),'-o',str(override_exe)];subprocess.run(override_cmd,check=True)
  c=cases[0];w,h,seed=c;rrargs=[str(refexe),str(w),str(h),str(seed)];refx=json.loads(subprocess.run(rrargs,capture_output=True,text=True,check=True).stdout)
  oxrun=[str(override_exe),str(w),str(h),str(seed)];orun=subprocess.run(oxrun,capture_output=True,text=True,check=True);ox=json.loads(orun.stdout);otracked=int(orun.stderr.split('TRACKED_PEAK_BYTES=')[-1].strip())
  assert len(ox['samples'])==len(refx['samples'])==5 and len(ox['checksums'])==len(refx['checksums'])==16 and all(math.isfinite(v) for row in ox['samples']+ox['checksums'] for v in row);oe=max(abs(ox['checksums'][b][j]-refx['checksums'][b][j])/((4*w*h+15-b)//16) for b in range(16) for j in (0,1));oerr=max(abs(a-b) for row,refrow in zip(ox['samples'],refx['samples']) for a,b in zip(row,refrow));assert oerr<=2e-9 and oe<=2e-8,f"double override failed high-precision reference fidelity: sample {oerr}, checksum {oe}"
  result['double_override']={'passed':True,'storage_bytes':ox['storage_bytes'],'tracked_allocation_peak_bytes':otracked,'reference_checksum_max_delta_per_element':oe,'reference_sample_max_error':oerr,'tracked_allocation_peak_bytes':otracked,'compile_command':override_cmd,'run_command':oxrun,'storage_cap_applies':False}
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
