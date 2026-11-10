#!/usr/bin/env python3
"""Recompute the predeclared resident adoption decision from archived receipts."""
import json
from pathlib import Path
root=Path('/tmp/objective-recovery-runs/u851/packet/abba-oversubscription')
p=json.loads((root/'predeclared.json').read_text())
q=json.loads((root/'qualify.json').read_text())
a=json.loads((root/'independent-audit.json').read_text())
s=q['summary']
gain=s['resident_reduction']
ratios=s['paired_resident_ratios']
cold=s['cold_reduction']
checks={
 'audit_verified_rejection':a['status']=='verified_performance_gate_rejected',
 'qualification_gate_rejected':q['status']=='performance_gate_rejected',
 'resident_below_predeclared_minimum':gain < .15,
 'both_pairs_improved':len(ratios)==2 and all(r<1 for r in ratios),
 'cold_not_regressed_over_5pct':cold >= -.05,
 'screen_winner_not_adopted':q.get('selected_route') is None,
}
for k,v in checks.items(): print(f'{k}={v}')
print(f"resident_reduction={gain:.6%}; required={.15:.0%}; ratios={ratios}; cold_reduction={cold:.6%}")
assert all(checks.values()), 'Archived evidence no longer supports the documented disposition'
print('PASS: performance rejection stands; cold/pair results do not waive resident gate.')
