import json, math, pathlib, subprocess, sys, tempfile, time
src = pathlib.Path(sys.argv[1]).resolve() / 'core.cpp'
weights = [.5, .75, 1., 1.25, 1.5, 1.75, 2., 2.25]

def reference(events, seed):
    result = []
    for c, weight in enumerate(weights):
        first = ((c - seed % 8) * 5) % 8
        count = 0 if first >= events else (events - 1 - first) // 8 + 1
        sum_values = count * (2 * (first + 1) + 8 * (count - 1)) // 2 if count else 0
        prior = (1 << 53) + c * 4096 + seed % 31
        result.append((prior + count, weight * .001 * sum_values))
    return result

def compare(stdout, expected):
    fields = stdout.split()
    if len(fields) != 16:
        return {'exact_counts': False, 'weighted_scores': False, 'details': 'expected 16 fields'}
    exact = True
    score_ok = True
    errors = []
    for c, (count, score) in enumerate(expected):
        try:
            actual_count = int(fields[2*c])
            actual_score = float(fields[2*c+1])
        except ValueError:
            return {'exact_counts': False, 'weighted_scores': False, 'details': f'invalid fields class {c}'}
        if actual_count != count:
            exact = False
            errors.append(f'class {c} count {actual_count} != {count}')
        if not math.isfinite(actual_score) or abs(actual_score-score) > max(.01, 1e-6*abs(score)):
            score_ok = False
            errors.append(f'class {c} score {actual_score} vs {score}')
    return {'exact_counts': exact, 'weighted_scores': score_ok, 'details': errors[:4]}

with tempfile.TemporaryDirectory() as td:
    exe = pathlib.Path(td) / 'candidate'
    subprocess.run(['g++', '-O2', '-std=c++17', str(src), '-o', str(exe)], check=True)
    checks, observations = {}, {}
    cases = [(1, 7), (31, 0x12345678), (1003, (1 << 63) + 11)]
    for events, seed in cases:
        p = subprocess.run([str(exe), str(events), str(seed)], capture_output=True,
                           text=True, check=True, timeout=4)
        result = compare(p.stdout, reference(events, seed))
        key = f'{events}_events_seed_{seed}'
        checks[key] = result['exact_counts'] and result['weighted_scores']
        observations[key] = result

    events, seed = 6000000, (1 << 63) + 37
    code = ('import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True); '
            'sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); '
            'print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss); '
            'sys.exit(p.returncode)')
    t0 = time.monotonic()
    p = subprocess.run(['python3', '-B', '-c', code, str(exe), str(events), str(seed)],
                       capture_output=True, text=True, check=True, timeout=4)
    elapsed = time.monotonic() - t0
    stdout = p.stdout.split('CHILD_RSS_KIB')[0]
    rss = int(p.stdout.split('CHILD_RSS_KIB')[-1].strip())
    result = compare(stdout, reference(events, seed))
    checks['full_archive_exact_counts'] = result['exact_counts']
    checks['full_archive_weighted_scores'] = result['weighted_scores']
    checks['full_archive_rss_le_40_mib'] = rss <= 40960
    checks['full_archive_handoff_deadline'] = elapsed <= 1.0
    observations['full_archive'] = {**result, 'rss_kib': rss, 'elapsed_s': round(elapsed, 4)}
    passed = all(checks.values())
    print(json.dumps({'passed': passed, 'checks': checks, 'observations': observations}))
    raise SystemExit(0 if passed else 1)
