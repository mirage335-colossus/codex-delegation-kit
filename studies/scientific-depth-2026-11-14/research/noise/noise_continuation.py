#!/usr/bin/env python3
"""Reproducible, conditional noise-tail, correlation, sampling/filter checks.
No project signal or receiver is simulated here.
"""
import math

def db(x):
    return 10.0 * math.log10(x) if x > 0 else float('-inf')

def gaussian_two_sided(z):
    return math.erfc(z / math.sqrt(2.0))

print('SAME-RMS TAIL COMPARISON (analytic, signed real samples)')
# 22 dB above RMS is a voltage ratio in the historical APD normalization.
z = 10 ** (22 / 20)
print(f'22 dB above RMS amplitude = {z:.4f} RMS; signed-real Gaussian with σ=RMS exceedance={gaussian_two_sided(z):.3e}; complex-Gaussian Rayleigh envelope exceedance at r/RMS={math.exp(-z*z):.3e}')
for z0 in (3, 5, 10):
    print(f'Gaussian |x|>{z0} sigma: {gaussian_two_sided(z0):.6g}')

print('\nEQUAL COMPONENTS, POWER AT REFERENCE PLANE')
# Two zero-mean real components with variance P and correlation rho:
# var(x+y)=2P(1+rho). The complex proper/uncorrelated case obeys the same
# power-addition result componentwise; phase-sensitive coherence is retained by rho.
for rho in (-0.9, 0.0, 0.5, 0.9, 1.0):
    ratio = 2 * (1 + rho) # relative to one component
    print(f'rho={rho:+.1f}: total/one={ratio:.3f}; level vs one={db(ratio):+.3f} dB')

print('\nSAME-MEAN-POWER SPARSE-SAMPLE STRESS (illustrative, not measured)')
q = 1e-3
amp = 1 / math.sqrt(q)  # unit mean-square with zero between events
for z0 in (3, 5, 10):
    tail = q if amp > z0 else 0
    print(f'|x|>{z0} rms: sparse mixture={tail:.6g}, Gaussian={gaussian_two_sided(z0):.6g}, ratio={tail/gaussian_two_sided(z0):.3g}')
fs, duration = 4000, 16
n = fs * duration
print(f'4k sample/s x 16s: N={n}, expected sparse events={n*q:.1f}, P(at least one)={1-(1-q)**n:.9f}')
print('Event clustering/coloring changes peak, duration and independent-event count; fixed occupancy alone is not a temporal model.')

print('\nMODEM-SCALE CONDITIONAL FILTER/CLOCK CALCULATIONS')
fs, bw, duration = 960.0, 225.0, 16.0
edge = bw / 2
nyq = fs / 2
ratio = nyq / edge
oct = math.log2(ratio)
for dr in (40, 60, 80):
    order = dr / (6 * oct)
    print(f'ideal 6 dB/pole/octave estimate: fs={fs:g} Hz, occupied BW={bw:g} Hz, edge={edge:g} Hz, Nyquist={nyq:g} Hz, DR={dr} dB -> {order:.2f} poles')
print(f'filter transition ratio={ratio:.4f}, octaves={oct:.4f}; real RF/IF selectivity and blocker rejection need measured transfer.')
for ppm in (1, 10, 100):
    drift_s = duration * ppm * 1e-6
    samples = fs * drift_s
    print(f'sample clock {ppm} ppm over {duration:g}s: timing drift={drift_s*1e6:.3f} us, sample drift={samples:.6f}')
print(f'1 kHz occupancy bin/native {bw:g} Hz width ratio={1000/bw:.4f}; equal flat-PSD integrated noise differs by {db(1000/bw):.3f} dB; 1/10 spacing RBW bound for {bw:g} Hz channels={bw/10:g} Hz (ITU-R SM.2256 guidance for swept analyzer).')
# Giesbrecht et al. (2006) field-calibration expression: En=P_n+20log10(F_MHz)+108.5 dBµV/m.
f_mhz = 6.2
print(f'Giesbrecht loss-free antenna mapping offset at {f_mhz:g} MHz: 20log10(F)+108.5={20*math.log10(f_mhz)+108.5:.3f} dB; their chain gain/loss constant (149.7) is setup-specific.')
