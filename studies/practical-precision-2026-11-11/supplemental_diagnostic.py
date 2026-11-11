"""Post-holdout discriminator, chosen after inspecting the two selectors.

Not an independent holdout or an unbiased prompt-effect estimate. Demonstrates
whether easy-case scalarization can lower useful capacity, and whether precision
labels change that mechanism. No source or frozen checks are modified.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
output = {}
for name in ('t01', 't02'):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'transfer' / name / 'selector.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    output[name] = []
    for bits in ((64, 16), (16, 64)):
        rows = [dict(id=label, bits=precision, stress_capacity=capacity, easy_ms=easy,
                     supported=True, qualified=True, memory_mb=64, error=.01)
                for label, precision, capacity, easy in
                [('fast_idle', bits[0], 80, .8), ('more_capacity', bits[1], 85, .9)]]
        selected = m.select_route(rows, 1024)
        output[name].append(dict(bits=bits, selected=selected,
                                 capacity=next(r['stress_capacity'] for r in rows if r['id'] == selected)))
print(json.dumps(output, indent=2))
