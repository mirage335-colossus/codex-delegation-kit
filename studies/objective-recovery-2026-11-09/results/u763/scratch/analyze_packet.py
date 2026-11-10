#!/usr/bin/env python3
"""Recompute archive gates and selected c54 scheduling facts from frozen packet."""
import json, pathlib, statistics
ROOT = pathlib.Path('/tmp/objective-recovery-runs/u763/packet')
abba = ROOT/'abba-oversubscription'
trace = json.loads((ROOT/'c54-trace/timing-trace.json').read_text())
audit = json.loads((abba/'independent-audit.json').read_text())
pre = json.loads((abba/'predeclared.json').read_text())
sc = json.loads((abba/'screen.json').read_text())
q = json.loads((abba/'qualify.json').read_text())
assert audit['status'] == 'verified_performance_gate_rejected'
assert audit['qualification']['resident_reduction'] < 0.15
assert all(x < 1 for x in audit['qualification']['paired_resident_ratios'])
assert audit['qualification']['cold_reduction'] > 0
assert audit['source_and_input']['live_source_and_native_hashes_verified_before_width_rollback']
assert audit['source_and_input']['exact_driver_hash_matches_predeclaration_and_both_phases']
assert audit['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']
base = next(x for x in sc['looks'] if x['route']=='p2w12')['row']['ratio_processing_seconds_per_baseband_second']
screen = next(x for x in sc['looks'] if x['route']=='p3w18')['row']['ratio_processing_seconds_per_baseband_second']
assert audit['screen']['selected_route'] == 'p3w18' and audit['screen']['selected_point_gain'] >= 0.10
assert trace['source_verified_unchanged'] and trace['input_verified_unchanged'] and trace['driver_verified_unchanged']
assert trace['status'] == 'passed'
# Source order establishes sequential lane dispatch at this checkpoint.
source = (ROOT/'source/tools/triad_tracking_receiver.py').read_text()
start = source.index('    def push(self, first_sample, values, valid=None, *, physical_origin=None, physical_offsets=None):', source.index('class PracticalTrackingReceiver'))
end = source.index('\n    def _combine', start)
push = source[start:end]
assert push.index('self.nominal.push(') < push.index('self.adaptive.push(')
events = trace['events']
selected = [e for e in events if e.get('job_id') == 3 and e.get('phase') in ('fine_cycle','fine_basis_statistics','fine_basis_dispatch','fine_gaussian','fine_merge')]
cycles = [e for e in selected if e['phase']=='fine_cycle']
assert {e['lane'] for e in cycles} == {'_InitialAffineReceiver','_PersistentTimingLane'}
cycle_spans = [(e['end_ns']-e['start_ns'])/1e6 for e in cycles]
workers = [e for e in events if e.get('job_id')==3 and e.get('phase')=='fine_basis_job']
gauss = [e for e in events if e.get('job_id')==3 and e.get('phase')=='fine_gaussian_job']
print('ABBA decision: REJECT width expansion for adoption; keep p2w12 default, p3w18 only as unqualified candidate.')
print(f"Screen-selected resident-slot point gain={audit['screen']['selected_point_gain']*100:.2f}% (metric is not the whole-stream ratio {base:.5f}->{screen:.5f}); qualification resident gain={audit['qualification']['resident_reduction']*100:.2f}% vs required {15:.0f}%.")
print(f"Paired resident ratios={audit['qualification']['paired_resident_ratios']}; cold lifecycle reduction={audit['qualification']['cold_reduction']*100:.2f}%; mean busy cores={audit['qualification']['busy_baseline']:.2f}->{audit['qualification']['busy_candidate']:.2f}/12.")
print(f"Archive parity/source/input audit checks: {audit['verified_checks']['looks']} looks, {audit['verified_checks']['jobs_with_all_five_unique_ordered_spans']} jobs; hashes unchanged before width rollback={audit['source_and_input']['live_source_and_native_hashes_verified_before_width_rollback']}.")
print(f"c54 trace: complete five windows; trace/control ratio={trace['looks'][1]['outer_seconds']/trace['looks'][0]['outer_seconds']:.5f}, observer slowdown limit check={trace['absolute_timing_qualification']}.")
print(f"Selected c54 3,000-row fine cycles: {[(e['lane'],round((e['end_ns']-e['start_ns'])/1e6,2)) for e in cycles]} ms; lane push order in source is nominal then adaptive (serial).")
print(f"That cycle recorded {len(workers)} mapped-basis worker intervals (aggregate worker CPU {sum(e['thread_cpu_ns'] for e in workers)/1e6:.1f} ms) and {len(gauss)} Gaussian worker intervals (aggregate worker CPU {sum(e['thread_cpu_ns'] for e in gauss)/1e6:.2f} ms). This is a scheduling lead, not proof of safe parallel lanes or general throughput.")
print('Coverage limit: one configured-calendar row-7 continuous stream; 5-window screen and 13-window ABBA. No manually specified full-suite forecasts or whole-message sensitivity qualification here.')
