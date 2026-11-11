"""Coordinator diagnostic after a predeclared v3 behavioral miss."""
from pathlib import Path
import json
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'metrology-diagnostic'
OUT.mkdir(exist_ok=True)
if (OUT / 'results.json').exists():
    raise SystemExit('Refusing to overwrite original diagnostic')
original = (ROOT / 'runs/g12/submitted/core.cpp').read_text()
plain = original.replace('add_compensated(value, total[c], total_correction[c]);',
                         'total[c] += value;').replace(
    'add_compensated(value * value, squares[c], squares_correction[c]);',
    'squares[c] += value * value;')
assert plain != original and plain.count('add_compensated(') == 1
mixed = plain.replace('squares[c] += value * value;',
                      'squares[c] += static_cast<float>(value) * static_cast<float>(value);')
sources = {'g12-submitted': original, 'plain-wide-sums': plain,
           'narrow-products-wide-sums': mixed,
           'g22-reused-cycle': (ROOT / 'runs/g22/submitted/core.cpp').read_text()}
result = {'kind': 'post-holdout coordinator diagnostic, not autonomous success',
          'flags': ['-O2', '-std=c++17'], 'shape': ['12000', '305419896', 'transient'],
          'quality': {}, 'timings': {}}
for name, code in sources.items():
    path = OUT / name
    path.mkdir()
    (path / 'core.cpp').write_text(code)
    command = ['python3', '-B', str(ROOT / 'frozen/e/streaming-metrology/private/evaluate.py'), str(path)]
    run = subprocess.run(command, capture_output=True, text=True)
    result['quality'][name] = dict(command=command, returncode=run.returncode,
                                  stdout=run.stdout, stderr=run.stderr)
    assert run.returncode == 0, name
with tempfile.TemporaryDirectory() as td:
    exes = {}
    for name in sources:
        exe = Path(td) / name
        command = ['g++', *result['flags'], str(OUT / name / 'core.cpp'), '-o', str(exe)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        exes[name] = exe
        result['timings'][name] = {'compile': command, 'whole_process_observations': []}
    names = list(exes)
    for rep in range(7):
        order = names[rep % len(names):] + names[:rep % len(names)]
        if rep % 2:
            order.reverse()
        for name in order:
            command = [str(exes[name]), *result['shape']]
            start = time.perf_counter()
            run = subprocess.run(command, check=True, capture_output=True, text=True)
            elapsed = time.perf_counter() - start
            result['timings'][name]['whole_process_observations'].append(
                dict(repetition=rep, elapsed_s=elapsed, output=run.stdout))
    for row in result['timings'].values():
        row['median_s'] = statistics.median(x['elapsed_s'] for x in row['whole_process_observations'])
(OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({name: row['median_s'] for name, row in result['timings'].items()}, indent=2))
