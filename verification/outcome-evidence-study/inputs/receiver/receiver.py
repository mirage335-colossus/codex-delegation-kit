"""Simple simulated two-tone signal and aligned discriminator."""
import json
import math
import random
import time
from pathlib import Path

CASE_PATH = Path(__file__).with_name('cases.json')
TONES = (64.0, 128.0)


def load_cases(path=CASE_PATH):
    return json.loads(Path(path).read_text())


def synthesize(case):
    """Return a stream with a delayed noisy signal. Case contains the truth."""
    rng = random.Random(case['seed'])
    sr, n = case['sample_rate'], case['symbol_samples']
    lead = case['leading_samples']
    total = lead + n * len(case['bits']) + n // 2
    samples = [rng.gauss(0, case['noise_sigma']) for _ in range(total)]
    for k, bit in enumerate(case['bits']):
        frequency = TONES[int(bit)] + case['offset_hz']
        for j in range(n):
            i = lead + k * n + j
            samples[i] += case['amplitude'] * math.cos(2 * math.pi * frequency * i / sr)
    return samples


def energy(samples, start, count, frequency, sample_rate):
    """Coherent quadrature energy at one candidate frequency and interval."""
    re = im = 0.0
    for j in range(count):
        angle = 2 * math.pi * frequency * j / sample_rate
        re += samples[start + j] * math.cos(angle)
        im += samples[start + j] * math.sin(angle)
    return re * re + im * im


def aligned_decision(samples, start, count, sample_rate):
    energies = [energy(samples, start, count, f, sample_rate) for f in TONES]
    return int(energies[1] > energies[0])


def aligned_check(case):
    samples = synthesize(case)
    start = case['leading_samples']
    n = case['symbol_samples']
    return ''.join(str(aligned_decision(samples, start + k*n, n, case['sample_rate']))
                   for k in range(len(case['bits'])))


if __name__ == '__main__':
    case = load_cases()[0]
    start = time.perf_counter()
    decision = aligned_check(case)
    print('aligned check:', decision, 'expected:', case['bits'])
    print('elapsed seconds:', round(time.perf_counter() - start, 6))
