#!/usr/bin/env python3
"""Arithmetic audit of published Ottawa–Alert loss summaries.

Inputs are values stated by Gillies et al. (2026), DOI 10.1029/2025SW004906.
The paper does not publish raw expected/success pulse counts in the accessible
text, so this does not reconstruct the data or claim operational truth.
"""

baseline_loss = 0.62
high_absorption_loss_range = (0.80, 0.90)  # all-frequency absolute loss, A30-site mean > 2 dB
normalized_increment_values = {
    "5_to_11_MHz_most_bands_low_end": 0.26,
    "5_to_11_MHz_most_bands_high_end": 0.32,
    "14_MHz": 0.19,
    "10_MHz_reported_anomaly": 0.40,
    "remote_3_riometers": (0.24, 0.28),
    "nearest_Rankin_Inlet": 0.41,
}

print("Source: Gillies et al. 2026, DOI 10.1029/2025SW004906, §§2–4")
print(f"pooled_expected_pulse_loss_baseline={baseline_loss:.3f}")
print(f"pooled_baseline_reception={1-baseline_loss:.3f}")
lo, hi = high_absorption_loss_range
print(f"absolute_loss_when_four_site_mean_A30_gt2dB={lo:.3f}..{hi:.3f}")
print(f"absolute_increment_over_pooled_baseline={(lo-baseline_loss):.3f}..{(hi-baseline_loss):.3f} (18..28 percentage points)")
print(f"fraction_of_remaining_reception_that_is_lost={(lo-baseline_loss)/(1-baseline_loss):.3f}..{(hi-baseline_loss)/(1-baseline_loss):.3f}")
print("frequency/site figure values are normalized increments, not absolute loss probability:")
for label, value in normalized_increment_values.items():
    print(f"  {label}={value}")
print("conditional_absolute_loss=p_baseline_frequency + normalized_increment*(1-p_baseline_frequency)")
print("frequency-specific baseline probabilities are required; pooled 0.62 is not interchangeable with them")

print("operation-denominator sensitivity; hypothetical share of listed opportunities actually offline")
for offline_share in (0.0, 0.05, 0.10, 0.20):
    corrected = (baseline_loss - offline_share) / (1 - offline_share)
    print(f"  offline_share={offline_share:.2f}: inferred_loss_given_operating={corrected:.3f}")
print("offline-share values are scenarios only; paper excludes Jul/Aug 2016 from occurrence plot but gives no operation-log fraction")

for pulses_per_hour in (4, 8, 24):
    print(f"scheduled_opportunities_per_frequency_per_24h_at_{pulses_per_hour}_per_hour={24*pulses_per_hour}")
print("frequency set MHz=5.38, 6.93, 8.10, 10.42, 11.11, 14.36")
print("no actual run-time pulse count/denominator reconstructed")
