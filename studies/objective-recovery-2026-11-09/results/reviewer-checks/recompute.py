import ast,json,statistics
from pathlib import Path
p=Path('/home/user/___quick/p/_cur/codex-delegation-kit/studies/objective-recovery-2026-11-09/freeze/packet')
def union(xs):
 merged=[]
 for a,b in sorted(xs):
  assert b>=a
  if merged and a <= merged[-1][1]: merged[-1][1]=max(b,merged[-1][1])
  else: merged.append([a,b])
 return sum(b-a for a,b in merged)
q=json.loads((p/'abba-oversubscription/qualify.json').read_text())
s=json.loads((p/'abba-oversubscription/screen.json').read_text())
qrows=[]
for phase in [s,q]:
 for l in phase['looks']:
  slots=set(l['selected_resident_service']['public_slots'])
  raw=union([(op['start'],op['stop']) for op in l['operations'] if op['job_id'] in slots])
  assert abs(raw-l['selected_resident_service']['seconds'])<1e-10
  cpu=l['monitor']['process_cpu_seconds']+l['monitor']['reaped_decoder_cpu_seconds']
  busy=cpu/l['monitor']['monitoring_seconds']
  assert abs(busy-l['average_busy_cores'])<1e-10
  if phase is q:qrows.append((l['route'],raw,l['complete_lifecycle_seconds'],busy,cpu))
print('9 original selected-span unions and matching monitor CPU ratios agree with receipts.')
print('ABBA route,resident_union,cold_lifecycle,busy_cores,cpu_seconds:',qrows)
b=[x for x in qrows if x[0]=='p2w12']; c=[x for x in qrows if x[0]=='p3w18']
for col,name in [(1,'resident'),(2,'cold'),(3,'busy'),(4,'cpu_seconds')]:
 bv=statistics.median(x[col] for x in b);cv=statistics.median(x[col] for x in c)
 print(name,bv,cv,'relative change',cv/bv-1)
print('matched ratios',[c[i][1]/b[i][1] for i in [0,1]])
t=json.loads((p/'c54-trace/timing-trace.json').read_text())
for phase in ['fine_tracking','fine_basis_job','fine_gaussian_job','parent_drain']:
 es=[e for e in t['events'] if e.get('phase')==phase]
 print(phase,len(es),'wall sums',sum(e['end_ns']-e['start_ns'] for e in es)/1e9,'CPU sums',sum(e.get('thread_cpu_ns') or 0 for e in es)/1e9)
source=ast.parse((p/'source/tools/triad_tracking_receiver.py').read_text())
cl=next(n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='PracticalTrackingReceiver')
fun=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name=='push')
print('PracticalTrackingReceiver.push calls',[(n.lineno,ast.unparse(n.func)) for n in ast.walk(fun) if isinstance(n,ast.Call)])
print('PASS independent raw receipt arithmetic and static source inspection; zero receiver execution assertions.')
