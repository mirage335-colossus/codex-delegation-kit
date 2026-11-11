import json
import math
import pathlib
import struct
import subprocess
import sys
import tempfile
import time

root = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / "core.cpp"
width, height, seed = 41, 29, 37
n = width * height
scores = []
buckets = [[0.0, 0.0, 0] for _ in range(32)]

def input_value(pixel, channel, seed_value):
    v = (pixel * 747796405 + channel * 2891336453 + seed_value * 277803737) & 0xffffffff
    shift = (v >> 28) + 4
    v = (((v >> shift) ^ v) * 277803737) & 0xffffffff
    v = (v >> 22) ^ v
    value = (v & 0x00ffffff) / 16777215.0
    return struct.unpack("f", struct.pack("f", value))[0]

def norm(value):
    return value / (1.0 + abs(value))

for pixel in range(n):
    x = [input_value(pixel, c, seed) for c in range(8)]
    a = norm(x[0]*x[1] + 0.35*x[2]*x[3] - 0.20*x[4] - 0.17)
    b = norm(x[5]*x[6] - 0.25*x[7] + 0.10*x[0] - 0.13)
    d0, d1 = x[3]-x[7], x[1]-x[6]
    z = (0.12 + 0.66*x[0] - 0.39*x[1] + 0.31*x[2]*x[4] - 0.27*x[5]
         + 0.45*a - 0.26*b + 0.13*a*b + 0.17*d0*d0 - 0.08*d1*d1)
    score = 0.5 + 0.5*z/(1.0+abs(z))
    scores.append(score)
    row = buckets[pixel % 32]
    row[0] += score
    row[1] += score*score
    row[2] += int(score >= 0.5)
ids = [0, n//17, n//5, n//2, 3*n//4, 16*n//17, n-1]

with tempfile.TemporaryDirectory() as temp_dir:
    executable = pathlib.Path(temp_dir) / "pixel-classifier"
    subprocess.run(["c++", "-O3", "-std=c++17", "-DNDEBUG", "-march=native", str(source), "-o", str(executable)], check=True)
    start = time.perf_counter()
    proc = subprocess.run([str(executable), str(width), str(height), str(seed)], capture_output=True, text=True, check=True)
    elapsed = time.perf_counter() - start
result = json.loads(proc.stdout)
assert result["storage_bytes"] <= 140 * 1024 * 1024
assert len(result["samples"]) == len(ids) and len(result["checksums"]) == 32
assert all(math.isfinite(v) for v in result["samples"])
assert all(len(row) == 3 and all(math.isfinite(v) for v in row) for row in result["checksums"])
expected = [scores[i] for i in ids]
assert max(abs(a-b) for a,b in zip(result["samples"], expected)) <= 2e-5
for b in range(32):
    count = (n + 31 - b) // 32
    assert abs(result["checksums"][b][0] - buckets[b][0]) / count <= 2e-5
    assert abs(result["checksums"][b][1] - buckets[b][1]) / count <= 2e-5
    assert abs(result["checksums"][b][2] - buckets[b][2]) <= 4
print(json.dumps({"public_smoke":"PASS", "pixels":n, "storage_bytes":result["storage_bytes"], "elapsed_seconds":elapsed, "samples":len(ids), "checksum_buckets":32}))
