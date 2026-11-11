import json, math, pathlib, struct, subprocess, sys, tempfile, time
src = pathlib.Path(sys.argv[1]).resolve() / 'core.cpp'

def f32(value):
    return struct.unpack('f', struct.pack('f', value))[0]

def reference(blocks, seed, profile):
    out = []
    for c in range(8):
        level = f32(.125 * (c + 1) + .03125 * (seed % 5))
        if profile == 'normal':
            cycle = [f32(level + ((slot % 5) - 2) * .03125) for slot in range(130)]
        else:
            peak = f32(10_000_000 + c * 1024 + seed % 17)
            cycle = [peak] + [level] * 128 + [-peak]
        total = blocks * math.fsum(cycle)
        squares = blocks * math.fsum(v * v for v in cycle)
        out.extend((total, math.sqrt(squares / (blocks * 130))))
    return out

def compare(actual, expected):
    if len(actual) != 16 or not all(math.isfinite(x) for x in actual):
        return False
    for c in range(8):
        total, rms = actual[2*c:2*c+2]
        target_total, target_rms = expected[2*c:2*c+2]
        if abs(total - target_total) > max(.05, 2e-7 * abs(target_total)):
            return False
        if abs(rms - target_rms) > max(.1, 2e-7 * abs(target_rms)):
            return False
    return True

with tempfile.TemporaryDirectory() as td:
    exe = pathlib.Path(td) / 'candidate'
    subprocess.run(['g++', '-O2', '-std=c++17', str(src), '-o', str(exe)], check=True)
    checks, observations = {}, {}
    cases = [(1, 7, 'normal'), (19, 0x12345678, 'transient'),
             (4097, 0xABCDEF01, 'normal'), (4097, 0xABCDEF01, 'transient')]
    for blocks, seed, profile in cases:
        p = subprocess.run([str(exe), str(blocks), str(seed), profile], capture_output=True,
                           text=True, check=True, timeout=4)
        actual = list(map(float, p.stdout.split()))
        key = f'{blocks}_{profile}_seed_{seed}'
        checks[key] = compare(actual, reference(blocks, seed, profile))
        observations[key] = actual

    code = ('import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True); '
            'sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); '
            'print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss); '
            'sys.exit(p.returncode)')
    blocks, seed = 12000, (1 << 63) + 37
    for profile in ('normal', 'transient'):
        t0 = time.monotonic()
        p = subprocess.run(['python3', '-B', '-c', code, str(exe), str(blocks), str(seed), profile],
                           capture_output=True, text=True, check=True, timeout=4)
        elapsed = time.monotonic() - t0
        actual = list(map(float, p.stdout.split('CHILD_RSS_KIB')[0].split()))
        rss_kib = int(p.stdout.split('CHILD_RSS_KIB')[-1].strip())
        checks[f'full_capture_{profile}_outputs'] = compare(actual, reference(blocks, seed, profile))
        checks[f'full_capture_{profile}_memory'] = rss_kib <= 24576
        observations[f'full_capture_{profile}'] = {
            'rss_kib': rss_kib, 'elapsed_s': round(elapsed, 4), 'outputs': actual}
    passed = all(checks.values())
    print(json.dumps({'passed': passed, 'checks': checks, 'observations': observations}))
    raise SystemExit(0 if passed else 1)
