#!/usr/bin/env python3
"""Reconstruct rounded aggregate path mixtures from Watterson (1969) Tables 4/6/8.

Input rows are the report's aggregate path rows only (a/b magnetoionic
components are excluded so their power is not double counted). Relative path
powers in dB are converted to linear weights and normalized to unity. The
calculation treats each path's tabulated Doppler spectrum as a Gaussian whose
standard deviation is the printed 2-sigma width divided by two.
"""
from math import log10, sqrt

cases = {
    "I1": {
        "freq_MHz": 9.259,
        "reported_mean_delay_us": 137.0,
        "reported_delay_width_2sigma_us": 478.0,
        "reported_center_hz": 0.0013,
        "reported_width_2sigma_hz": 0.123,
        "paths": [(40, -1.2, 0.0094, 0.0272),
                  (290, -7.2, 0.0089, 0.144),
                  (1139, -13.5, -0.167, 0.340)],
    },
    "I2": {
        "freq_MHz": 9.259,
        "reported_mean_delay_us": 173.0,
        "reported_delay_width_2sigma_us": 520.0,
        "reported_center_hz": 0.0171,
        "reported_width_2sigma_hz": 0.140,
        "paths": [(40, -1.7, 0.0071, 0.0153),
                  (290, -5.9, 0.0159, 0.180),
                  (590, -17.6, 0.108, 0.334),
                  (1126, -12.6, 0.118, 0.336)],
    },
    "I3A": {
        "freq_MHz": 5.864,
        "reported_mean_delay_us": 589.0,
        "reported_delay_width_2sigma_us": 464.0,
        "reported_center_hz": 0.110,
        "reported_width_2sigma_hz": 0.0666,
        "paths": [(445, -1.6, 0.0989, 0.0658),
                  (750, -7.7, 0.131, 0.0229),
                  (1088, -8.5, 0.140, 0.0335)],
    },
}

print("Watterson Table 4/6/8 rounded aggregate-path reconstruction")
print("weights from path relative dB; a/b rows excluded; no absolute delay implied")
for name, c in cases.items():
    rows = c["paths"]
    raw_w = [10 ** (row[1] / 10) for row in rows]
    total = sum(raw_w)
    w = [x / total for x in raw_w]
    mean_t = sum(wi * row[0] for wi, row in zip(w, rows))
    var_t = sum(wi * (row[0] - mean_t) ** 2 for wi, row in zip(w, rows))
    rms_t = sqrt(var_t)
    mean_f = sum(wi * row[2] for wi, row in zip(w, rows))
    var_f = sum(wi * ((row[3] / 2) ** 2 + (row[2] - mean_f) ** 2)
                for wi, row in zip(w, rows))
    width_f = 2 * sqrt(var_f)
    print(f"\n{name}: {c['freq_MHz']:.3f} MHz, paths={len(rows)}")
    print("  normalized powers = " + ", ".join(f"{100*x:.2f}%" for x in w))
    print(f"  delay mean reconstructed/reported = {mean_t:.2f}/{c['reported_mean_delay_us']:.1f} us; delta={mean_t-c['reported_mean_delay_us']:+.2f} us")
    print(f"  delay mixture 2sigma reconstructed/reported = {2*rms_t:.2f}/{c['reported_delay_width_2sigma_us']:.1f} us; delta={2*rms_t-c['reported_delay_width_2sigma_us']:+.2f} us")
    print(f"  Doppler mean reconstructed/reported = {mean_f:.6f}/{c['reported_center_hz']:.6f} Hz; delta={mean_f-c['reported_center_hz']:+.6f} Hz")
    print(f"  Doppler mixture 2sigma reconstructed/reported = {width_f:.6f}/{c['reported_width_2sigma_hz']:.6f} Hz; delta={width_f-c['reported_width_2sigma_hz']:+.6f} Hz")
    print("  power-normalized tap centers/delays = " + ", ".join(f"({row[0]:g} us, {row[2]:+.4f} Hz)" for row in rows))

print("\nAssumptions: rounded printed values; aggregate tap powers and one Gaussian 2sigma per path; report-level delay/frequency summaries may use different estimation/smoothing and include finite errors. Relative delay origin is arbitrary. These checks do not recover raw time series, exact subband correlation, phase, outages, or occurrence frequencies.")
