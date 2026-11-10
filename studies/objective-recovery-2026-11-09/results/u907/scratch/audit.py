#!/usr/bin/env python3
"""Executable discriminator for the archived worker-width decision."""
import json
from pathlib import Path
ROOT = Path('/tmp/objective-recovery-runs/u907/packet')
screen = json.loads((ROOT/'abba-oversubscription/screen.json').read_text())
qual = json.loads((ROOT/'abba-oversubscription/qualify.json').read_text())
audit = json.loads((ROOT/'abba-oversubscription/independent-audit.json').read_text())
trace = json.loads((ROOT/'c54-trace/timing-trace.json').read_text())
assert audit['status'] == 'verified_performance_gate_rejected'
assert audit['verified_checks']['all_selected_unions_envelopes_and_gaps_recomputed_exactly']
assert audit['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']
base = next(x for x in screen['looks'] if x['route']=='p2w12')
three = next(x for x in screen['looks'] if x['route']=='p3w18')
six = next(x for x in screen['looks'] if x['route']=='p6w24')
def t(x): return x['selected_resident_service']['seconds']
def pct(a,b): return 100*(a-b)/a
print(f"screen p3w18 gain vs p2w12: {pct(t(base),t(three)):.3f}% (predeclared >=10% point screen)")
print(f"screen p6w24 gain vs p2w12: {pct(t(base),t(six)):.3f}%")
s = qual['summary']; rg = s['resident_reduction']*100; cg=s['cold_reduction']*100
print(f"ABBA selected p3w18 resident reduction: {rg:.3f}% (required >=15%)")
print('ABBA matched resident ratios:', ', '.join(f"{v:.6f}" for v in s['paired_resident_ratios']))
print(f"ABBA cold complete-lifecycle reduction: {cg:.3f}% (allowed regression <=5%)")
print(f"ABBA average busy cores: {s['busy_baseline']:.3f} -> {s['busy_candidate']:.3f} / 12 visible logical CPUs")
print(f"busy-core capacity share: {100*s['busy_baseline']/12:.1f}% -> {100*s['busy_candidate']/12:.1f}%")
print(f"trace observer paired: {trace['looks'][0]['outer_seconds']:.6f}s control; {trace['looks'][1]['outer_seconds']:.6f}s traced; observer overhead {trace['observer_overhead_fraction']*100:.3f}%")
print(f"c54 trace source rev: {trace['source_before']['revision']}; ABBA revision: {qual['source_before']['revision']}")
print(f"c54 trace input sha256 IQ/valid: {trace['input_iq_sha256']} / {trace['input_valid_sha256']}")
print(f"ABBA full-capture IQ/valid: {audit['source_and_input']['raw_array_sha256_verified']['iq']} / {audit['source_and_input']['raw_array_sha256_verified']['valid']}")
print('assertions: 3 receipt/parity assertions passed; arithmetic outputs above')
