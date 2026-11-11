import pathlib,subprocess,time,math,tempfile
root=pathlib.Path(__file__).resolve().parent
subprocess.run(['g++','-O2','-std=c++17','core.cpp','-o','probe'],cwd=root,check=True)
def run(args,measure=False):
 if measure:
  code='import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True);sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);sys.exit(p.returncode)'
  t=time.monotonic();p=subprocess.run(['python3','-B','-c',code,str(root/'probe'),*map(str,args)],cwd=root,text=True,capture_output=True,check=True,timeout=4);return list(map(float,p.stdout.split('CHILD_RSS_KIB')[0].split())),int(p.stdout.split('CHILD_RSS_KIB')[-1].strip()),time.monotonic()-t
 p=subprocess.run([str(root/'probe'),*map(str,args)],cwd=root,text=True,capture_output=True,check=True,timeout=4);return list(map(float,p.stdout.split()))
def exact(n,step):
 ks=[(i*17)%1001-500 for i in range(1001)];cycles,rem=divmod(n,1001);s=cycles*sum(ks)+sum(ks[:rem]);q=cycles*sum(k*k for k in ks)+sum(k*k for k in ks[:rem]);return step*s/n,math.sqrt(step*step*q/n)
for n,origin,step in [(2000,'1000000000000','0.25'),(1501,'10000000000000000','0.001')]:
 out=run([n,origin,step]);ref=exact(n,float(step));assert abs(out[0]-ref[0])<=1e-4 and abs(out[1]-ref[1])<=1e-4,(out,ref)
# Reference path retains a wider local accumulator for the difficult large-coordinate batch.
audit=run([1501,'10000000000000000','0.001','--minimum-precision']);ref=exact(1501,.001);assert abs(audit[0]-ref[0])<=1e-8 and abs(audit[1]-ref[1])<=1e-8,(audit,ref)
ticks=run([2000,'9007199254740993','3','--ticks']);ref=exact(2000,3);assert abs(ticks[0]-ref[0])<=1e-12 and abs(ticks[1]-ref[1])<=1e-12,(ticks,ref)
large,peak,elapsed=run([3200000,'1000000000000','0.25'],True);ref=exact(3200000,.25);assert abs(large[0]-ref[0])<=1e-4 and abs(large[1]-ref[1])<=1e-4,(large,ref);assert peak<=20480,f'peak {peak} KiB > 20 MiB';assert elapsed<=4,f'elapsed {elapsed:.3f}s'
print(f'PASS decimal, minimum-precision and integer-tick oracles; peak={peak} KiB elapsed={elapsed:.3f}s')
