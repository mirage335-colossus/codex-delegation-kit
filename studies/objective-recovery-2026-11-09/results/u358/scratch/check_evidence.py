#!/usr/bin/env python3
"""Check key archive claims without executing the receiver or reconstructing the ABBA run."""
import json
from pathlib import Path
ROOT = Path('/tmp/objective-recovery-runs/u358/packet')
load = lambda rel: json.loads((ROOT / rel).read_text())
pre = load('abba-oversubscription/predeclared.json')
screen = load('abba-oversubscription/screen.json')
qual = load('abba-oversubscription/qualify.json')
audit = load('abba-oversubscription/independent-audit.json')
trace = load('c54-trace/timing-trace.json')
trace_pre = load('c54-trace/predeclared.json')
assert audit['status'] == 'verified_performance_gate_rejected'
assert qual['status'] == 'performance_gate_rejected'
assert audit['verified_checks']['looks'] == 9
assert audit['verified_checks']['jobs_with_all_five_unique_ordered_spans'] == 87
assert audit['verified_checks']['all_selected_unions_envelopes_and_gaps_recomputed_exactly']
s = qual['summary']; q = audit['qualification']
assert abs(s['resident_reduction'] - (1-s['resident_candidate_seconds']/s['resident_baseline_seconds'])) < 1e-12
assert all(r < 1 for r in s['paired_resident_ratios'])
assert s['resident_reduction'] < q['resident_reduction_minimum']
assert s['cold_reduction'] > 0 and s['cold_reduction'] < .15
assert abs(s['busy_baseline']-q['busy_baseline']) < 1e-12
assert abs(s['busy_candidate']-q['busy_candidate']) < 1e-12
assert len(screen['looks']) == 5 and len(qual['looks']) == 4
assert audit['source_and_input']['frozen_source_count'] == 66
assert trace['status'] == 'passed' and trace['source_verified_unchanged'] and trace['input_verified_unchanged']
assert trace['maximum_numeric_difference'] == 0
assert trace_pre['aggregate_workers'] == 12
assert trace_pre['scope'].startswith('Currentwholefivewindow chronology')
assert trace['selected_fine_cycle']['scope'].endswith('not representativewarmaverage.')
print('ABBA status:', qual['status'], '/', audit['status'])
print('Coverage: 5 screen routes; 4 ABBA looks; audited 9 total looks and 87 jobs')
print(f"Resident: {s['resident_baseline_seconds']:.6f}s -> {s['resident_candidate_seconds']:.6f}s; reduction={100*s['resident_reduction']:.3f}% vs {100*q['resident_reduction_minimum']:.1f}% predeclared gate")
print('Paired resident ratios:', ', '.join(f'{x:.6f}' for x in s['paired_resident_ratios']))
print(f"Cold lifecycle: {s['cold_baseline_seconds']:.6f}s -> {s['cold_candidate_seconds']:.6f}s; reduction={100*s['cold_reduction']:.3f}%")
print(f"Busy-core equivalents: {s['busy_baseline']:.3f} -> {s['busy_candidate']:.3f} / 12")
print('Earlier c54 trace: control/trace passed, exact numeric parity, inputs/source unchanged; selected cycle is explicitly nonrepresentative.')
print('Archive boundary: ABBA revision 488c26aae4abc05b5d25f88844562d88cf1ab06c; earlier trace revision c54e24698c69c79805b5aad86205abdd36d2ca7c; no reconstruction attempted.')
