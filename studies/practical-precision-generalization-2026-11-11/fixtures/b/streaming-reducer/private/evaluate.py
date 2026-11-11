import json,pathlib,subprocess,sys,tempfile,time,math
src=pathlib.Path(sys.argv[1]).resolve()/'core.cpp'
def sample(i,c):
 x=((i+1)*6364136223846793005+(c+7)*1442695040888963407)&((1<<64)-1);x^=x>>29;x=(x*0x9e3779b97f4a7c15)&((1<<64)-1);x^=x>>32;return ((x%200001)-100000)*.01
def oracle(n,w):
 sums=[0.0]*8;out=[0.0]*8;ring=[[0.0]*8 for _ in range(w)]
 for i in range(n):
  k=i%w
  if i>=w:
   for c in range(8):sums[c]-=ring[k][c]
  for c in range(8):v=sample(i,c);ring[k][c]=v;sums[c]+=v
  if i+1>=w:
   for c in range(8):out[c]+=sums[c]/w
 return out
def run(exe,n,w,timeout=4):
 code='import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True);sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);sys.exit(p.returncode)'
 t=time.monotonic();p=subprocess.run(['python3','-B','-c',code,str(exe),str(n),str(w)],capture_output=True,text=True,check=True,timeout=timeout);return list(map(float,p.stdout.split('CHILD_RSS_KIB')[0].split())),int(p.stdout.split('CHILD_RSS_KIB')[-1].strip()),time.monotonic()-t
with tempfile.TemporaryDirectory() as td:
 exe=pathlib.Path(td)/'candidate';subprocess.run(['g++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True)
 shapes=[(40,7),(1000,127),(600000,256)];results=[];ok=True
 for n,w in shapes:
  try:out,rss,elapsed=run(exe,n,w);ref=oracle(n,w);quality=len(out)==8 and all(math.isfinite(a) and abs(a-b)<=max(.02,2e-7*abs(b)) for a,b in zip(out,ref));capacity=(n!=600000 or (rss<=24576 and elapsed<=4));ok &= quality and capacity;results.append({'n':n,'w':w,'quality':quality,'rss_kib':rss,'elapsed_s':round(elapsed,4),'capacity':capacity})
  except Exception as e:ok=False;results.append({'n':n,'w':w,'error':str(e)})
 print(json.dumps({'passed':ok,'checks':{'independent_oracle_all_shapes':all(x.get('quality',False) for x in results),'required_capture_resource_envelope':len(results)==3 and results[-1].get('capacity',False)},'observations':results}));raise SystemExit(0 if ok else 1)
