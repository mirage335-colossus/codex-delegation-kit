#!/usr/bin/env python3
"""Conditional same-reference field-to-C/N0 arithmetic; not a site budget."""
from math import log10

KTB_DBM_HZ = -173.975  # k*T0 at 290 K
NF_DB = 5.0
F = 10 ** (NF_DB / 10)
RX_INTERNAL_DBM_HZ = KTB_DBM_HZ + 10 * log10(F - 1)
B_HZ = 3000.0

# Signal available powers are the observed NTIA LFMF outputs for 1 W,
# 100 km, zero-height, dry soil, vertical polarization, and its 4.77 dBi
# receive reference gain. External densities are conditional P.372-17 values.
CASES = [
    ("1MHz rural median", -73.085, [-106.78]),
    ("1MHz city median", -73.085, [-97.18]),
    ("30MHz rural+unshielded galaxy", -145.178, [-147.69, -155.95]),
]

print("assumptions: same lossless short-vertical reference, co-polarized, matched 50 ohm, zero feeder loss, NF=5 dB")
print(f"receiver added noise density k*T0*(F-1): {RX_INTERNAL_DBM_HZ:.3f} dBm/Hz")
for name, signal, external in CASES:
    terms = external + [RX_INTERNAL_DBM_HZ]
    total_n0 = 10 * log10(sum(10 ** (x / 10) for x in terms))
    cn0 = signal - total_n0
    cn = cn0 - 10 * log10(B_HZ)
    print(f"{name}: C={signal:.3f} dBm, external={external}, N0={total_n0:.3f} dBm/Hz, C/N0={cn0:.3f} dBHz, C/N({B_HZ:.0f}Hz)={cn:.3f} dB")
