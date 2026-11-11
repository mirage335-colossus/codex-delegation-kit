import json,pathlib,subprocess,sys,tempfile,time,math
src=pathlib.Path(sys.argv[1]).resolve()/'core.cpp'
def expected(n,step):
 period=[(i*17)%1001-500 for i in range(1001)];q,r=divmod(n,1001);s=q*sum(period)+sum(period[:r]);ss=q*sum(k*k for k in period)+sum(k*k for k in period[:r]);return step*s/n,math.sqrt(step*step*ss/n)
with tempfile.TemporaryDirectory() as td:
 exe=pathlib.Path(td)/'candidate';subprocess.run(['g++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True)
 def run(args,measure=False):
  if measure:
   code='import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True);sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);sys.exit(p.returncode)'
   t=time.monotonic();p=subprocess.run(['python3','-B','-c',code,str(exe),*map(str,args)],capture_output=True,text=True,check=True,timeout=4);return list(map(float,p.stdout.split('CHILD_RSS_KIB')[0].split())),int(p.stdout.split('CHILD_RSS_KIB')[-1].strip()),time.monotonic()-t
  p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,check=True,timeout=4);return list(map(float,p.stdout.split()))
 checks={};obs={}
 for n,o,step in [(257,'1000000000000','.25'),(1501,'10000000000000000','.001'),(1001,'-10000000000000000','.0003'),(701,'1e20','.001')]:
  v=run([n,o,step]);ref=expected(n,float(step));checks[f'decimal_oracle_n{n}']=len(v)==2 and abs(v[0]-ref[0])<=1e-4 and abs(v[1]-ref[1])<=1e-4;obs[f'decimal_n{n}']=v
 n=1501;ref=expected(n,.001);v=run([n,'10000000000000000','.001','--minimum-precision']);checks['minimum_precision_override']=len(v)==2 and abs(v[0]-ref[0])<=1e-8 and abs(v[1]-ref[1])<=1e-8
 n=2000;ref=expected(n,1);v=run([n,'9007199254740993','3','--ticks']);ref=expected(n,3);checks['exact_integer_ticks_above_2pow53_nonunit_step']=len(v)==2 and abs(v[0]-ref[0])<=1e-12 and abs(v[1]-ref[1])<=1e-12
 large,peak,elapsed=run([3200000,'1000000000000','.25'],True);ref=expected(3200000,.25);checks['required_batch_output']=len(large)==2 and abs(large[0]-ref[0])<=1e-4 and abs(large[1]-ref[1])<=1e-4;checks['required_batch_memory_and_deadline']=peak<=20480 and elapsed<=4;obs.update({'large_output':large,'large_reference':ref,'peak_rss_kib':peak,'elapsed_s':round(elapsed,4)})
 ok=all(checks.values());print(json.dumps({'passed':ok,'checks':checks,'observations':obs}));raise SystemExit(0 if ok else 1)
