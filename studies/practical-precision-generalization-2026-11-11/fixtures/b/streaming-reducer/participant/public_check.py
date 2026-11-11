import pathlib,subprocess,time,math,tempfile
root=pathlib.Path(__file__).resolve().parent
subprocess.run(['g++','-O2','-std=c++17','core.cpp','-o','probe'],cwd=root,check=True)
def sample(i,c):
 x=((i+1)*6364136223846793005+(c+7)*1442695040888963407)&((1<<64)-1);x^=x>>29;x=(x*0x9e3779b97f4a7c15)&((1<<64)-1);x^=x>>32;return ((x%200001)-100000)*.01
def oracle(n,w):
 sums=[0.0]*8; out=[0.0]*8; ring=[[0.0]*8 for _ in range(w)]
 for i in range(n):
  slot=i%w
  if i>=w:
   for c in range(8):sums[c]-=ring[slot][c]
  for c in range(8):
   v=sample(i,c);ring[slot][c]=v;sums[c]+=v
  if i+1>=w:
   for c in range(8):out[c]+=sums[c]/w
 return out
def run(n,w):
 code='import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True);sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss);sys.exit(p.returncode)'
 t=time.monotonic();p=subprocess.run(['python3','-B','-c',code,str(root/'probe'),str(n),str(w)],cwd=root,text=True,capture_output=True,check=True,timeout=4);elapsed=time.monotonic()-t
 peak=int(p.stdout.split('CHILD_RSS_KIB')[-1].strip());return peak,elapsed
for n,w in [(40,7),(1000,127)]:
 p=subprocess.run([str(root/'probe'),str(n),str(w)],cwd=root,text=True,capture_output=True,check=True);out=list(map(float,p.stdout.split()));ref=oracle(n,w)
 assert len(out)==8 and all(abs(a-b)<=max(.02,2e-7*abs(b)) for a,b in zip(out,ref)),(out,ref)
peak,elapsed=run(600000,256);assert peak<=24576,f'peak {peak} KiB exceeds 24 MiB';assert elapsed<=4,f'capture took {elapsed:.3f}s'
print(f'PASS output oracle (3 shapes); peak={peak} KiB elapsed={elapsed:.3f}s')
