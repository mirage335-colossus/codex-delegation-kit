#!/usr/bin/env python3
"""Reproducible arithmetic and denominator audit of Dear et al. (2024).

Inputs below are the four relative arrival delays explicitly printed for CIR
cluster #1 in the published 21-Dec-2021 13:30 LT example. This script does not
reconstruct unpublished samples or infer availability.
"""

C_M_PER_S = 299_792_458
relative_delay_ms = [0.213, 0.441, 1.377, 1.654]
period_minutes = 15
campaign_days = 7

print("Source: Dear et al. 2024, DOI 10.1029/2023RS007877, Fig. 10 / §4")
print("Published capture: 2021-12-21 13:30 LT UTC+7; 7.12 MHz equatorial NVIS")
print("tau_excess_ms, excess_path_length_km")
for tau_ms in relative_delay_ms:
    excess_km = C_M_PER_S * tau_ms / 1000 / 1000
    print(f"{tau_ms:.3f}, {excess_km:.3f}")

planned_slots = campaign_days * 24 * 60 // period_minutes
print(f"scheduled_slots_if_continuous_24h={planned_slots}")
print("observed_slot_success_count=not reported in article")
print("availability_fraction=not identifiable from published article")
print("interpretation=excess path length only; no vertical height or absolute ToF")
print("Doppler summary=0.7-1.1 Hz shift, mean 0.9 Hz; not spectral spread")
