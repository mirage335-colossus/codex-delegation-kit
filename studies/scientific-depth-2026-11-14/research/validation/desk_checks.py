"""Reproducible desk checks for statistical validation design; no modem code/data."""
from math import log, log10

alpha = 0.05
print("zero observed failures: exact one-sided 95% binomial upper bound")
for n in (30, 100, 300, 1000):
    upper = 1 - alpha ** (1 / n)
    approx = -log(alpha) / n
    print(f"n={n:4d}: exact={upper:.6%}; rule-of-three={3/n:.6%}; exp approximation={approx:.6%}")

print("\nAR(1) illustrative autocorrelation penalty for mean uncertainty")
rho = 0.9
for n in (100, 1000, 10000):
    design_effect = 1 + 2 * sum((1-k/n) * rho**k for k in range(1, n))
    n_eff = n / design_effect
    print(f"n={n:5d}, rho={rho}: n_eff={n_eff:.2f}, variance inflation={design_effect:.2f}x")

print("\nnoise-bandwidth conversion at 290 K, using kT0 = -203.98 dBW/Hz")
for bw in (2400, 12000):
    n0_dbm_hz = -173.98
    noise_dbm = n0_dbm_hz + 10 * log10(bw)
    print(f"B={bw:5d} Hz: thermal noise={noise_dbm:.2f} dBm; SNR=(C/N0)-{10*log10(bw):.2f} dB")

print("\npaired comparison with shared additive calibration error")
for common_error in (-2.0, 0.0, 2.0):
    baseline, candidate = -110 + common_error, -108 + common_error
    print(f"shared error={common_error:+.1f} dB: absolute baseline={baseline:.1f}, candidate={candidate:.1f}, paired delta={candidate-baseline:.1f} dB")
print("\nindependent zero-event trials needed to bound a failure probability at 95% one-sided confidence")
for target in (0.01, 0.001, 0.0001):
    n = int(log(alpha) / log(1-target)) + 1
    achieved = 1 - alpha**(1/n)
    print(f"target={target:.4%}: n={n}; zero-event upper={achieved:.6%}")
