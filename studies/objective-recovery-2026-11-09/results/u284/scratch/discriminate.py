#!/usr/bin/env python3
"""Recompute the archived disposition and c54 trace signals (stdlib only)."""
import json
import statistics
from collections import defaultdict
from pathlib import Path

PACKET = Path('/tmp/objective-recovery-runs/u284/packet')
out = {}
screen = json.loads((PACKET/'abba-oversubscription/screen.json').read_text())
qual = json.loads((PACKET/'abba-oversubscription/qualify.json').read_text())
audit = json.loads((PACKET/'abba-oversubscription/independent-audit.json').read_text())
trace = json.loads((PACKET/'c54-trace/timing-trace.json').read_text())

def vals(phase, route, key):
    return [x[key] if key != 'service' else x['selected_resident_service']['seconds']
            for x in phase['looks'] if x['route'] == route]

base = vals(qual, 'p2w12', 'service')
cand = vals(qual, 'p3w18', 'service')
cold_base = vals(qual, 'p2w12', 'complete_lifecycle_seconds')
cold_cand = vals(qual, 'p3w18', 'complete_lifecycle_seconds')
resident_reduction = 1-statistics.median(cand)/statistics.median(base)
cold_reduction = 1-statistics.median(cold_cand)/statistics.median(cold_base)
pair_ratios = [cand[0]/base[0], cand[1]/base[1]]
out['abba'] = {
    'audit_status': audit['status'], 'qualification_status': qual['status'],
    'screen_winner': screen['selected_route'],
    'screen_service_seconds': {x['route']: x['selected_resident_service']['seconds']
                               for x in screen['looks']},
    'qualification_resident_seconds': {'baseline': base, 'candidate': cand},
    'resident_reduction_recomputed': resident_reduction,
    'cold_complete_lifecycle_seconds': {'baseline': cold_base, 'candidate': cold_cand},
    'cold_reduction_recomputed': cold_reduction, 'matched_pair_ratios': pair_ratios,
    'busy_cores': {'baseline': vals(qual,'p2w12','average_busy_cores'),
                   'candidate': vals(qual,'p3w18','average_busy_cores')},
    'hardware_threads': audit['verified_checks']['effective_hardware_threads'],
    'memory_bytes': audit['verified_checks']['common_cap_bytes'],
}

events = trace['events']
agg = defaultdict(lambda: [0, 0, 0])
for e in events:
    if e.get('kind') == 'phase':
        a = agg[e['phase']]
        a[0] += e['end_ns']-e['start_ns']
        a[1] += e.get('thread_cpu_ns') or 0
        a[2] += 1
out['c54_trace'] = {
    'checkpoint': trace['source_before']['revision'],
    'input_samples': trace['input_samples'],
    'max_numeric_difference': trace['maximum_numeric_difference'],
    'worker_allocations_by_job': [j['workers'] for j in trace['jobs']],
    'phase_inclusive_elapsed_and_thread_cpu_seconds': {
        k: {'elapsed_sum_seconds': round(v[0]/1e9, 4),
            'thread_cpu_sum_seconds': round(v[1]/1e9, 4), 'events': v[2]}
        for k,v in sorted(agg.items(), key=lambda kv:-kv[1][0])},
    'clock_interpretation': trace['clock']['scope'],
}

# The disposition criterion is intentionally the declared 15% qualification gate.
out['gate'] = {
    'resident_minimum': 0.15,  # Parsed from the archived predeclaration's "≥15%" clause.
    'resident_pass': resident_reduction >= 0.15,
    'both_matched_pairs_faster': all(r < 1 for r in pair_ratios),
    'cold_regression_within_5pct': cold_reduction >= -0.05,
    'disposition': 'REJECT wider-controller adoption; retain two-owner default pending complete forecasts'
        if not (resident_reduction >= 0.15 and all(r < 1 for r in pair_ratios) and cold_reduction >= -0.05)
        else 'QUALIFY wider-controller candidate',
}
assert not out['gate']['resident_pass']
assert out['gate']['both_matched_pairs_faster']
assert out['gate']['cold_regression_within_5pct']
assert trace['maximum_numeric_difference'] == 0.0 and trace['source_verified_unchanged']
print(json.dumps(out, indent=2, sort_keys=True))
