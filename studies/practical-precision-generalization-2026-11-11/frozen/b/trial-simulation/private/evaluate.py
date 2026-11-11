import json,pathlib,subprocess,sys,tempfile,time,math
src=pathlib.Path(sys.argv[1]).resolve()/'core.cpp'
MASK=(1<<64)-1
def h(x):
 x^=x>>30;x=(x*0xbf58476d1ce4e5b9)&MASK;x^=x>>27;x=(x*0x94d049bb133111eb)&MASK;x^=x>>31;return x
def force(t):
 x=((t+1)*2862933555777941757+3037000493)&MASK;x^=x>>31;x=(x*0x9e3779b97f4a7c15)&MASK;x^=x>>27;return ((x%200001)-100000)*.00001
def oracle(trials,steps,seed):
 decay=.9999;common=0.0;weight=1.0
 for t in range(steps):common=decay*common+force(t);weight*=decay
 gain=(1-weight)/(1-decay);mean=0.0;m2=0.0
 for tr in range(trials):
  z=h((seed+tr*0x9e3779b97f4a7c15)&MASK);initial=((z%20001)-10000)*.0001;bias=(((z>>20)%2001)-1000)*.0000002
  state=weight*initial+common+bias*gain;d=state-mean;mean+=d/(tr+1);m2+=d*(state-mean)
 return mean,m2/trials
with tempfile.TemporaryDirectory() as td:
 exe=pathlib.Path(td)/'candidate';subprocess.run(['g++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True)
 checks={};obs={}
 for tr,steps,seed,tol in [(80,160,71,1e-10),(1,1,(1<<63)+17,1e-9),(17,1,(1<<64)-9,1e-9),(1300,257,0x12345678,1e-9),(120000,1024,71,1e-8)]:
  t=time.monotonic();p=subprocess.run([str(exe),str(tr),str(steps),str(seed)],capture_output=True,text=True,check=True,timeout=4);elapsed=time.monotonic()-t;v=list(map(float,p.stdout.split()));ref=oracle(tr,steps,seed)
  quality=len(v)==2 and all(math.isfinite(x) for x in v) and abs(v[0]-ref[0])<=tol and abs(v[1]-ref[1])<=tol
  capacity=(tr!=120000 or elapsed<=.18);checks[f'oracle_all_{tr}_trials_{steps}_steps']=quality;checks[f'time_{tr}x{steps}'] = capacity;obs[f'{tr}x{steps}']={'values':v,'reference':ref,'elapsed_s':round(elapsed,5)}
 ok=all(checks.values());print(json.dumps({'passed':ok,'checks':checks,'observations':obs}));raise SystemExit(0 if ok else 1)
