"""Matched developmental diagnostic; separate from frozen product checks."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ids', nargs='+')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    sources = {'witness': ROOT / 'frozen/c/burst/private/witness/core.cpp'}
    sources.update({i: ROOT / 'runs' / i / 'submitted/core.cpp' for i in args.ids})
    records = {k: [] for k in sources}
    with tempfile.TemporaryDirectory(prefix='precision-burst-compare-') as td:
        bins = {}
        for k, src in sources.items():
            out = Path(td) / k
            cmd = ['g++', '-O3', '-std=c++17', str(src),
                   str(ROOT / 'frozen/c/burst/private/heap_probe.cpp'), '-o', str(out)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            bins[k] = out
        # Complete invocation includes initialization, allocation, computation
        # and output. Each process uses the actual automatic/default route.
        order = list(bins)
        for rep in range(4):
            for k in (order if rep % 2 == 0 else list(reversed(order))):
                start = time.perf_counter()
                p = subprocess.run([str(bins[k]), '5', '5000000'], capture_output=True,
                                   text=True, check=True, timeout=15)
                elapsed = time.perf_counter()-start
                fields = dict(re.findall(r'([A-Za-z_][A-Za-z_0-9]*)=([^\s]+)', p.stdout))
                heap = int(re.search(r'heap_peak_bytes=(\d+)', p.stderr).group(1))
                records[k].append(dict(repetition=rep, whole_process_s=elapsed,
                    measured_heap_bytes=heap, scores=[float(fields[f'score{n}']) for n in range(5)],
                    stdout=p.stdout, stderr=p.stderr))
    reference = records['witness'][0]['scores']
    for k, rows in records.items():
        for row in rows:
            row['matches_qualified_witness_tolerance'] = all(
                abs(a-b) <= .002 + .00002*abs(b) for a, b in zip(row['scores'], reference))
    result = dict(scope='developmental same-shape diagnostic, not frozen product acceptance',
        flags=['-O3', '-std=c++17'], shape=[5,5000000], route='no flag/automatic',
        sources={k:dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for k,p in sources.items()},
        observations=records, medians_s={k:statistics.median(r['whole_process_s'] for r in v) for k,v in records.items()})
    (ROOT / args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['medians_s']))
