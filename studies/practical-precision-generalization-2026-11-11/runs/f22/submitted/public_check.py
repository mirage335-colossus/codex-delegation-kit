import pathlib,subprocess,time,math
root=pathlib.Path(__file__).resolve().parent
subprocess.run(['g++','-O2','-std=c++17','core.cpp','-o','probe'],cwd=root,check=True)
def run(args):
 t=time.monotonic();p=subprocess.run([str(root/'probe'),*map(str,args)],cwd=root,text=True,capture_output=True,check=True,timeout=4);return list(map(float,p.stdout.split())),time.monotonic()-t
def h(x):
 x^=x>>30;x=(x*0xbf58476d1ce4e5b9)&((1<<64)-1);x^=x>>27;x=(x*0x94d049bb133111eb)&((1<<64)-1);x^=x>>31;return x
def force(t):
 x=((t+1)*2862933555777941757+3037000493)&((1<<64)-1);x^=x>>31;x=(x*0x9e3779b97f4a7c15)&((1<<64)-1);x^=x>>27;return ((x%200001)-100000)*.00001
vals=[]
for tr in range(80):
 z=h((71+tr*0x9e3779b97f4a7c15)&((1<<64)-1));s=((z%20001)-10000)*.0001;b=(((z>>20)%2001)-1000)*.0000002
 for t in range(160):s=.9999*s+force(t)+b
 vals.append(s)
mean=sum(vals)/len(vals);var=sum((x-mean)**2 for x in vals)/len(vals)
out,_=run([80,160,71]);assert abs(out[0]-mean)<1e-10 and abs(out[1]-var)<1e-10,(out,mean,var)
large,elapsed=run([120000,1024,71]);assert len(large)==2 and all(math.isfinite(x) for x in large) and elapsed<=0.18,f'large probe {elapsed:.3f}s'
print(f'PASS small mean={out[0]:.10g} variance={out[1]:.10g}; large elapsed={elapsed:.3f}s')
