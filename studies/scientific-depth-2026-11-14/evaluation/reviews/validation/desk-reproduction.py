"""Independent standard-library checks for validation chapter arithmetic.

No pump code, datasets, or receiver are used. Formulas are derived directly
from the stated Bernoulli and stationary AR(1) assumptions.
"""
from math import log, log1p, log10

alpha = 0.05
print("one-sided 95% CP upper limit after zero failures")
for n in (30, 100, 300, 1000):
    upper = 1.0 - alpha ** (1.0 / n)
    print(f"n={n:4d}: {upper:.9%}")

print("\nminimum n with zero failures for target upper limit")
for target in (0.01, 0.001, 0.0001):
    n = int(log(alpha) / log1p(-target)) + 1
    upper = 1.0 - alpha ** (1.0 / n)
    print(f"target={target:.4%}: n={n}; attained={upper:.9%}")

print("\nfinite-n AR(1) variance inflation, closed geometric sums, rho=0.9")
rho = 0.9
for n in (100, 1000, 10000):
    s1 = rho * (1.0 - rho ** (n - 1)) / (1.0 - rho)
    s2 = rho * (1.0 - n * rho ** (n - 1) + (n - 1) * rho**n) / (1.0 - rho) ** 2
    design_effect = 1.0 + 2.0 * (s1 - s2 / n)
    print(f"n={n:5d}: design_effect={design_effect:.9f}; n_eff={n/design_effect:.9f}")

print("\nwhite thermal noise at 290 K using -173.98 dBm/Hz")
for bandwidth in (2400, 12000):
    print(f"B={bandwidth:5d} Hz: N={-173.98 + 10*log10(bandwidth):.9f} dBm; "
          f"SNR offset={10*log10(bandwidth):.9f} dB")
