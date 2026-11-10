#!/usr/bin/env python3
"""Audit frozen u519 archived ABBA/trace claims; no receiver execution."""
import json, pathlib, statistics, sys
base = pathlib.Path('/tmp/objective-recovery-runs/u519/packet')
abba = base / 'abba-oversubscription'
screen = json.loads((abba/'screen.json').read_text())
qual = json.loads((abba/'qualify.json').read_text())
audit = json.loads((abba/'independent-audit.json').read_text())
trace = json.loads((base/'c54-trace/timing-trace.json').read_text())
pre = json.loads((abba/'predeclared.json').read_text())
summary = qual['summary']
looks = qual['looks']
base_r = [x['selected_resident_service']['seconds'] for x in looks if x['route']=='p2w12']
cand_r = [x['selected_resident_service']['seconds'] for x in looks if x['route']=='p3w18']
base_c = [x['complete_lifecycle_seconds'] for x in looks if x['route']=='p2w12']
cand_c = [x['complete_lifecycle_seconds'] for x in looks if x['route']=='p3w18']
assert len(base_r)==len(cand_r)==len(base_c)==len(cand_c)==2
med_b, med_c = statistics.median(base_r), statistics.median(cand_r)
ratios = [c/b for b,c in zip(base_r,cand_r)]
resident_gain = 1-med_c/med_b
cold_gain = 1-statistics.median(cand_c)/statistics.median(base_c)
assert qual['status']=='performance_gate_rejected'
assert screen['selected_route']=='p3w18'
assert all(x['row']['complete_receiver_work_covered'] for x in looks)
assert audit['status']=='verified_performance_gate_rejected'
assert audit['verified_checks']['all_selected_unions_envelopes_and_gaps_recomputed_exactly']
assert audit['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']
assert audit['verified_checks']['all_modeled_and_sampled_memory_checks_passed']
assert audit['verified_checks']['fallbacks_or_retries']==0
assert abs(med_b-summary['resident_baseline_seconds']) < 1e-8
assert abs(med_c-summary['resident_candidate_seconds']) < 1e-8
assert abs(resident_gain-summary['resident_reduction']) < 1e-8
assert max(abs(a-b) for a,b in zip(ratios,summary['paired_resident_ratios'])) < 1e-8
assert abs(cold_gain-summary['cold_reduction']) < 1e-8
minimum_resident_reduction=0.15
maximum_cold_regression=0.05
print(f"screen selected={screen['selected_route']} threshold=10% point gain only")
print(f"ABBA resident medians baseline={med_b:.3f}s candidate={med_c:.3f}s gain={resident_gain*100:.2f}% required={minimum_resident_reduction*100:.1f}%")
print('paired candidate/baseline ratios='+','.join(f'{x:.4f}' for x in ratios)+' (both must be <1)')
print(f"cold lifecycle median reduction={cold_gain*100:.2f}% maximum regression={maximum_cold_regression*100:.1f}%")
print(f"busy cores baseline={summary['busy_baseline']:.2f} candidate={summary['busy_candidate']:.2f}")
print(f"independent audit: {audit['status']}; 87 selected span unions; {audit['verified_checks']['looks']} looks; no fallback/retry")
assert resident_gain < minimum_resident_reduction
assert all(x < 1 for x in ratios)
assert cold_gain >= -maximum_cold_regression
print('decision: retain rejection of p3w18 adoption; speed gate fails despite higher busy-core measure')
print(f"older trace source={trace['source_before']['revision']} later ABBA source={qual['source_before']['revision']} (distinct checkpoints)")
print('scope: archived receipt arithmetic and metadata only; no source candidate rebuild/reproduction')
