import json, math, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parent
w, h, seed = 160, 90, 17
n = w * h
buckets = [[0.0, 0.0] for _ in range(16)]
samples = []
ids = [0, n // 7, n // 2, (n * 5) // 7, n - 1]
for p in range(n):
    k = (p * 1664525 + seed * 1013904223) & 0xffffffff
    bg = [((k >> 3) & 1023) / 1023.0, ((k >> 13) & 1023) / 1023.0, ((k >> 23) & 255) / 255.0]
    fg = [((k >> 7) & 511) / 511.0, ((k >> 17) & 511) / 511.0, ((k >> 27) & 31) / 31.0]
    a = ((k >> 10) & 255) / 255.0
    vals = [fg[c] * a + bg[c] * (1.0 - a) for c in range(3)] + [1.0]
    for c, v in enumerate(vals):
        b = (4 * p + c) % 16
        buckets[b][0] += v
        buckets[b][1] += v * v
    if p in ids:
        samples.append(vals)

with tempfile.TemporaryDirectory(dir=root) as td:
    exe = pathlib.Path(td) / 'double_probe'
    subprocess.run(['c++', '-O2', '-std=c++17', '-DVALUE=double', str(root / 'core.cpp'), '-o', str(exe)], check=True)
    result = json.loads(subprocess.run([str(exe), str(w), str(h), str(seed)], check=True, capture_output=True, text=True).stdout)
    sample_error = max(abs(got - ref) for row, refrow in zip(result['samples'], samples) for got, ref in zip(row, refrow))
    checksum_error = max(abs(result['checksums'][b][j] - buckets[b][j]) / ((4 * n + 15 - b) // 16) for b in range(16) for j in range(2))
    assert sample_error <= 2e-9, sample_error
    assert checksum_error <= 2e-8, checksum_error
    print(json.dumps({'diagnostic_double': 'PASS', 'max_sample_error': sample_error, 'max_checksum_error_per_output_scalar': checksum_error, 'storage_bytes_reported': result['storage_bytes']}))
