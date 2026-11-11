"""One bounded clarification of the noisy h23 width diagnostic."""
from pathlib import Path
import hashlib
import json
import random
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent / 'spectral-diagnostic'
OUTPUT = ROOT / 'clarification.json'
if OUTPUT.exists():
    raise SystemExit('Refusing to replace original clarification')
names = ['submitted-fp64', 'fp32-transform']
result = {'groups': 25, 'cold_requests_per_group': 3,
          'flags': ['-O3', '-std=c++17', '-Wall', '-Wextra', '-pedantic'],
          'shape': ['32', '4', '1024'], 'rows': [], 'compiler_commands': []}
order = [0, 1] * 12 + [0]
random.Random(20261111).shuffle(order)
hashes = {}
with tempfile.TemporaryDirectory() as td:
    exes = {}
    for name in names:
        exe = Path(td) / name
        command = ['g++', *result['flags'], str(ROOT / name / 'core.cpp'), '-o', str(exe)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        result['compiler_commands'].append(command)
        exes[name] = exe
    for group, first in enumerate(order):
        row = {'group': group, 'order': [names[first], names[1-first]], 'observations': {}}
        for name in row['order']:
            observed=[]
            for rep in range(3):
                start = time.perf_counter()
                run = subprocess.run([str(exes[name]), *result['shape']],
                                     check=True, capture_output=True, text=True)
                elapsed = time.perf_counter() - start
                header, _, data = run.stdout.partition(' values=')
                fields = dict(token.split('=', 1) for token in header.split())
                digest = hashlib.sha256(data.encode()).hexdigest()
                hashes.setdefault(name, digest)
                assert hashes[name] == digest and int(fields['outputs']) == 65664
                observed.append({'elapsed_s': elapsed, 'internal_s': float(fields['seconds'])})
            row['observations'][name] = observed
        result['rows'].append(row)
for metric in ['elapsed_s', 'internal_s']:
    values = {name: [statistics.mean(r[metric] for r in row['observations'][name])
                     for row in result['rows']] for name in names}
    paired = [a-b for a,b in zip(values[names[0]], values[names[1]])]
    result[metric + '_summary'] = {
        'group_means': values,
        'overall_mean_s': {name: statistics.mean(v) for name,v in values.items()},
        'group_median_s': {name: statistics.median(v) for name,v in values.items()},
        'narrow_wins': sum(v > 0 for v in paired),
        'paired_mean_s': statistics.mean(paired),
        'paired_stdev_s': statistics.stdev(paired),
        'paired_median_s': statistics.median(paired)}
result['full_output_hashes_stable_across_75_cold_requests_each'] = hashes
OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k.endswith('_summary')}, indent=2))
