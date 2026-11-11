"""Post-holdout coordinator diagnostic, never scored as autonomous success."""
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'fir-diagnostic'
OUT.mkdir(exist_ok=True)
if (OUT / 'results.json').exists():
    raise SystemExit('Refusing to overwrite original diagnostic')

sources = {}
for ident in ('f12', 'f24'):
    original = (ROOT / 'runs' / ident / 'submitted/core.cpp').read_text()
    if ident == 'f12':
        product = ('static_cast<double>(input[channel_offset + source]) *\n'
                   '                         static_cast<double>(coefficients[k])')
        narrow = 'input[channel_offset + source] * coefficients[k]'
        acc, local = 'double accumulator = 0.0;', 'VALUE accumulator = 0;'
    else:
        product = '(double)x[(size_t)c*n+q]*(double)h[k]'
        narrow = 'x[(size_t)c*n+q]*h[k]'
        acc, local = 'double acc=0;', 'VALUE acc=0;'
    assert original.count(product) == original.count(acc) == 1
    mixed = original.replace(product, narrow)
    variants = {'submitted': original, 'narrow_products': mixed,
                'narrow_products_and_sum': mixed.replace(acc, local)}
    for variant, code in variants.items():
        name = ident + '-' + variant
        path = OUT / name
        path.mkdir()
        (path / 'core.cpp').write_text(code)
        sources[name] = path

result = {'kind': 'coordinator post-holdout arithmetic discriminator',
          'shape': [8, 32768, 127, 9],
          'timing_scope': 'whole process including preparation, allocation, computation, output',
          'repetitions': 7, 'quality': {}, 'timings': {}}
evaluator = ROOT / 'frozen/a/multichannel-fir/private/evaluate.py'
for name, path in sources.items():
    command = ['python3', '-B', str(evaluator), str(path)]
    run = subprocess.run(command, capture_output=True, text=True)
    result['quality'][name] = dict(command=command, returncode=run.returncode,
                                   stdout=run.stdout, stderr=run.stderr)
    assert run.returncode == 0, name

with tempfile.TemporaryDirectory() as tmp:
    for label, flags in [('fixture-O2', ['-O2', '-std=c++17']),
                         ('native-O3', ['-O3', '-march=native', '-std=c++17'])]:
        exes = {}
        records = {}
        for name, path in sources.items():
            exe = Path(tmp) / name
            command = ['g++', *flags, str(path / 'core.cpp'), '-o', str(exe)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            exes[name] = exe
            records[name] = {'compile': command, 'observations': []}
        names = list(exes)
        for rep in range(result['repetitions']):
            order = names[rep % len(names):] + names[:rep % len(names)]
            if rep % 2:
                order.reverse()
            for name in order:
                command = [str(exes[name]), *map(str, result['shape'])]
                start = time.perf_counter()
                run = subprocess.run(command, capture_output=True, text=True, check=True)
                elapsed = time.perf_counter() - start
                records[name]['observations'].append(
                    dict(repetition=rep, elapsed_s=elapsed, output=json.loads(run.stdout)))
        for record in records.values():
            record['median_s'] = statistics.median(x['elapsed_s'] for x in record['observations'])
        result['timings'][label] = records
(OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({label: {name: rec['median_s'] for name, rec in rows.items()}
                  for label, rows in result['timings'].items()}, indent=2))
