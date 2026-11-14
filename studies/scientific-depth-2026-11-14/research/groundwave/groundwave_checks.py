#!/usr/bin/env python3
"""Reproducible groundwave reference/geometry checks; not a path simulator.

Sources and formula locators are in chapter.md.  These checks use only
standard-library arithmetic and intentionally do not implement propagation.
"""
from math import log10, sqrt

EPS0 = 8.854187817e-12

print("P.368-10 reference-field normalization")
e_dbuv_m = 20 * log10(300e-3 / 1e-6)  # 300 mV/m at 1 km
for f_mhz in (1.0, 30.0):
    lb_db = 142.0 + 20 * log10(f_mhz) - e_dbuv_m
    fspl_db = 32.45 + 20 * log10(f_mhz)  # d=1 km
    print(f"f={f_mhz:g} MHz: E={e_dbuv_m:.2f} dB(uV/m), "
          f"P.368 Lb={lb_db:.2f} dB, 1-km FSPL={fspl_db:.2f} dB, "
          f"difference={lb_db-fspl_db:+.3f} dB")

print("\nPower-loss dB to voltage/complex-IQ amplitude (fixed receive impedance)")
loss_db = 20.0
iq_amplitude_ratio = 10 ** (-loss_db / 20)
power_ratio = 10 ** (-loss_db / 10)
print(f"{loss_db:g} dB path power loss: apply IQ amplitude x{iq_amplitude_ratio:g}; "
      f"power x{power_ratio:g}; with fixed receiver noise variance, SNR shifts by "
      f"{-loss_db:g} dB")

print("\nConduction/displacement-current ratio sigma/(2*pi*f*epsilon0*epsilon_r)")
soils = (
    ("very-dry illustrative", 1e-4, 3.0),
    ("medium-dry illustrative", 1e-3, 15.0),
    ("wet illustrative", 1e-2, 30.0),
    ("average-salinity sea-water P.368 curve", 5.0, 70.0),
)
for name, sigma, er in soils:
    ratios = [sigma / (2 * 3.141592653589793 * f * 1e6 * EPS0 * er)
              for f in (1.0, 30.0)]
    print(f"{name}: sigma={sigma:g} S/m, eps_r={er:g}, "
          f"ratio@1MHz={ratios[0]:.3g}, ratio@30MHz={ratios[1]:.3g}")

print("\nGeometry screens; Earth effective radius k=4/3 (P.526 convention)")
for ht, hr in ((2.0, 2.0), (10.0, 2.0)):
    horizon_km = 4.12 * (sqrt(ht) + sqrt(hr))
    print(f"heights {ht:g} m/{hr:g} m: nominal refracted radio horizon="
          f"{horizon_km:.2f} km (frequency-independent geometry; no cutoff claim)")
for distance_km in (1.0, 10.0, 45.0):
    for f_mhz in (1.0, 30.0):
        r1_m = 550 * sqrt(distance_km / (4 * f_mhz))
        print(f"midpoint first-Fresnel radius, {distance_km:g} km at "
              f"{f_mhz:g} MHz: {r1_m:.1f} m")

print("\nInterpretation: the P.368 reference agrees with free-space loss at 1 km; "
      "this validates the reference convention only. Soil ratios show why "
      "frequency-specific complex ground properties matter. Horizon/Fresnel "
      "values screen geometry but do not model groundwave attenuation or "
      "declare reception impossible beyond the horizon.")
