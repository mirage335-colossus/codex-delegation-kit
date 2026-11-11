import json, math, pathlib, resource, subprocess, time
root = pathlib.Path(__file__).resolve().parent
subprocess.run(['g++', '-O2', '-std=c++17', 'core.cpp', '-o', 'probe'], cwd=root, check=True)
weights = [.5, .75, 1., 1.25, 1.5, 1.75, 2., 2.25]

def reference(events, seed):
    result = []
    for c, weight in enumerate(weights):
        first = ((c - seed % 8) * 5) % 8
        count = 0 if first >= events else (events - 1 - first) // 8 + 1
        sum_indices_plus_one = count * (2 * (first + 1) + 8 * (count - 1)) // 2 if count else 0
        prior = (1 << 53) + c * 4096 + seed % 31
        result.append((prior + count, weight * .001 * sum_indices_plus_one))
    return result

def run(events, seed):
    p = subprocess.run([str(root / 'probe'), str(events), str(seed)], cwd=root,
                       capture_output=True, text=True, check=True, timeout=4)
    fields = p.stdout.split()
    if len(fields) != 16:
        return None
    return [(int(fields[2*c]), float(fields[2*c+1])) for c in range(8)]

def quality(actual, expected):
    if actual is None:
        return False, False
    exact = all(a[0] == e[0] for a, e in zip(actual, expected))
    scores = all(math.isfinite(a[1]) and abs(a[1]-e[1]) <= max(.01, 1e-6*abs(e[1]))
                 for a, e in zip(actual, expected))
    return exact, scores

checks = {}
for events, seed in [(1, 7), (31, 0x12345678), (1003, (1 << 63) + 11)]:
    actual = run(events, seed)
    exact, scores = quality(actual, reference(events, seed))
    checks[f'{events}_exact_counts'] = exact
    checks[f'{events}_weighted_scores'] = scores
seed = (1 << 63) + 37
full = run(6000000, seed)
exact, scores = quality(full, reference(6000000, seed))
checks['full_exact_counts'] = exact
checks['full_weighted_scores'] = scores
code = ('import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True); '
        'sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); '
        'print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss); '
        'sys.exit(p.returncode)')
t0=time.monotonic()
p=subprocess.run(['python3','-B','-c',code,str(root/'probe'),'6000000',str(seed)],
                 cwd=root,capture_output=True,text=True,check=True,timeout=4)
elapsed=time.monotonic()-t0
rss=int(p.stdout.split('CHILD_RSS_KIB')[-1].strip())
checks['full_capture_rss_le_40_mib'] = rss <= 40960
checks['full_capture_handoff_deadline'] = elapsed <= 1.0
print(json.dumps({'checks':checks,'peak_rss_kib':rss,'elapsed_s':round(elapsed,4)}))
assert all(checks.values()), 'one or more event count, score, or capacity checks failed'
print('PASS full archive count and score oracle')
