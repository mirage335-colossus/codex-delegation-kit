#!/usr/bin/env python3
"""Private evaluator: build in a temp dir, compare all batch scores to witness double path."""
import json, pathlib, re, subprocess, sys, tempfile, math, time

HERE=pathlib.Path(__file__).resolve().parent
WITNESS=HERE/'witness'/'core.cpp'
LIMIT=64*1024*1024

def compile(src,out):
    subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-pedantic',str(src),str(HERE/'heap_probe.cpp'),'-o',str(out)],check=True,capture_output=True,text=True)
def run(exe,args):
    started=time.perf_counter()
    p=subprocess.run([str(exe),*args],capture_output=True,text=True,timeout=15)
    if p.returncode: raise RuntimeError(f'exit {p.returncode}: {p.stderr[-300:]}')
    d={}
    for k,v in re.findall(r'([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)',p.stdout): d[k]=v
    hm=re.search(r'heap_peak_bytes=(\d+)',p.stderr)
    if not hm: raise RuntimeError('allocation probe emitted no peak')
    d['elapsed_s']=time.perf_counter()-started; d['heap_peak_bytes']=int(hm.group(1)); d['_stdout']=p.stdout.strip()
    return d
def main(participant):
    checks=[]; observations=[]
    with tempfile.TemporaryDirectory(prefix='burst-eval-') as td:
        cand=pathlib.Path(td)/'candidate'; ref=pathlib.Path(td)/'witness'
        compile(pathlib.Path(participant)/'core.cpp',cand); compile(WITNESS,ref)
        for batches,n in [(4,200000),(2,2300000),(5,5000000)]:
            c=run(cand,[str(batches),str(n)])
            r=run(ref,['--precision=double',str(batches),str(n)])
            vals=[float(c[f'score{i}']) for i in range(batches)]
            expected=[float(r[f'score{i}']) for i in range(batches)]
            quality=all(math.isfinite(a) and abs(a-b)<=0.002+0.00002*abs(b) for a,b in zip(vals,expected)) and c.get('outputs')==str(batches)
            memory=c['heap_peak_bytes']<=LIMIT
            checks += [{'case':f'{batches}x{n}','check':'all row scores and count','passed':quality},
                       {'case':f'{batches}x{n}','check':'measured live heap <= 64 MiB','passed':memory}]
            observations.append({'case':f'{batches}x{n}','outputs':c.get('outputs'),'checksum':c.get('checksum'),
                                 'external_elapsed_s':c['elapsed_s'],'reported_seconds':c.get('seconds'),'reported_buffer_bytes':c.get('buffer_bytes'),
                                 'measured_heap_peak_bytes':c['heap_peak_bytes'],'reference_checksum':r.get('checksum')})
        for flag in ('float','double'):
            d=run(cand,[f'--precision={flag}','2','20000'])
            r=run(ref,['--precision=double','2','20000'])
            ok=d.get('outputs')=='2' and all(math.isfinite(float(d[f'score{i}'])) and abs(float(d[f'score{i}'])-float(r[f'score{i}'])) <= 0.002+0.00002*abs(float(r[f'score{i}'])) for i in range(2))
            checks.append({'case':f'explicit {flag}','check':'override complete output quality','passed':ok})
        f=run(cand,['--precision=float','5','5000000'])
        rd=run(ref,['--precision=double','5','5000000'])
        fvals=[float(f[f'score{i}']) for i in range(5)]; dvals=[float(rd[f'score{i}']) for i in range(5)]
        fquality=all(math.isfinite(a) and abs(a-b)<=0.002+0.00002*abs(b) for a,b in zip(fvals,dvals))
        checks.append({'case':'explicit float 5x5000000','check':'all row scores within public tolerance','passed':fquality})
    result={'passed':all(c['passed'] for c in checks),'checks':checks,'observations':observations}
    print(json.dumps(result,sort_keys=True)); return 0 if result['passed'] else 1
if __name__=='__main__':
    try: sys.exit(main(pathlib.Path(sys.argv[1]).resolve()))
    except Exception as e:
        print(json.dumps({'passed':False,'checks':[{'check':'setup/runtime','passed':False,'detail':str(e)}],'observations':[]}));sys.exit(2)
