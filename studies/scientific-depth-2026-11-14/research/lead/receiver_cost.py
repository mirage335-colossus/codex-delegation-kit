"""Arithmetic-only paired cost bounds for the fixed native fixture design."""

from fractions import Fraction
from math import ceil

RATE = 6_000
COORDINATE_CAP = 4
BITS = 2
RAW_BYTES_PER_SAMPLE = 17
COMPLEX_BYTES = 16


def operation_bound(rows: int, coordinate_count: int, paired: bool) -> int:
    """Elementwise arithmetic only. Renderer and final scalar work are separate."""
    if coordinate_count == 0:
        return 0
    shared_arithmetic = 4 * rows
    arithmetic_per_template_row = 16 + (12 if paired else 0)
    return shared_arithmetic + coordinate_count * BITS * rows * arithmetic_per_template_row


for seconds in (1, 16):
    rows = RATE * seconds
    raw_bytes = rows * RAW_BYTES_PER_SAMPLE
    shadow_bytes = rows * COMPLEX_BYTES
    print(f"Illustrative scored duration={seconds}s, rows={rows:,}, coordinate cap={COORDINATE_CAP}")
    print(f"  immutable IQ + mask={raw_bytes:,} bytes, new full whitened vector={shadow_bytes:,} bytes")
    print(f"  shadow template evaluations up to {BITS * COORDINATE_CAP * rows:,} raw rows")
    print(f"  colored only: {operation_bound(rows, COORDINATE_CAP, paired=False):,} real operations")
    print(f"  colored + identity control: {operation_bound(rows, COORDINATE_CAP, paired=True):,} real operations")
    print(f"  all stages, both arms: runtime and actual complete-slot rows unmeasured")

grid_delay_seconds = Fraction(21, 1_000)
for tx_scale in (Fraction(1), Fraction(10_001, 10_000)):
    ring = COMPLEX_BYTES * (ceil(RATE * grid_delay_seconds * tx_scale) + 64)
    print(f"Illustrative TX history arithmetic at 21ms and clock scale {float(tx_scale)}: {ring:,} bytes per ring")

records = 5 * 4
active_duration = 4 * sum((60, 10, 10, 60, 15))
print(f"Five-domain pilot: {records} records and {2 * records} arm runs")
print(f"  active-source duration lower bound: {active_duration}s per arm")
print("  sample-zero simulation extent: N_d,j = max(N_natural,d,j, minimum_capture_samples_d,j)")
print("  the public capture floor already reserves two quiet slots; check aperture validity separately")
print("  full input duration: sum(N_d,j / F_s,rx)")
print("  full input bytes: 17 * sum(N_d,j) per lane")
print("  exact profile/tail inputs and observed longer tails require preflight")
print("Superseded first estimate: 652s/arm using arbitrary 1s/2s/3s tails; underaccounted and unusable for allocation.")
