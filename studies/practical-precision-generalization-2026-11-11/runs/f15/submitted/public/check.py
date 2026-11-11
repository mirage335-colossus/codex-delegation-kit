import json,math,pathlib,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'core.cpp';w,h,steps,seed=96,72,12,31;a=[0.]*(w*h)
for y in range(h):
 for x in range(w):a[y*w+x]=.125 if x==0 or y==0 or x==w-1 or y==h-1 else (1. if (x*17+y*29+seed*13)%97==0 else 0.)
for _ in range(steps):
 b=a.copy()
 for y in range(1,h-1):
  q=y*w
  for x in range(1,w-1):i=q+x;b[i]=.25*(a[i-1]+a[i+1]+a[i-w]+a[i+w])
 a=b
ids=[0,w-1,(h//3)*w+w//4,(h//2)*w+w//2,(h-2)*w+w//2,w*h-1];ref=[a[i] for i in ids];bins=[[0.,0.] for _ in range(16)]
for i,v in enumerate(a):bins[i%16][0]+=v;bins[i%16][1]+=v*v
with tempfile.TemporaryDirectory() as d:
 exe=pathlib.Path(d)/'probe';subprocess.run(['c++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True);x=json.loads(subprocess.run([str(exe),str(w),str(h),str(steps),str(seed)],capture_output=True,text=True,check=True).stdout)
 assert len(x['samples'])==6 and len(x['checksums'])==16 and all(math.isfinite(v) for v in x['samples']) and all(math.isfinite(v) for row in x['checksums'] for v in row)
 err=max(abs(a-b) for a,b in zip(x['samples'],ref));c=max(abs(x['checksums'][b][j]-bins[b][j])/((w*h+15-b)//16) for b in range(16) for j in range(2));assert err<=3e-4 and c<=9e-4
 print(json.dumps({'public_smoke':'PASS','full_output_checksum_error_per_element':c,'max_sample_error':err,'storage_bytes_reported':x['storage_bytes']}))
