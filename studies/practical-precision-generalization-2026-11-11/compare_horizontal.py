"""One bounded diagnostic of j21's remaining horizontal promotions."""
from pathlib import Path
import json
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'horizontal-diagnostic'
OUT.mkdir(exist_ok=True)
if (OUT / 'results.json').exists():
    raise SystemExit('Refusing to replace original diagnostic')
original = (ROOT / 'runs/j21/submitted/core.cpp').read_text()
assert original.count('const double q=image[row+') == 3
narrow = original.replace('const double q=image[row+', 'const float q=image[row+')
sources = {'submitted-mixed': original, 'fp32-horizontal': narrow}
result = {'kind': 'coordinator diagnostic, not autonomous review or repair',
          'flags': ['-O3', '-std=c++17', '-DNDEBUG', '-march=native'],
          'shape': ['1280', '960', '7301', '15'], 'quality': {}, 'timings': {}}
for name, code in sources.items():
    path = OUT / name
    path.mkdir()
    (path / 'core.cpp').write_text(code)
    command = ['python3', '-B', str(ROOT / 'frozen/h/area-inspection/private/evaluate.py'), str(path)]
    run = subprocess.run(command, capture_output=True, text=True)
    result['quality'][name] = dict(command=command, returncode=run.returncode,
                                  stdout=run.stdout, stderr=run.stderr)
    assert run.returncode == 0, name
with tempfile.TemporaryDirectory() as td:
    exes = {}
    for name in sources:
        exe = Path(td) / name
        command = ['c++', *result['flags'], str(OUT / name / 'core.cpp'), '-o', str(exe)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        exes[name] = exe
        result['timings'][name] = {'compile': command, 'observations': []}
    for rep in range(9):
        order = list(exes) if rep % 2 == 0 else list(reversed(exes))
        for name in order:
            start = time.perf_counter()
            run = subprocess.run([str(exes[name]), *result['shape']], check=True,
                                 capture_output=True, text=True)
            elapsed = time.perf_counter()-start
            result['timings'][name]['observations'].append(
                {'repetition': rep, 'elapsed_s': elapsed, 'output': json.loads(run.stdout)})
    for row in result['timings'].values():
        row['median_s'] = statistics.median(r['elapsed_s'] for r in row['observations'])
    a=result['timings']['submitted-mixed']['observations']
    b=result['timings']['fp32-horizontal']['observations']
    deltas=[left['elapsed_s']-right['elapsed_s'] for left,right in zip(a,b)]
    result['paired_differences_s']=deltas
    result['narrow_wins']=sum(d>0 for d in deltas)
(OUT / 'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'medians':{k:v['median_s'] for k,v in result['timings'].items()},
                  'narrow_wins':result['narrow_wins'], 'paired_differences_s':deltas},indent=2))
