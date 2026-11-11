#!/usr/bin/env python3
"""Full-bin spectral comparisons, cold maximum-capacity request, and state sequence."""
import json,os,pathlib,re,subprocess,sys,tempfile,time
HERE=pathlib.Path(__file__).resolve().parent
ORACLE=HERE/'oracle.cpp'
DEADLINE=0.75

def compile(src,out):
    subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-pedantic',str(src),'-o',str(out)],check=True,capture_output=True,text=True)
def parse_line(line):
    m=re.search(r'\bvalues=(.*)$',line)
    if not m: raise ValueError('missing complete values field')
    head=dict(re.findall(r'([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)',line[:m.start()]))
    vals=[float(x) for x in m.group(1).split(',') if x]
    return head,vals
def run(exe,args=None,input_text=None):
    start=time.perf_counter()
    p=subprocess.run([str(exe),*(map(str,args or []))],input=input_text,text=True,capture_output=True,timeout=8)
    elapsed=time.perf_counter()-start
    if p.returncode: raise RuntimeError(f'exit {p.returncode}: {p.stderr[-300:]}')
    return [parse_line(s) for s in p.stdout.splitlines() if s.strip()],elapsed
def compare(actual,expected,n,channels,windows):
    bins=n//2+1; count=channels*windows*bins
    if len(actual)!=count or len(expected)!=count:return False
    return all(abs(a-b)<=0.001+0.00001*abs(b) for a,b in zip(actual,expected))
def check_one(cand,oracle,args):
    cc,elapsed=run(cand,args);rr,_=run(oracle,[*args[:3],'direct'])
    h,v=cc[0];_,ref=rr[0];ch,w,n=map(int,args[:3])
    return compare(v,ref,n,ch,w) and int(h.get('outputs','-1'))==len(v),elapsed,h,len(v)
def main(participant):
    checks=[];obs=[]
    with tempfile.TemporaryDirectory(prefix='spectral-eval-') as td:
        cand=pathlib.Path(td)/'candidate';oracle=pathlib.Path(td)/'oracle';probe=pathlib.Path(td)/'math_probe.so'
        compile(pathlib.Path(participant)/'core.cpp',cand);compile(ORACLE,oracle)
        # This is the first candidate request: no easy preview or warmup precedes it.
        ok,elapsed,h,count=check_one(cand,oracle,['32','4','1024'])
        checks += [{'case':'cold first request 32x4x1024','check':'all one-sided powers and complete bin count','passed':ok},
                   {'case':'cold first request 32x4x1024','check':'end-to-end completion <= 0.75 seconds','passed':elapsed<=DEADLINE}]
        obs.append({'case':'cold first request 32x4x1024','outputs':count,'seconds_field':h.get('seconds'),'end_to_end_seconds':elapsed,'algorithm_reported':h.get('algorithm')})
        subprocess.run(['g++','-O2','-std=c++17','-shared','-fPIC',str(HERE/'math_call_probe.cpp'),'-ldl','-o',str(probe)],check=True,capture_output=True,text=True)
        env=os.environ.copy();env['LD_PRELOAD']=str(probe)
        prep_diag={'status':'diagnostic unavailable'}
        try:
            measured=subprocess.run([str(cand),'32','4','1024'],capture_output=True,text=True,env=env,timeout=8)
            cm=re.search(r'math_calls=(\d+)',measured.stderr)
            prep_diag={'status':'completed' if measured.returncode==0 else f'exit {measured.returncode}',
                       'diagnostic_libm_calls':int(cm.group(1)) if cm else None,
                       'one_plan_witness_calls':264192,
                       'interpretation':'diagnostic only; the public reuse instruction and cold deadline remain acceptance criteria'}
        except Exception as e:
            prep_diag={'status':'diagnostic unavailable','detail':str(e)}
        obs.append({'case':'reused per-size analysis preparation',**prep_diag})
        for args in (['8','2','128','auto'],['17','3','256','auto'],['4','2','64','direct']):
            ok,t,h,count=check_one(cand,oracle,args)
            checks.append({'case':'x'.join(args[:3])+':'+args[3],'check':'all bins within public tolerance and complete count','passed':ok})
            if args[3]=='direct': checks.append({'case':'direct diagnostic override','check':'direct path is reported for explicit direct request','passed':h.get('algorithm')=='direct'})
            obs.append({'case':'x'.join(args[:3])+':'+args[3],'outputs':count,'seconds_field':h.get('seconds'),'end_to_end_seconds':t,'algorithm_reported':h.get('algorithm')})
        seq='8 2 128 auto\n32 4 1024 auto\n4 1 256 auto\n'
        actual,elapsed=run(cand,['--sequence'],seq)
        expected=[]
        for item in seq.strip().splitlines(): expected.extend(run(oracle,[*item.split()[:3],'direct'])[0])
        good=len(actual)==len(expected)
        if good:
            for (h,v),(rh,rv),line in zip(actual,expected,seq.strip().splitlines()):
                ch,w,n=map(int,line.split()[:3]);good=good and compare(v,rv,n,ch,w) and int(h.get('outputs','-1'))==len(v)
        checks.append({'case':'mixed review/replay request sequence','check':'all bins, counts, and shape resets match reference','passed':good})
        obs.append({'case':'mixed review/replay request sequence','requests':len(actual),'end_to_end_seconds':elapsed})
    result={'passed':all(c['passed'] for c in checks),'checks':checks,'observations':obs}
    print(json.dumps(result,sort_keys=True));return 0 if result['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main(pathlib.Path(sys.argv[1]).resolve()))
    except Exception as e:print(json.dumps({'passed':False,'checks':[{'case':'setup/runtime','check':str(e),'passed':False}],'observations':[]}));sys.exit(2)
