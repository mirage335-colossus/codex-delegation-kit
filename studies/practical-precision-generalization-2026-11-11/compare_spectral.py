"""Bounded post-run discriminator, not participant evidence."""
from pathlib import Path
import json
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'spectral-diagnostic'
OUT.mkdir(exist_ok=True)
if (OUT / 'results.json').exists():
    raise SystemExit('Refusing to overwrite original diagnostic')
original = (ROOT / 'runs/h23/submitted/core.cpp').read_text()
start = original.index('static int automatic(')
end = original.index('static int run(', start)
body = original[start:end].replace('std::complex<double>', 'std::complex<float>')
body = body.replace('std::vector<double> taper(n);', 'std::vector<float> taper(n);')
assert body != original[start:end]
sources = {'submitted-fp64': original,
           'fp32-transform': original[:start] + body + original[end:]}
result = {'kind': 'coordinator discriminator, not autonomous behavior',
          'flags': ['-O3', '-std=c++17', '-Wall', '-Wextra', '-pedantic'],
          'shape': ['32', '4', '1024'], 'quality': {}, 'timings': {}}
for name, code in sources.items():
    path = OUT / name
    path.mkdir()
    (path / 'core.cpp').write_text(code)
    command = ['python3', '-B', str(ROOT / 'frozen/f/spectral-bank/private/evaluate.py'), str(path)]
    run = subprocess.run(command, capture_output=True, text=True)
    result['quality'][name] = dict(command=command, returncode=run.returncode,
                                  stdout=run.stdout, stderr=run.stderr)
    assert run.returncode == 0, name
with tempfile.TemporaryDirectory() as td:
    exes = {}
    for name in sources:
        exe = Path(td) / name
        command = ['g++', *result['flags'], str(OUT / name / 'core.cpp'), '-o', str(exe)]
        compile_run = subprocess.run(command, check=True, capture_output=True, text=True)
        exes[name] = exe
        result['timings'][name] = {'compile': command, 'compiler_stderr': compile_run.stderr,
                                  'whole_process_observations': []}
    for rep in range(11):
        order = list(exes) if rep % 2 == 0 else list(reversed(exes))
        for name in order:
            command = [str(exes[name]), *result['shape']]
            start = time.perf_counter()
            run = subprocess.run(command, check=True, capture_output=True, text=True)
            elapsed = time.perf_counter() - start
            header, _, data = run.stdout.partition(' values=')
            fields = dict(token.split('=', 1) for token in header.split())
            values = [float(x) for x in data.strip().split(',') if x]
            result['timings'][name]['whole_process_observations'].append(
                dict(repetition=rep, elapsed_s=elapsed, internal_s=float(fields['seconds']),
                     outputs=int(fields['outputs']), values=values))
    for row in result['timings'].values():
        row['median_s'] = statistics.median(x['elapsed_s'] for x in row['whole_process_observations'])
        row['internal_median_s'] = statistics.median(x['internal_s'] for x in row['whole_process_observations'])
    original_rows = result['timings']['submitted-fp64']['whole_process_observations']
    narrow_rows = result['timings']['fp32-transform']['whole_process_observations']
    ratios=[]
    for left,right in zip(original_rows,narrow_rows):
        assert len(left['values']) == len(right['values']) == 65664
        ratios.append(max(abs(a-b)/(0.001+0.00001*abs(a)) for a,b in zip(left['values'],right['values'])))
        assert ratios[-1] <= 1
        for row in (left,right):
            del row['values']  # Every-bin comparison retained as maximum ratio below.
    result['every_bin_max_tolerance_ratios'] = ratios
(OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({name: {key:row[key] for key in ['median_s','internal_median_s']}
                  for name,row in result['timings'].items()}, indent=2))
