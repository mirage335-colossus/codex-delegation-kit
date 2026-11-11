import json
import math
import pathlib
import struct
import subprocess
import sys
import tempfile
import time

root=pathlib.Path(__file__).resolve().parents[1]
source=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/"core.cpp"
def f32(x):return struct.unpack("f",struct.pack("f",x))[0]
def measurement(i,seed):
    if i%65536==0:return 0.0
    if i%65536==1:return 1.0
    a=(i*1664525+seed*1013904223)&0xffffffff
    a^=a>>16;a=(a*2246822519)&0xffffffff;a^=a>>13;a=(a*3266489917)&0xffffffff;a^=a>>16
    code=256+(a%65280);fraction=f32(((a>>16)&0xffff)/65536.0)
    raw=f32(f32(f32(code)+fraction)/65535.0)
    return min(1.0,raw)
def response(x):return -math.log1p(-0.97*x)/0.85+0.20*math.log1p(0.30*x)+0.03+0.02*x*x
def reference(w,h,seed):
    n=w*h;values=[response(measurement(i,seed)) for i in range(n)]
    bins=[[0.,0.,0] for _ in range(32)]
    for i,q in enumerate(values):
        b=bins[i%32];b[0]+=q;b[1]+=q*q;b[2]+=int(q>=3.8)
    ids=[0,1,n//7,n//3,n//2,(2*n)//3,n-2 if n>1 else 0,n-1]
    return [values[i] for i in ids],bins
flags=["c++","-O3","-std=c++17","-DNDEBUG","-march=native"]
cases=[(101,53,13),(2,1,7),(63,37,91)]
with tempfile.TemporaryDirectory() as d:
    exe=pathlib.Path(d)/"curve-processing"
    subprocess.run(flags+[str(source),"-o",str(exe)],check=True)
    for w,h,seed in cases:
        expected,bins=reference(w,h,seed)
        start=time.perf_counter();proc=subprocess.run([str(exe),str(w),str(h),str(seed)],capture_output=True,text=True,check=True);elapsed=time.perf_counter()-start
        data=json.loads(proc.stdout)
        assert len(data["samples"])==8 and len(data["checksums"])==32
        assert all(math.isfinite(v) for v in data["samples"])
        assert all(len(row)==3 and all(math.isfinite(v) for v in row) for row in data["checksums"])
        assert max(abs(a-b) for a,b in zip(data["samples"],expected))<=2e-5
        for b in range(32):
            count=max(0,(w*h+31-b)//32)
            if count:
                assert abs(data["checksums"][b][0]-bins[b][0])/count<=2e-5
                assert abs(data["checksums"][b][1]-bins[b][1])/count<=2e-5
                assert abs(data["checksums"][b][2]-bins[b][2])<=4
            else:assert data["checksums"][b]==[0,0,0]
    w,h,seed=101,53,13;expected,bins=reference(w,h,seed)
    proc=subprocess.run([str(exe),str(w),str(h),str(seed),"--audit"],capture_output=True,text=True,check=True)
    data=json.loads(proc.stdout)
    assert max(abs(a-b) for a,b in zip(data["samples"],expected))<=1e-12
    for b in range(32):
        count=max(0,(w*h+31-b)//32)
        if count:
            assert abs(data["checksums"][b][0]-bins[b][0])/count<=1e-10
            assert abs(data["checksums"][b][1]-bins[b][1])/count<=1e-10
            assert data["checksums"][b][2]==bins[b][2]
        else:assert data["checksums"][b]==[0,0,0]
print(json.dumps({"public_smoke":"PASS","varied_shapes":len(cases),"high_accuracy_audit":"PASS","complete_output_buckets":32}))
