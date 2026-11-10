import json, pathlib, hashlib
R=pathlib.Path('/tmp/objective-recovery-runs/u091/packet')
def load(p): return json.loads((R/p).read_text())
s=load('abba-oversubscription/screen.json'); q=load('abba-oversubscription/qualify.json'); a=load('abba-oversubscription/independent-audit.json')
t=load('c54-trace/timing-trace.json'); pre=load('c54-trace/predeclared.json')
assert a['status']=='verified_performance_gate_rejected'
assert a['verified_checks']['effective_hardware_threads']==12 and a['verified_checks']['looks']==9
assert q['status']=='performance_gate_rejected' and len(q['looks'])==4
assert q['source_verified_unchanged'] and q['driver_verified_unchanged'] and q['input_verified_unchanged']
assert q['private_driver_sha256']==q['final_driver_sha256']
assert s['source_verified_unchanged'] and s['input_verified_unchanged'] and s['driver_verified_unchanged']
summary=q['summary']; assert summary['resident_reduction']<.15 and summary['cold_reduction']>=-.05
assert all(x<1 for x in summary['paired_resident_ratios'])
base=q['looks'][0]; cand=q['looks'][1]
assert (base['route'],cand['route'])==('p2w12','p3w18')
assert base['hardware_threads']==cand['hardware_threads']==12
assert cand['average_busy_cores']>base['average_busy_cores']
assert cand['row']['complete_receiver_work_covered'] if 'complete_receiver_work_covered' in cand['row'] else cand['row']['slot_pipeline']['submitted_jobs']==13
assert t['status']=='passed' and t['source_after']['revision']=='c54e24698c69c79805b5aad86205abdd36d2ca7c'
assert t['maximum_numeric_difference']==0 and t['message_numeric_difference']==0
assert t['absolute_timing_qualification']=='singlematchedcontrol_within10percent_slowdown'
assert t['input_samples']==1649627 and len(t['events'])==206
# Stable source-bound scheduling limit and trace structural lead.
src=(R/'source/tools/triad_stream_receiver.py').read_text()
assert 'len(self._jobs) >= 2' in src and 'maximum_processes=2 if self._pipeline else 1' in src
ph=[e for e in t['events'] if e.get('kind')=='phase' and e.get('phase')=='fine_tracking']
assert len(ph)==5
print('PASS archived receipts: unchanged source/driver/input; 12 hardware threads; complete ABBA; exact exposed work by audit')
print(f"ABBA p2w12 -> p3w18: busy cores {base['average_busy_cores']:.3f} -> {cand['average_busy_cores']:.3f}; gain {summary['resident_reduction']*100:.2f}% resident, {summary['cold_reduction']*100:.2f}% cold")
print(f"resident paired ratios={summary['paired_resident_ratios']}; acceptance required >=15% resident so archived gate remains rejected")
print(f"earlier c54 checkpoint: 5-window captured source/input, exact decision/numeric parity, timing qualification={t['absolute_timing_qualification']}; 5 fine_tracking intervals totaling {sum((e['end_ns']-e['start_ns'])/1e9 for e in ph):.3f}s while traced fine_cycles total {sum((e['end_ns']-e['start_ns'])/1e9 for e in t['events'] if e.get('phase')=='fine_cycle'):.3f}s (sparse cycle not representative)")
print('bounded source serializes capacity to two in _dispatch_ready; controller drain can wait with negligible parent CPU, but called intervals are not OS scheduled CPU time')
