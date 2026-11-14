#!/usr/bin/env python3
"""Reproducible conditional noise checks for the noise research branch.

P.372-17 external-noise category equations are used as predecessor-edition
illustrations only. They are not asserted unchanged in current P.372-18 and
do not cover VLF below 0.3 MHz or any named site.
"""
from math import log, log10, pi, exp

K = 1.380649e-23
T0 = 290.0
DBM_HZ = 10 * log10(K * T0 / 1e-3)

def p372_fa(c, d, f_mhz):
    return c - d * log10(f_mhz)

print(f"kT0={DBM_HZ:.3f} dBm/Hz (T0={T0:g} K)")
print("P.372-17 predecessor illustrative median external PSD and 3-kHz power")
cats = {
    "city": (76.8, 27.7),
    "residential": (72.5, 27.7),
    "rural": (67.2, 27.7),
    "quiet-rural": (53.6, 28.6),
    "galactic-unshielded": (52.0, 23.0),
}
for freq in (1.0, 30.0):
    print(f"{freq:g} MHz")
    for name, (c, d) in cats.items():
        fa = p372_fa(c, d, freq)
        # External noise PSD, referred to the lossless P.372 reference antenna.
        psd = DBM_HZ + fa
        p3k = psd + 10 * log10(3000)
        print(f"  {name:22s} Fa={fa:6.2f} dB, PSD={psd:7.2f} dBm/Hz, 3kHz={p3k:7.2f} dBm")
print("VLF 4/7.5/9 kHz: P.372-17's plotted 10 kHz lower limit and MF/HF")
print("  city/rural formulas are out of range; use local measured spectra/APD and VLF models.")

print("\n5.8-GHz lunar disk beam coupling (ideal circular Gaussian main beam)")
lam = 299_792_458 / 5.8e9
moon_radius_deg = 0.25  # P.372-17 nominal ~0.5 degree diameter, idealized.
for dish_m in (0.6, 1.0, 3.0, 6.0):
    # Conventional approximate dish HPBW in degrees; actual taper/pattern requires measurement.
    hpbw_deg = 58.0 * lam / dish_m
    coupling = 1 - exp(-4 * log(2) * (moon_radius_deg / hpbw_deg) ** 2)
    print(f"  D={dish_m:3.1f} m, HPBW~{hpbw_deg:5.2f} deg, coupling={coupling:6.3f}, "
          f"TA Moon={140*coupling:5.1f}..{280*coupling:5.1f} K")
print("  Assumes uniform lunar disk, centered Gaussian beam and no sidelobe/spillover correction.")
print("  This is a conditional sensitivity, not a measured receiver or antenna result.")
