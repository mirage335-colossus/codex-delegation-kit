#!/usr/bin/env python3
"""Reproducible conversions for HF scenario planning; no external data/packages."""
from math import sqrt, pi, log

C_KM_S = 299_792.458

def gaussian_channel(width_2sigma_hz):
    """F.1487 convention B=2 sigma; proper complex process R(t)=exp(-2pi^2 sigma^2 t^2)."""
    B = width_2sigma_hz
    sigma = B / 2
    fwhm = 2 * sqrt(2 * log(2)) * sigma
    central_80 = 2 * 1.2815515655446004 * sigma
    e_fold = sqrt(2) / (pi * B) if B else float('inf')
    return sigma, fwhm, central_80, e_fold

print("F.1487 Gaussian width conversion; B=2sigma")
print("B_hz,sigma_hz,fwhm_hz,central80_hz,complex_gain_e_fold_s")
for b in (.1, .5, 1.0, 3.0, 10.0, 30.0):
    sigma, fwhm, central80, e_fold = gaussian_channel(b)
    print(f"{b:.3f},{sigma:.6f},{fwhm:.6f},{central80:.6f},{e_fold:.6f}")
print("\nDelay-to-free-space excess path conversion (not ionospheric altitude)")
print("delay_ms,excess_path_km")
for ms in (.1, .5, 1, 2, 3, 5, 7):
    print(f"{ms:.3f},{C_KM_S*ms/1000:.3f}")
