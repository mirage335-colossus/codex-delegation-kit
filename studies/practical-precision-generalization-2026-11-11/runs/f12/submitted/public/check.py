import json,math,pathlib,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'core.cpp';ch,n,taps,seed=3,1024,31,9;h=[];hs=0.
for k in range(taps):
 z=(k-(taps-1)*.5)/(taps*.5);v=(.5+.5*math.cos(math.pi*z))*math.cos(.23*k);h.append(v);hs+=abs(v)
h=[v/hs for v in h];r=taps//2;ids=[0,n//11,n//3,n//2,n-1,(ch-1)*n+n//4];samples=[];bins=[[0.,0.] for _ in range(16)]
for c in range(ch):
 for i in range(n):
  acc=0.
  for k in range(taps):
   q=i+k-r
   if 0<=q<n:acc+=(math.sin((q+seed*7+c*13)*.017)+.35*math.cos((q*3+seed+c*5)*.009))*h[k]
  b=(c*n+i)%16;bins[b][0]+=acc;bins[b][1]+=acc*acc
  if c*n+i in ids:samples.append(acc)
with tempfile.TemporaryDirectory() as d:
 exe=pathlib.Path(d)/'probe';subprocess.run(['c++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True);x=json.loads(subprocess.run([str(exe),str(ch),str(n),str(taps),str(seed)],capture_output=True,text=True,check=True).stdout)
 assert len(x['samples'])==6 and len(x['checksums'])==16 and all(math.isfinite(v) for v in x['samples']) and all(math.isfinite(v) for row in x['checksums'] for v in row)
 err=max(abs(a-b) for a,b in zip(x['samples'],samples));c=max(abs(x['checksums'][b][j]-bins[b][j])/((ch*n+15-b)//16) for b in range(16) for j in range(2));assert err<=2e-5 and c<=6e-5
 print(json.dumps({'public_smoke':'PASS','full_output_checksum_error_per_element':c,'max_sample_error':err,'storage_bytes_reported':x['storage_bytes']}))
