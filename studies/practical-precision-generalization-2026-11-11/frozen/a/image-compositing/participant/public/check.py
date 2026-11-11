import json,math,pathlib,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'core.cpp'
w,h,seed=160,90,17;n=w*h;ids=[0,n//7,n//2,(n*5)//7,n-1];samples=[];bins=[[0.,0.] for _ in range(16)]
for p in range(n):
 k=(p*1664525+seed*1013904223)&0xffffffff;bg=[((k>>3)&1023)/1023.,((k>>13)&1023)/1023.,((k>>23)&255)/255.];fg=[((k>>7)&511)/511.,((k>>17)&511)/511.,((k>>27)&31)/31.];a=((k>>10)&255)/255.;vals=[fg[c]*a+bg[c]*(1-a) for c in range(3)]+[1.]
 for c,v in enumerate(vals):b=(4*p+c)%16;bins[b][0]+=v;bins[b][1]+=v*v
 if p in ids:samples.append(vals)
with tempfile.TemporaryDirectory() as d:
 exe=pathlib.Path(d)/'probe';subprocess.run(['c++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True);x=json.loads(subprocess.run([str(exe),str(w),str(h),str(seed)],capture_output=True,text=True,check=True).stdout)
 assert x['storage_bytes']<=110*1024*1024 and len(x['samples'])==5 and all(len(v)==4 for v in x['samples']) and len(x['checksums'])==16
 assert all(math.isfinite(v) for row in x['samples'] for v in row) and all(math.isfinite(v) for row in x['checksums'] for v in row)
 err=max(abs(a-b) for row,ref in zip(x['samples'],samples) for a,b in zip(row,ref));assert all(abs(row[3]-1)<=1e-7 for row in x['samples']);assert err<=2e-5
 c=max(abs(x['checksums'][b][j]-bins[b][j])/((4*n+15-b)//16) for b in range(16) for j in range(2));assert c<=6e-5
 print(json.dumps({'public_smoke':'PASS','full_output_checksum_error_per_element':c,'max_sample_error':err,'storage_bytes_reported':x['storage_bytes']}))
