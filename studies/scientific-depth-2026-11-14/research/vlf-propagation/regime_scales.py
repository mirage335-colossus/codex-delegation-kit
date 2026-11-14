#!/usr/bin/env python3
"""Reproduce first-order VLF/ELF wavelength, reactive-distance and guide scales.

This is a dimensional sensitivity check, not a waveguide solver or link budget.
The parallel-plate cutoff relation is an idealized scale; real Earth/ionosphere
mode constants depend on lossy, anisotropic, curved boundaries.
"""
from math import log10, pi, sqrt
import cmath

C = 299_792_458.0
EARTH_RADIUS_KM = 6_371.0
MU0 = 4e-7 * pi
FREQUENCIES_HZ = (500, 1_000, 1_700, 3_000, 5_000, 8_000, 9_000)
HEIGHTS_KM = (70.0, 85.0, 90.0)
CONDUCTIVITIES_S_PER_M = (4.0, 1e-2, 1e-3)

print("frequency_hz wavelength_km lambda_over_2pi_km r_over_lambda_500km")
for f in FREQUENCIES_HZ:
    wavelength_km = C / f / 1_000
    print(f"{f:>13} {wavelength_km:>13.3f} {wavelength_km/(2*pi):>19.3f}"
          f" {500/wavelength_km:>22.3f}")

print("\nideal_parallel_plate_cutoffs_kHz (f_n=n*c/(2h))")
for h in HEIGHTS_KM:
    fc = C / (2 * h * 1_000) / 1_000
    print(f"height_km={h:.1f} fundamental_kHz={fc:.3f}"
          f" higher_mode_n_at_3kHz={3/fc:.2f}"
          f" higher_mode_n_at_8kHz={8/fc:.2f}")

print(f"\nEarth_circumference_km={2*pi*EARTH_RADIUS_KM:.1f}")

print("\nideal_good_conductor_skin_depth_m (delta=sqrt(2/(2*pi*f*mu0*sigma)))")
for sigma in CONDUCTIVITIES_S_PER_M:
    row = " ".join(f"{sqrt(2/(2*pi*f*MU0*sigma)):>9.2f}"
                    for f in (1_000, 3_000, 8_000))
    print(f"sigma_S_per_m={sigma:g} at_1kHz_3kHz_8kHz={row}")

print("\nillustrative_two_path_notch: H=1-0.99*exp(-j*2*pi*f*T)")
f0, delay_s, echo = 8_000.0, 0.007, 0.99
h = 1 - echo * cmath.exp(-2j*pi*f0*delay_s)
dh_df = 2j*pi*delay_s*echo*cmath.exp(-2j*pi*f0*delay_s)
group_delay_s = -(h.conjugate()*dh_df).imag / (2*pi*abs(h)**2)
print(f"f_hz={f0:g} physical_path_support_ms={delay_s*1000:g}"
      f" abs_H={abs(h):g} null_depth_db={20*log10(abs(h)):.2f}"
      f" local_group_delay_ms={group_delay_s*1000:.3f}")
