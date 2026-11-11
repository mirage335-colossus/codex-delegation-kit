import json, math, subprocess, sys

def reference(ch,n,taps,seed):
    h=[]; hs=0.0
    for k in range(taps):
        z=(k-(taps-1)*.5)/(taps*.5)
        v=(.5+.5*math.cos(math.pi*z))*math.cos(.23*k)
        h.append(v); hs+=abs(v)
    h=[v/hs for v in h]
    bins=[[0.,0.] for _ in range(16)]
    samples=[]; ids={0,n//11,n//3,n//2,n-1,(ch-1)*n+n//4}
    for c in range(ch):
        for i in range(n):
            a=0.0
            for k,v in enumerate(h):
                q=i+k-taps//2
                if 0<=q<n:
                    x=math.sin((q+seed*7+c*13)*.017)+.35*math.cos((q*3+seed+c*5)*.009)
                    a+=x*v
            j=c*n+i; b=bins[j%16]; b[0]+=a; b[1]+=a*a
            if j in ids: samples.append((j,a))
    samples=[v for j,v in sorted(samples)]
    return samples,bins

def run(exe,ch,n,taps,seed):
    return json.loads(subprocess.run([exe,str(ch),str(n),str(taps),str(seed)],capture_output=True,text=True,check=True).stdout)

for exe,args,strict in [('/tmp/precision-generalization-runs/d05/high',(3,1024,31,9),True),('/tmp/precision-generalization-runs/d05/default',(8,32768,127,9),False)]:
    expected_s,expected_b=reference(*args); actual=run(exe,*args)
    se=max(abs(x-y) for x,y in zip(expected_s,actual['samples']))
    ce=max(abs(actual['checksums'][b][j]-expected_b[b][j])/((args[0]*args[1]+15-b)//16) for b in range(16) for j in range(2))
    print(json.dumps({'exe':exe.rsplit('/',1)[-1],'samples_max_abs':se,'checksum_max_abs_per_element':ce,'storage_bytes':actual['storage_bytes'],'thresholds':{'sample':2e-9 if strict else 2e-5,'checksum_per_element':2e-8 if strict else 'public-smoke-6e-5'}}))
    assert se <= (2e-9 if strict else 2e-5)
    if strict: assert ce <= 2e-8
