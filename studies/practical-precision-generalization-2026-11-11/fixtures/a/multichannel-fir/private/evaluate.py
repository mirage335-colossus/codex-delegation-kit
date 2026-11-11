import math,json,pathlib,subprocess,sys,tempfile,time
base=pathlib.Path(__file__).resolve().parents[1]
src=(pathlib.Path(sys.argv[1])/'core.cpp' if len(sys.argv)>1 and pathlib.Path(sys.argv[1]).is_dir() else (pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/'participant/core.cpp'))
def expected(ch,n,taps,seed):
 h=[];hs=0.
 for k in range(taps):z=(k-(taps-1)*.5)/(taps*.5);v=(.5+.5*math.cos(math.pi*z))*math.cos(.23*k);h.append(v);hs+=abs(v)
 h=[v/hs for v in h];r=taps//2;ids=[0,n//11,n//3,n//2,n-1,(ch-1)*n+n//4];out=[];s=[[0.,0.] for _ in range(16)]
 for c in range(ch):
  for i in range(n):
   acc=0.
   for k in range(taps):q=i+k-r;acc+=(math.sin((q+seed*7+c*13)*.017)+.35*math.cos((q*3+seed+c*5)*.009))*h[k] if 0<=q<n else 0.
   b=(c*n+i)%16;s[b][0]+=acc;s[b][1]+=acc*acc
   if c*n+i in ids:out.append(acc)
 return out,s

def evaluate(path):
 with tempfile.TemporaryDirectory() as td:
  td=pathlib.Path(td);tracker=td/'tracker.hpp';tracker.write_text(TRACKER)
  exe=td/'candidate';refexe=td/'reference'
  compile_cmd=['c++','-O2','-std=c++17','-include',str(tracker),str(path),'-o',str(exe)]
  ref_cmd=['c++','-O2','-std=c++17','-include',str(tracker),'-DVALUE=double',str(base/'private/witness/core.cpp'),'-o',str(refexe)]
  subprocess.run(compile_cmd,check=True);subprocess.run(ref_cmd,check=True)
  cases=[(8,32768,127,9),(3,4096,63,113),(5,2048,31,1)];rows=[]
  for case in cases:
   ch,n,taps,seed=case
   run_cmd=[str(exe),str(ch),str(n),str(taps),str(seed)];t=time.perf_counter();r=subprocess.run(run_cmd,capture_output=True,text=True,check=True);elapsed=time.perf_counter()-t;x=json.loads(r.stdout);tracked=int(r.stderr.split('TRACKED_PEAK_BYTES=')[-1].strip())
   rr=subprocess.run([str(refexe),str(ch),str(n),str(taps),str(seed)],capture_output=True,text=True,check=True);rx=json.loads(rr.stdout)
   cap_bytes=int(2.8*1024*1024);assert x['storage_bytes']<=cap_bytes,f"reported storage {x['storage_bytes']} > {cap_bytes}";assert tracked<=cap_bytes,f"tracked allocation peak {tracked} > {cap_bytes}"
   assert len(x['samples'])==len(rx['samples'])==6 and len(x['checksums'])==len(rx['checksums'])==16 and all(len(v)==2 for v in x['checksums']+rx['checksums']);assert all(math.isfinite(v) for v in x['samples']) and all(math.isfinite(v) for row in x['checksums'] for v in row)
   sample_err=max(abs(a-b) for a,b in zip(x['samples'],rx['samples']))
   counts=[(ch*n+15-b)//16 for b in range(16)]
   checksum_err=max(max(abs(x['checksums'][b][0]-rx['checksums'][b][0]),abs(x['checksums'][b][1]-rx['checksums'][b][1]))/counts[b] for b in range(16))
   assert sample_err<=2e-5,f"sample quality error {sample_err}";assert checksum_err<=6e-5,f"full-output checksum quality error {checksum_err}"
   rows.append({'ch*n':list(case),'storage_bytes_reported':x['storage_bytes'],'tracked_allocation_peak_bytes':tracked,'max_sample_error':sample_err,'full_output_checksum_error_per_element':checksum_err,'elapsed_seconds':elapsed,'compile_command':compile_cmd,'run_command':run_cmd})
  result={'passed':True,'checks':['actual tracked C++ heap peak','reported element storage','sample values','16-bin full-output sum and square aggregates'],'cases':rows}
  # Exercise the public diagnostic double override outside the float storage cap.
  override_exe=td/'candidate-double';override_cmd=['c++','-O2','-std=c++17','-include',str(tracker),'-DVALUE=double',str(path),'-o',str(override_exe)];subprocess.run(override_cmd,check=True)
  c=cases[0];ch,n,taps,seed=c;rrargs=[str(refexe),str(ch),str(n),str(taps),str(seed)];refx=json.loads(subprocess.run(rrargs,capture_output=True,text=True,check=True).stdout)
  oxrun=[str(override_exe),str(ch),str(n),str(taps),str(seed)];orun=subprocess.run(oxrun,capture_output=True,text=True,check=True);ox=json.loads(orun.stdout);otracked=int(orun.stderr.split('TRACKED_PEAK_BYTES=')[-1].strip())
  assert len(ox['samples'])==len(refx['samples'])==6 and len(ox['checksums'])==len(refx['checksums'])==16 and all(math.isfinite(v) for v in ox['samples']) and all(math.isfinite(v) for row in ox['checksums'] for v in row);oe=max(abs(ox['checksums'][b][j]-refx['checksums'][b][j])/((ch*n+15-b)//16) for b in range(16) for j in (0,1));oerr=max(abs(a-b) for a,b in zip(ox['samples'],refx['samples']));assert oerr<=2e-9 and oe<=2e-8,f"double override failed high-precision reference fidelity: sample {oerr}, checksum {oe}"
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
