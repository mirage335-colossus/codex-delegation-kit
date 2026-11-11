import json
import math
import pathlib
import subprocess
import struct
import sys
import tempfile
import time

root=pathlib.Path(__file__).resolve().parents[1]
source=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/"core.cpp"
def pixel_value(x,y,w,h,seed):
    gx=x/max(1,w-1);gy=y/max(1,h-1)
    v=0.16+0.44*gx+0.18*gy+0.05*math.sin(0.025*x+0.13*seed)*math.cos(0.031*y-0.07*seed)
    if ((x+seed*23)%211<5) and ((y+seed*17)%173<4):
        v+=0.24 if ((x//211+y//173+seed)&1) else -0.20
    return struct.unpack("f",struct.pack("f",max(0.02,min(0.95,v))))[0]
def reference(w,h,seed,r):
    n=w*h;scores=[]
    for y in range(h):
        for x in range(w):
            vals=[pixel_value(xx,yy,w,h,seed) for yy in range(max(0,y-r),min(h-1,y+r)+1) for xx in range(max(0,x-r),min(w-1,x+r)+1)]
            mean=sum(vals)/len(vals);variance=max(1e-4,sum(v*v for v in vals)/len(vals)-mean*mean)
            scores.append((pixel_value(x,y,w,h,seed)-mean)/math.sqrt(variance))
    bins=[[0.,0.,0] for _ in range(32)]
    for i,q in enumerate(scores):
        b=bins[i%32];b[0]+=q;b[1]+=q*q;b[2]+=int(abs(q)>=2.5)
    ids=[0,w-1,(h//3)*w+w//5,(h//2)*w+w//2,(h-1)*w,(h//2)*w+w-1,n//2,n-1]
    return [scores[i] for i in ids],bins
flags=["c++","-O3","-std=c++17","-DNDEBUG","-march=native"]
cases=[(47,31,13,12),(19,11,7,15),(29,21,91,0),(1,1,3,15)]
with tempfile.TemporaryDirectory() as d:
    exe=pathlib.Path(d)/"area-inspection"
    subprocess.run(flags+[str(source),"-o",str(exe)],check=True)
    for w,h,seed,r in cases:
        expected,bins=reference(w,h,seed,r)
        start=time.perf_counter();proc=subprocess.run([str(exe),str(w),str(h),str(seed),str(r)],capture_output=True,text=True,check=True);elapsed=time.perf_counter()-start
        data=json.loads(proc.stdout)
        assert len(data["samples"])==8 and len(data["checksums"])==32
        assert all(math.isfinite(v) for v in data["samples"])
        assert all(len(row)==3 and math.isfinite(row[0]) and math.isfinite(row[1]) and math.isfinite(row[2]) for row in data["checksums"])
        assert max(abs(a-b) for a,b in zip(data["samples"],expected))<=0.01
        for b in range(32):
            count=max(0,(w*h+31-b)//32)
            if count:
                assert abs(data["checksums"][b][0]-bins[b][0])/count<=0.001
                assert abs(data["checksums"][b][1]-bins[b][1])/count<=0.001
                assert abs(data["checksums"][b][2]-bins[b][2])<=64
            else:
                assert data["checksums"][b]==[0,0,0]
    w,h,seed,r=47,31,13,12
    expected,bins=reference(w,h,seed,r)
    proc=subprocess.run([str(exe),str(w),str(h),str(seed),str(r),"--audit"],capture_output=True,text=True,check=True)
    data=json.loads(proc.stdout)
    assert len(data["samples"])==8 and len(data["checksums"])==32
    assert max(abs(a-b) for a,b in zip(data["samples"],expected))<=1e-12
    for b in range(32):
        count=max(0,(w*h+31-b)//32)
        if count:
            assert abs(data["checksums"][b][0]-bins[b][0])/count<=1e-10
            assert abs(data["checksums"][b][1]-bins[b][1])/count<=1e-10
            assert abs(data["checksums"][b][2]-bins[b][2])==0
        else:
            assert data["checksums"][b]==[0,0,0]
print(json.dumps({"public_smoke":"PASS","boundary_cases":len(cases),"audit":"PASS","full_output_buckets":32}))
