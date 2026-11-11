#!/usr/bin/env python3
"""Check all scene frame energies against the wide witness and measure live heap."""
import json, pathlib, re, subprocess, sys, tempfile
HERE=pathlib.Path(__file__).resolve().parent; WITNESS=HERE/'witness'/'core.cpp'; LIMIT=4*1024*1024
def compile(src,out): subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-pedantic',str(src),str(HERE/'heap_probe.cpp'),'-o',str(out)],check=True,capture_output=True,text=True)
def run(exe,args):
    p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,timeout=10)
    if p.returncode: raise RuntimeError(f'exit {p.returncode}: {p.stderr[-250:]}')
    d=dict(re.findall(r'([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)',p.stdout)); m=re.search(r'heap_peak_bytes=(\d+)',p.stderr)
    if not m: raise RuntimeError('allocation probe emitted no peak')
    d['heap_peak_bytes']=int(m.group(1)); return d
def compare(c,r,count):
    try: a=[float(c[f'frame{i}']) for i in range(count+1)]; b=[float(r[f'frame{i}']) for i in range(count+1)]
    except (KeyError,ValueError): return False
    return c.get('outputs')==str(count+1) and all(abs(x-y)<=0.02+0.00005*abs(y) for x,y in zip(a,b))
def main(participant):
    checks=[]; obs=[]
    with tempfile.TemporaryDirectory(prefix='scene-eval-') as td:
        cand=pathlib.Path(td)/'candidate'; ref=pathlib.Path(td)/'witness'; compile(pathlib.Path(participant)/'core.cpp',cand);compile(WITNESS,ref)
        cases=[(12,320,180,1280,720,8),(5,400,200,960,840,14),(0,320,180,960,840,12)]
        for args in cases:
            c=run(cand,args); r=run(ref,[*args,'double'])
            quality=compare(c,r,args[0]); memory=c['heap_peak_bytes']<=LIMIT
            label='x'.join(map(str,args))
            checks += [{'case':label,'check':'every frame energy and count','passed':quality},
                       {'case':label,'check':'measured live heap <= 4 MiB','passed':memory}]
            obs.append({'case':label,'outputs':c.get('outputs'),'checksum':c.get('checksum'),'seconds':c.get('seconds'),
                        'measured_heap_peak_bytes':c['heap_peak_bytes'],'reported_buffer_bytes':c.get('buffer_bytes'),
                        'reference_checksum':r.get('checksum')})
        f=run(cand,[5,400,200,960,840,14,'float']); d=run(cand,[5,400,200,960,840,14,'double'])
        checks.append({'case':'explicit diagnostic modes','check':'float selection uses less measured live heap than double','passed':f['heap_peak_bytes']<d['heap_peak_bytes']})
    out={'passed':all(x['passed'] for x in checks),'checks':checks,'observations':obs};print(json.dumps(out,sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':
    try: sys.exit(main(pathlib.Path(sys.argv[1]).resolve()))
    except Exception as e: print(json.dumps({'passed':False,'checks':[{'case':'setup/runtime','check':str(e),'passed':False}],'observations':[]}));sys.exit(2)
