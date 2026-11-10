#!/usr/bin/env python3
"""Recompute archived ABBA decision gates; no receiver execution."""
import json
from pathlib import Path

root = Path('/home/user/___quick/p/_cur/codex-delegation-kit/studies/objective-recovery-2026-11-09/freeze/packet/abba-oversubscription')
q = json.loads((root / 'qualify.json').read_text())
a = json.loads((root / 'independent-audit.json').read_text())
s = json.loads((root / 'screen.json').read_text())
summary = q['summary']
looks = q['looks']
baseline = [l['selected_resident_service']['seconds'] for l in (looks[0], looks[3])]
candidate = [l['selected_resident_service']['seconds'] for l in (looks[1], looks[2])]
ratios = [candidate[0]/baseline[0], candidate[1]/baseline[1]]
screen_baseline = next(l['selected_resident_service']['seconds'] for l in s['looks'] if l['route'] == 'p2w12')
screen_candidate = next(l['selected_resident_service']['seconds'] for l in s['looks'] if l['route'] == s['selected_route'])
screen_gain = 1 - screen_candidate/screen_baseline
resident_reduction = 1 - sum(candidate)/sum(baseline)
cold_reduction = 1 - summary['cold_candidate_seconds']/summary['cold_baseline_seconds']
busy_base, busy_cand = summary['busy_baseline'], summary['busy_candidate']
checks = {
    'screen selected candidate is p3w18 at >=10% screen gain':
        s['selected_route'] == 'p3w18' and screen_gain >= .10,
    'both paired resident ratios favor candidate': all(r < 1 for r in ratios),
    'resident median reduction meets >=15% adoption gate': resident_reduction >= .15,
    'cold lifecycle avoids >5% regression': cold_reduction >= -.05,
    'parity/resource/provenance audit accepted':
        a['status'] == 'verified_performance_gate_rejected'
        and a['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']
        and a['verified_checks']['all_modeled_and_sampled_memory_checks_passed']
        and a['source_and_input']['exact_driver_hash_matches_predeclaration_and_both_phases'],
}
print(f"ABBA resident ratios: {ratios[0]:.6f}, {ratios[1]:.6f}")
print(f"Resident reduction: {resident_reduction:.3%} (required >=15%)")
print(f"Cold lifecycle reduction: {cold_reduction:.3%} (allowed no worse than -5%)")
print(f"Average busy cores: {busy_base:.3f} -> {busy_cand:.3f} of 12")
print(f"Candidate screen gain: {screen_gain:.3%}; route {s['selected_route']}")
for name, result in checks.items():
    print(('PASS' if result else 'FAIL') + ': ' + name)
assert all(checks.values()) is False  # archived rejection is expected
assert checks['both paired resident ratios favor candidate']
assert not checks['resident median reduction meets >=15% adoption gate']
assert checks['cold lifecycle avoids >5% regression']
assert checks['parity/resource/provenance audit accepted']
