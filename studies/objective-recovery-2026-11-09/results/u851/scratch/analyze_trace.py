#!/usr/bin/env python3
"""Summarize phase wall/CPU evidence from the immutable c54 timing trace."""
import json
from collections import defaultdict
from pathlib import Path
p=Path('/tmp/objective-recovery-runs/u851/packet/c54-trace/timing-trace.json')
d=json.loads(p.read_text())
g=defaultdict(lambda:[0,0,0])
for e in d['events']:
    if e.get('kind') not in ('phase','worker'): continue
    a,b=e.get('start_ns'),e.get('end_ns')
    if not isinstance(a,int) or not isinstance(b,int) or b<a: continue
    x=g[e.get('phase','?')]
    x[0]+=1; x[1]+=b-a; x[2]+=e.get('thread_cpu_ns') or 0
print('phase,count,aggregate_event_wall_s,thread_cpu_s,scope_note')
for k,(n,w,c) in sorted(g.items(),key=lambda kv:kv[1][2],reverse=True):
    print(f'{k},{n},{w/1e9:.6f},{c/1e9:.6f},overlapping event intervals; thread CPU is not OS-running time')
# Job 3 selected cycle: event kinds/phase counts and parent duration.
print('\nSelected job 3 fine cycle events:')
for e in d['events']:
    if e.get('job_id')==3 and e.get('kind') in ('phase','worker'):
        a,b=e.get('start_ns'),e.get('end_ns')
        if isinstance(a,int) and isinstance(b,int):
            print(f"{e.get('kind'):6} {e.get('phase'):22} pid={e.get('owner_pid')} tid={e.get('thread_id')} wall={(b-a)/1e6:9.3f}ms cpu={(e.get('thread_cpu_ns') or 0)/1e6:8.3f}ms parent={e.get('parent_id')}")
