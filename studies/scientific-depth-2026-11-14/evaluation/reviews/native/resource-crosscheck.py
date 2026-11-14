#!/usr/bin/env python3
"""Bounded native resource arithmetic from frozen defaults and Fable-70 inputs."""
from decimal import Decimal

# Production default source: inner_rate=36 Hz, added_symbols=10,
# sample_rate=960 Hz. Production geometry: fine=inner/6*added;
# spacing=1.25*fine; occupied DATA width=3*spacing; admission requires
# Fs >= 4*fine and Fs > 1.1*occupied width.
inner_hz = Decimal(36)
added = Decimal(10)
sample_rate = Decimal(960)
fine_hz = inner_hz / 6 * added
spacing_hz = Decimal("1.25") * fine_hz
occupied_hz = 3 * spacing_hz
sample_gate = max(4 * fine_hz, Decimal("1.1") * occupied_hz)

# Fable-5.2 70 declared resource illustrations, recalculated independently.
vlf_seconds = Decimal("421.875") * 3600
vlf_samples = vlf_seconds * sample_rate
complex_bytes_assumption = 16  # common std::complex<double>; not a portable sizeof proof
mask_bytes = 1
vlf_all_retained_bytes = vlf_samples * (complex_bytes_assumption + mask_bytes)
eme_products = Decimal(256) * 512 * 48000 * 1800

print(f"default_fine_chip_rate_hz={fine_hz}")
print(f"default_spacing_hz={spacing_hz}")
print(f"default_nominal_DATA_bandwidth_hz={occupied_hz}")
print(f"default_sample_admission_lower_bound_hz={sample_gate}")
print(f"default_sample_rate_hz={sample_rate}; passes={sample_rate >= sample_gate}")
print(f"VLF_421.875h_seconds={vlf_seconds}")
print(f"VLF_samples_at_960Hz={vlf_samples}")
print(f"VLF_hypothetical_all_retained_bytes_16B_complex_plus_1B_mask={vlf_all_retained_bytes}")
print(f"EME_256x512_at_48kHz_for_1800s_cell_sample_products={eme_products}")
for rate in (Decimal("1e8"), Decimal("1e9"), Decimal("1e10")):
    print(f"illustrative_products_per_s={rate}; hours={eme_products / rate / 3600}")
