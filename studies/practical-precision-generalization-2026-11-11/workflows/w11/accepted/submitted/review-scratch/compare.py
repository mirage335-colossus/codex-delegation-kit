import json, subprocess, time, statistics
from pathlib import Path
root=Path(__file__).resolve().parent
records={}
def run(name,args):
 t=time.perf_counter(); p=subprocess.run([str(root/name),*map(str,args)],check=True,capture_output=True,text=True); elapsed=time.perf_counter()-t
 return json.loads(p.stdout),elapsed
def compare(a,b,n):
 return {'sample_max':max(abs(x-y) for x,y in zip(a['samples'],b['samples'])), 'mean_max':max(abs(a['checksums'][i][0]-b['checksums'][i][0])/max(1,(n+31-i)//32) for i in range(32)), 'square_mean_max':max(abs(a['checksums'][i][1]-b['checksums'][i][1])/max(1,(n+31-i)//32) for i in range(32)), 'count_max':max(abs(a['checksums'][i][2]-b['checksums'][i][2]) for i in range(32))}
for args in [(4096,2048,13),(8192,8192,91),(1,1,13)]:
 audit,dt=run('current',(*args,'--audit'))
 result={'audit_seconds':dt}
 for name in ['current','float-bins','no-guard']:
  out,dt=run(name,args); result[name]={'seconds':dt,**compare(out,audit,args[0]*args[1]),'storage_bytes':out['storage_bytes']}
 records[str(args)]=result
benchmark={name:[] for name in ['current','no-guard']}
for k in range(9):
 for name in (['current','no-guard'] if k%2==0 else ['no-guard','current']):
  out,dt=run(name,[]);benchmark[name].append(dt)
records['default_benchmark']={name:{'times':times,'median':statistics.median(times)} for name,times in benchmark.items()}
(root/'comparison.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
