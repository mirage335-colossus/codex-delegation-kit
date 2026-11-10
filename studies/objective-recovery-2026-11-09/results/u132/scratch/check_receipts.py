#!/usr/bin/env python3
"""Read-only discriminator for the frozen u132 performance and trace receipts."""
import json
from pathlib import Path

ROOT = Path('/tmp/objective-recovery-runs/u132/packet')

def load(path):
    return json.loads(path.read_text())

screen = load(ROOT/'abba-oversubscription/screen.json')
qual = load(ROOT/'abba-oversubscription/qualify.json')
audit = load(ROOT/'abba-oversubscription/independent-audit.json')
trace = load(ROOT/'c54-trace/timing-trace.json')
assert audit['status'] == 'verified_performance_gate_rejected'
assert qual['status'] == 'performance_gate_rejected'
s = qual['summary']
assert s['resident_reduction'] < .15
assert max(s['paired_resident_ratios']) < 1
assert s['cold_reduction'] >= -.05 # actual predeclared allowance was max 5% regression
assert screen['selected_route'] == 'p3w18'
assert trace['status'] == 'passed'
assert trace['source_verified_unchanged'] and trace['driver_verified_unchanged']
assert trace['input_iq_sha256'] == trace['final_input_iq_sha256']
assert trace['input_valid_sha256'] == trace['final_input_valid_sha256']
phases = {}
for e in trace['events']:
    d = phases.setdefault((e['kind'], e['phase']), [0, 0, 0])
    d[0] += e['end_ns'] - e['start_ns']
    d[1] += e.get('thread_cpu_ns') or 0
    d[2] += 1
print('ABBA:', qual['status'], 'selected_route=', screen['selected_route'])
print('resident median reduction=', round(s['resident_reduction']*100, 2), '%; required 15%')
print('paired resident ratios=', ', '.join(f'{v:.4f}' for v in s['paired_resident_ratios']), '; each must be <1')
print('cold reduction=', round(s['cold_reduction']*100, 2), '%; predeclared maximum cold regression 5%')
print('busy cores baseline/candidate=', round(s['busy_baseline'], 2), '/', round(s['busy_candidate'], 2))
print('trace status=', trace['status'], 'observer overhead=', round(trace['observer_overhead_fraction']*100, 3), '%')
print('same input/source/driver=', trace['input_iq_sha256']==trace['final_input_iq_sha256'] and trace['input_valid_sha256']==trace['final_input_valid_sha256'], trace['source_verified_unchanged'], trace['driver_verified_unchanged'])
for key in [('phase','fine_tracking'), ('phase','bank_preparation'), ('phase','parent_drain'), ('phase','parent_ingress'), ('phase','fine_cycle'), ('worker','fine_basis_job')]:
    v=phases.get(key,[0,0,0]); print(f'trace {key[1]}: wall-span sum={v[0]/1e9:.3f}s cpu={v[1]/1e9:.3f}s events={v[2]}')
print('Trace intervals overlap; phase wall sums are diagnostic and must not be added as total service.')
