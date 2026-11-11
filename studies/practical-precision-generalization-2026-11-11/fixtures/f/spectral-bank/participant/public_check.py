#!/usr/bin/env python3
import math,pathlib,subprocess,tempfile
p=pathlib.Path(__file__).resolve().parent
def values(exe,args):
    r=subprocess.run([str(exe),*map(str,args)],text=True,capture_output=True,check=True)
    header,raw=r.stdout.split('values=',1)
    h=dict(item.split('=',1) for item in header.split() if '=' in item)
    return h,[float(x) for x in raw.strip().rstrip(',').split(',') if x]
def reference(n):
    tau=2*math.pi
    frame=[]
    for i in range(n):
        x=0.55*math.sin(tau*i*3/n)+0.22*math.cos(tau*i*17/n)+0.001*(int((i*17)%101)-50)
        frame.append(x*(0.5-0.5*math.cos(tau*i/(n-1))))
    out=[]
    for k in range(n//2+1):
        re=sum(x*math.cos(-tau*k*i/n) for i,x in enumerate(frame))
        im=sum(x*math.sin(-tau*k*i/n) for i,x in enumerate(frame))
        out.append(re*re+im*im)
    return out
with tempfile.TemporaryDirectory(prefix='.public-check-',dir=p) as td:
    exe=pathlib.Path(td)/'spectral-bank'
    subprocess.run([str(p/'build.sh'),str(exe)],check=True)
    h,bins=values(exe,['8','2','128'])
    assert h.get('outputs')=='1040' and len(bins)==1040 and all(math.isfinite(x) for x in bins)
    hs,small=values(exe,['1','1','16'])
    expected=reference(16)
    assert hs.get('outputs')=='9' and len(small)==9 and all(math.isfinite(x) for x in small)
    assert all(abs(x-y)<=0.001+0.00001*abs(y) for x,y in zip(small,expected))
    print(f"ordinary_outputs={len(bins)} small_reference_bins={len(small)} all_finite=true")
