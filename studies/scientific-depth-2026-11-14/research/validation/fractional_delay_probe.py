"""Tiny independent check of pumpModem's documented windowed-sinc delay kernel.

No pump sources are compiled; this re-expresses interpolate()'s 16-tap
Blackman-windowed sinc formula on complex samples to inspect phase, support,
history and amplitude normalization boundaries.
"""
from cmath import exp, phase
from math import cos, floor, log10, pi, sin, sqrt

OFFSETS = range(-7, 9)

def interp(x, p, first=0, end=None):
    if end is None:
        end = len(x)
    if not (-8 <= p < end + 8):
        return 0j
    def sample(index):
        return x[index] if first <= index < end else 0j
    if p == floor(p) and p >= 0:
        return sample(int(p))
    center = floor(p)
    value, norm = 0j, 0.0
    for offset in OFFSETS:
        tap = center + offset
        d = p - tap
        if abs(d) >= 8:
            continue
        z = (d + 8) / 16
        window = 0.42 - 0.5*cos(2*pi*z) + 0.08*cos(4*pi*z)
        coeff = (1.0 if abs(d) < 1e-12 else sin(pi*d)/(pi*d))*window
        if 0 <= tap < end:
            value += coeff * sample(tap)
        norm += coeff
    return value/norm if abs(norm) > 1e-12 else 0j

def rms(xs):
    return sqrt(sum(abs(z)**2 for z in xs)/len(xs))

# Complex tones: ratio to exact analytic delayed sample, well away from edges.
N, delay = 256, 8.25
print("COMPLEX TONE RESPONSE: Fs=1 sample-unit; fractional delay=8.25 samples")
print("freq_cycles_per_sample  gain_dB  residual_phase_deg  implied_delay_error_samples")
for f in (0.01, 0.05, 0.125, 0.20, 0.35, 0.45):
    x = [exp(2j*pi*f*k) for k in range(N)]
    ratios = [interp(x, n-delay)/exp(2j*pi*f*(n-delay)) for n in range(80, 180)]
    h = sum(ratios)/len(ratios)
    delay_error = -phase(h)/(2*pi*f)
    print(f"{f:22.3f} {20*log10(abs(h)):8.4f} {phase(h)*180/pi:19.4f} {delay_error:28.6f}")

# A discrete impulse shows the finite interpolation kernel's temporal support.
print("\nIMPULSE SUPPORT: x[64]=1, y[n]=interp(x,n-delay); threshold 1e-12")
for delay in (8.0, 3.25, 8.25, 12.25):
    x = [0j]*128
    x[64] = 1+0j
    ys = [interp(x, n-delay) for n in range(128)]
    nz = [n for n,y in enumerate(ys) if abs(y)>1e-12]
    peak = max(abs(y) for y in ys)
    energy = sum(abs(y)**2 for y in ys)
    print(f"delay={delay:5.2f}: first={min(nz):3d}, last={max(nz):3d}, input_index=64, peak={peak:.8f}, output_energy={energy:.8f}")

# Initial zero-history boundary: a complex tone turns on at sample 0, so a
# strict causal delay has no output before n >= delay. The centered 16-tap
# interpolator can expose a finite precursor even with zero-filled history.
print("\nINITIALIZATION: unit complex tone begins at sample 0; nominal delay=8.25")
x = [exp(2j*pi*0.125*k) for k in range(64)]
ys = [interp(x, n-8.25) for n in range(24)]
pre = [(n, abs(y)) for n,y in enumerate(ys) if n < 8.25 and abs(y) > 1e-12]
print(f"strict-causal pre-arrival outputs={len(pre)}; first={pre[0] if pre else 'none'}; max_pre={max((v for _,v in pre), default=0):.8f}")
print("The source initializes its bounded history with zeros; interpreting this precursor requires the actual signal's occupied-band and source-ramp assumptions.")


# A continuous stateful history and a deliberately broken per-chunk history.
# The latter models a caller that drops source samples before each read boundary.
print("\nCHUNK HISTORY CHECK: complex tone plus impulse, chunk sizes 16 and 31")
x = [exp(2j*pi*0.125*k) for k in range(160)]
x[73] += 0.7-0.2j
for chunk in (16, 31):
    full = [interp(x, n-delay) for n in range(160)]
    reset = []
    for n in range(160):
        lo = (n//chunk)*chunk
        reset.append(interp(x, n-delay, first=lo, end=min(lo+chunk, len(x))))
    delta = [abs(a-b) for a,b in zip(full, reset)]
    large = [(n,d) for n,d in enumerate(delta) if d > 1e-9]
    print(f"chunk={chunk:2d}: differing_outputs={len(large):3d}, max_abs_error={max(delta):.8g}, first={large[0][0] if large else 'none'}")

# Gain is a physical boundary: the kernel's coefficient-sum normalization is
# not whole-capture signal normalization.
print("\nGAIN NORMALIZATION CHECK: g=0.5 before interpolation; fixed source noise omitted")
x = [exp(2j*pi*0.125*k) for k in range(128)]
y = [interp(x, n-delay) for n in range(32, 96)]
y_half = [interp([0.5*z for z in x], n-delay) for n in range(32, 96)]
print(f"unit_gain_rms={rms(y):.8f}; half_gain_rms={rms(y_half):.8f}; ratio={rms(y_half)/rms(y):.8f}")
print(f"if each output were renormalized back to input RMS, half_gain would become {0.5*rms(y)/rms(y_half):.3f}x larger (signal-level evidence erased)")
