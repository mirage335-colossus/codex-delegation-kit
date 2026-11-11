#!/usr/bin/env python3
"""Check complete dispatch outputs, actual heap use and deny-only fallback."""
import json,pathlib,re,subprocess,sys,tempfile
HERE=pathlib.Path(__file__).resolve().parent; WITNESS=HERE/'witness'/'core.cpp'; LIMIT=72*1024*1024
def compile(src,out): subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-pedantic',str(src),str(HERE/'heap_probe.cpp'),'-o',str(out)],check=True,capture_output=True,text=True)
def run(exe,args):
    p=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,timeout=12)
    if p.returncode: raise RuntimeError(f'exit {p.returncode}: {p.stderr[-250:]}')
    d=dict(re.findall(r'([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)',p.stdout));m=re.search(r'heap_peak_bytes=(\d+)',p.stderr)
    if not m:raise RuntimeError('allocation probe emitted no peak')
    d['heap_peak_bytes']=int(m.group(1));return d
def main(participant):
    checks=[];obs=[]
    with tempfile.TemporaryDirectory(prefix='dispatch-eval-') as td:
        cand=pathlib.Path(td)/'candidate';ref=pathlib.Path(td)/'witness';caps=pathlib.Path(td)/'caps'
        compile(pathlib.Path(participant)/'core.cpp',cand);compile(WITNESS,ref)
        subprocess.run(['g++','-O2','-std=c++17',str(HERE/'capability_probe.cpp'),'-o',str(caps)],check=True,capture_output=True,text=True)
        host=subprocess.check_output([str(caps)],text=True); supported='avx2=true' in host
        for n in (1027,500000,3700000,10000000):
            c=run(cand,[n]);r=run(ref,[n,'--deny-avx2'])
            try: quality=(int(c['outputs'])==n and abs(float(c['checksum'])-float(r['checksum']))<=0.01+0.00001*abs(float(r['checksum'])) and abs(float(c['weighted'])-float(r['weighted']))<=0.01+0.00001*abs(float(r['weighted'])))
            except (KeyError,ValueError):quality=False
            memory=c['heap_peak_bytes']<=LIMIT
            report=bool(c.get('storage')) and c.get('compute')=='fp32' and c.get('accumulator')=='fp64' and c.get('gpu_backend')=='absent'
            checks += [{'case':str(n),'check':'complete sample count and both reference totals','passed':quality},
                       {'case':str(n),'check':'measured live heap <= 72 MiB','passed':memory},
                       {'case':str(n),'check':'format and unavailable-backend report fields','passed':report}]
            obs.append({'samples':n,'outputs':c.get('outputs'),'checksum':c.get('checksum'),'weighted':c.get('weighted'),'seconds':c.get('seconds'),
                        'heap_peak_bytes':c['heap_peak_bytes'],'reported_buffer_bytes':c.get('buffer_bytes'),'selected':c.get('selected'),
                        'cpu_avx2_reported':c.get('cpu_avx2'),'independent_cpu_avx2':supported,'gpu_backend':c.get('gpu_backend')})
        normal=run(cand,['500000']);denied=run(cand,['10000000','--deny-avx2']);expected=run(ref,['10000000','--deny-avx2'])
        try: denied_ok=(int(denied['outputs'])==10000000 and denied['heap_peak_bytes']<=LIMIT and abs(float(denied['checksum'])-float(expected['checksum']))<=0.01+0.00001*abs(float(expected['checksum'])) and abs(float(denied['weighted'])-float(expected['weighted']))<=0.01+0.00001*abs(float(expected['weighted'])))
        except (KeyError,ValueError):denied_ok=False
        checks.append({'case':'deny-only fallback','check':'portable path computes the same complete output as reference','passed':denied_ok})
        expected='avx2' if supported else 'portable'
        branch=(normal.get('selected')==expected and denied.get('selected')=='portable' and normal.get('cpu_avx2')==('true' if supported else 'false') and denied.get('cpu_avx2')==('true' if supported else 'false') and normal.get('gpu_backend')=='absent')
        checks.append({'case':'capability selection','check':'native support and deny-only fallback reporting agrees with independent probe','passed':branch})
        assembly=subprocess.check_output(['objdump','-d',str(cand)],text=True).lower()
        obs.append({'binary_instruction_evidence':{'vcvtdq2ps': 'vcvtdq2ps' in assembly, 'vmulps':'vmulps' in assembly}, 'scope':'diagnostic only; guarded reachable path and equivalent instructions require source review'})

    out={'passed':all(x['passed'] for x in checks),'checks':checks,'observations':obs};print(json.dumps(out,sort_keys=True));return 0 if out['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main(pathlib.Path(sys.argv[1]).resolve()))
    except Exception as e:print(json.dumps({'passed':False,'checks':[{'case':'setup/runtime','check':str(e),'passed':False}],'observations':[]}));sys.exit(2)
