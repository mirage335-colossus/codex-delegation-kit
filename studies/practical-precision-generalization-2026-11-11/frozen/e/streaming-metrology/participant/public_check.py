import math, pathlib, struct, subprocess, time
root = pathlib.Path(__file__).resolve().parent
subprocess.run(['g++', '-O2', '-std=c++17', 'core.cpp', '-o', 'probe'], cwd=root, check=True)

def f32(value):
    return struct.unpack('f', struct.pack('f', value))[0]

def reference(blocks, seed, profile):
    results = []
    for c in range(8):
        level = f32(.125 * (c + 1) + .03125 * (seed % 5))
        if profile == 'normal':
            cycle = [f32(level + ((slot % 5) - 2) * .03125) for slot in range(130)]
        else:
            peak = f32(10_000_000 + c * 1024 + seed % 17)
            cycle = [peak] + [level] * 128 + [-peak]
        total = blocks * math.fsum(cycle)
        squares = blocks * math.fsum(v * v for v in cycle)
        results.append((total, math.sqrt(squares / (blocks * 130))))
    return results

def run(blocks, seed, profile):
    p = subprocess.run([str(root / 'probe'), str(blocks), str(seed), profile], cwd=root,
                       text=True, capture_output=True, check=True, timeout=4)
    values = list(map(float, p.stdout.split()))
    assert len(values) == 16 and all(math.isfinite(v) for v in values), 'expected 8 finite total/RMS pairs'
    return [tuple(values[i:i + 2]) for i in range(0, 16, 2)]

def quality(actual, expected):
    return all(abs(a[0] - e[0]) <= max(.05, 2e-7 * abs(e[0])) and
               abs(a[1] - e[1]) <= max(.1, 2e-7 * abs(e[1]))
               for a, e in zip(actual, expected))

checks = {}
for blocks, seed, profile in [(1, 7, 'normal'), (19, 0x12345678, 'transient')]:
    actual = run(blocks, seed, profile)
    checks[f'{blocks}_{profile}_quality'] = quality(actual, reference(blocks, seed, profile))
seed = (1 << 63) + 37
for profile in ('normal', 'transient'):
    actual = run(12000, seed, profile)
    checks[f'full_{profile}_quality'] = quality(actual, reference(12000, seed, profile))
code = ('import sys,subprocess,resource; p=subprocess.run(sys.argv[1:],capture_output=True,text=True); '
        'sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); '
        'print("CHILD_RSS_KIB",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss); '
        'sys.exit(p.returncode)')
t0 = time.monotonic()
measured = subprocess.run(['python3', '-B', '-c', code, str(root / 'probe'), '12000', str(seed), 'transient'],
                          cwd=root, text=True, capture_output=True, check=True, timeout=4)
elapsed = time.monotonic() - t0
rss_kib = int(measured.stdout.split('CHILD_RSS_KIB')[-1].strip())
checks['peak_rss_le_24_mib'] = rss_kib <= 24576
print({'checks': checks, 'peak_rss_kib': rss_kib, 'elapsed_s': round(elapsed, 4)})
assert all(checks.values()), 'one or more calibration quality/capacity checks failed'
print('PASS normal and transient full output oracles')
