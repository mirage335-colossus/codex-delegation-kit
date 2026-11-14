#!/usr/bin/env python3
"""Show why absolute UTC*RF in binary64 is not a phase accumulator."""
from decimal import Decimal, getcontext
import math

getcontext().prec = 60
epoch_seconds_text = "1793404800.123456789"
carrier_hz = 5_800_000_000
exact_cycles = Decimal(epoch_seconds_text) * Decimal(carrier_hz)
exact_fraction = exact_cycles % 1
binary64_seconds = float(epoch_seconds_text)
binary64_cycles = binary64_seconds * carrier_hz
binary64_fraction = binary64_cycles % 1.0

print(f"UTC seconds (input) {epoch_seconds_text}")
print(f"carrier_hz {carrier_hz}")
print(f"exact cycles integer={int(exact_cycles)} fraction={exact_fraction}")
print(f"binary64 seconds {binary64_seconds:.17g}")
print(f"binary64 ULP seconds {math.ulp(binary64_seconds):.12g}")
print(f"binary64 cycles ULP {math.ulp(binary64_cycles):.12g}")
print(f"binary64 phase fraction {binary64_fraction:.17g}")
print(f"phase fraction absolute error {abs(float(exact_fraction)-binary64_fraction):.12g} cycles")
