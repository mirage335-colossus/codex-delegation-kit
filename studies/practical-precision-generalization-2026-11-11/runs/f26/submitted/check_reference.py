#!/usr/bin/env python3
import pathlib
import re
import struct
import subprocess

exe = pathlib.Path('/tmp/review-worker-f26')
f32 = lambda value: struct.unpack('f', struct.pack('f', value))[0]

for count in (11, 1003):
    total = 0.0
    weighted = 0.0
    for i in range(count):
        h = (i * 1664525 + 1013904223) & 0xffffffff
        sample = (h % 60001) - 30000
        normalized = f32(f32(sample) * f32(1.0 / 32768.0))
        output = f32(f32(normalized * f32(0.75)) + f32(0.125))
        total += output
        weighted += output * (i % 97 + 1)

    for args in ([str(count)], [str(count), '--deny-avx2']):
        output = subprocess.run([str(exe), *args], check=True, text=True,
                                capture_output=True).stdout
        fields = dict(re.findall(r'(\w+)=([^ ]+)', output))
        got_total = float(fields['checksum'])
        got_weighted = float(fields['weighted'])
        assert abs(got_total - total) <= 0.01 + 0.00001 * abs(total)
        assert abs(got_weighted - weighted) <= 0.01 + 0.00001 * abs(weighted)
        assert int(fields['outputs']) == count
        print(f"count={count} selected={fields['selected']} ref=pass")
