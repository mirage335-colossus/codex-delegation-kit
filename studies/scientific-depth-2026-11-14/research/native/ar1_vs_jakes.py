#!/usr/bin/env python3
"""Reproducible desk check: a lag-one-matched AR(1) is not Jakes fading."""
import math


def j0(x: float) -> float:
    """Power series for J0(x), adequate for the x<=2*pi check below."""
    term = 1.0
    total = term
    quarter_x2 = x * x / 4.0
    for m in range(1, 80):
        term *= -quarter_x2 / (m * m)
        total += term
        if abs(term) <= 2.0e-16 * max(1.0, abs(total)):
            break
    return total


print("fd*dt lag Jakes_R AR1_lag1_matched_R abs_error")
for normalized_doppler in (0.01, 0.05):
    rho = j0(2.0 * math.pi * normalized_doppler)
    for lag in (1, 5, 10, 20):
        target = j0(2.0 * math.pi * normalized_doppler * lag)
        ar1 = rho**lag
        print(f"{normalized_doppler:.2f} {lag:>3} {target: .9f} {ar1: .9f} {abs(target-ar1):.9f}")
