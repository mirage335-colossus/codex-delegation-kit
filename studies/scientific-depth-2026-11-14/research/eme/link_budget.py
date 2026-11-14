#!/usr/bin/env python3
"""Reproducible conditional lunar EME reference checks; no pump code involved."""
import math

C = 299_792_458.0
K = 1.380649e-23
D_MOON = 384_400_000.0
R_MOON = 1_737_400.0
F0 = 7_209.125e6
PT = 200.0
ETA_TX = 0.50
D_TX = 18.0
ETA_RX = 0.47
D_RX = 40.0
TRX = 96.0
ALBEDO_OC = 0.07

lam = C / F0
At = ETA_TX * math.pi * (D_TX / 2) ** 2
Ar = ETA_RX * math.pi * (D_RX / 2) ** 2
Gt = 4 * math.pi * At / lam**2
Gr = 4 * math.pi * Ar / lam**2
# Paper's receiver illuminates a 503-km diameter region; its cross-section
# approximation takes radar albedo times projected illuminated disk area.
d_footprint = 503_000.0
A_footprint = math.pi * (d_footprint / 2) ** 2
sigma = ALBEDO_OC * A_footprint
# Point-target bistatic radar equation, with the transmit and receive ranges
# separately shown (here approximated equal).
Pr = PT * Gt * Gr * lam**2 * sigma / ((4 * math.pi) ** 3 * D_MOON**4)
Pr_dbm = 10 * math.log10(Pr / 1e-3)
B = 35.0
noise = K * TRX * B
CNR = 10 * math.log10(Pr / noise)
integration_s = 10.0
# The 2019 paper defines SNR using RMS uncertainty of integrated noise power:
# ΔPn = k*T*B/sqrt(B*integration_time), which is not Pr/(kTB).
delta_noise_power = noise / math.sqrt(B * integration_s)
paper_snr = Pr / delta_noise_power

# The published geometry's 35-Hz echo width at 7.209 GHz scales nearly
# linearly with carrier for the same projected illuminated lunar region.
width_58 = 35.0 * 5.8 / 7.209125
path_rate_span_35 = 35.0 * C / F0
path_rate_span_90 = 90.0 * C / F0
# Calibrated absolute lunar backscatter products are reported 6-10x lower
# than earlier investigations. This power factor is not an uncertainty sigma.
cal_db = (10 * math.log10(6), 10 * math.log10(10))
# Near subradar surface point to the geometric limb (tangent ray), exact
# two-leg range difference. This tends to 2*R_MOON/c as D >> R_MOON.
near_center_to_limb = 2 * (math.sqrt(D_MOON**2 - R_MOON**2) - (D_MOON - R_MOON)) / C

def db(x): return 10 * math.log10(x)

print(f"lambda_m={lam:.6f}")
print(f"tx_gain_dbi={db(Gt):.2f}; rx_gain_dbi={db(Gr):.2f}; tx_aperture_m2={At:.3f}; rx_aperture_m2={Ar:.3f}")
print(f"footprint_area_km2={A_footprint/1e6:.0f}; sigma_m2={sigma:.4e}; sigma_dbsm={db(sigma):.2f}; RCS_assumption=0.07*projected_503km_disk")
print(f"Pr_W={Pr:.4e}; Pr_dBm={Pr_dbm:.2f}; kTB_dBm={10*math.log10(noise/1e-3):.2f}; raw_CNR_dB={CNR:.2f} in {B:g}Hz, before integration")
print(f"published_metric_DeltaPn_W={delta_noise_power:.4e}; SNR_Pr_over_DeltaPn={paper_snr:.0f} ({10*math.log10(paper_snr):.2f}dB), 10s, matched to paper's estimator convention")
print(f"if sigma power is /6..10: Pr_dBm={Pr_dbm-cal_db[0]:.2f}..{Pr_dbm-cal_db[1]:.2f}; CNR_dB={CNR-cal_db[0]:.2f}..{CNR-cal_db[1]:.2f}")
print(f"10log10(6..10) dB={cal_db[0]:.2f}..{cal_db[1]:.2f}")
print(f"echo_width_5.8GHz_scaled_Hz={width_58:.2f}; valid only with same footprint/geometry/libration")
print(f"paper_derived_7.209GHz_width_to_total_path_rate_span_mps: 35Hz={path_rate_span_35:.3f}; 90Hz={path_rate_span_90:.3f}; 1mps_at_5.8GHz={5.8e9/C:.2f}Hz")
print(f"spherical_front_surface_delay_near_subradar_to_limb_ms={near_center_to_limb*1e3:.3f}")
print(f"roundtrip_center_delay_s={2*D_MOON/C:.6f}; one-way_pointing_offset_from_dish_gain_not_modeled")
# Two pure geometric sensitivities, holding everything else fixed.
for x in (356_500_000.0, 406_700_000.0):
    print(f"range_km={x/1e3:.0f}; range_delta_dB={-40*math.log10(x/D_MOON):+.2f}")
# Fixed-diameter / fixed-aperture scan: the Friis/bistatic gain factor alone
# improves as f^2. Lunar sigma and atmosphere still need band-specific evidence.
for f in (5.8e9, F0, 10.368e9):
    print(f"carrier_GHz={f/1e9:.3f}; fixed_aperture_radar_gain_factor_vs_7.209_dB={20*math.log10(f/F0):+.2f}")

# Conditional pointing/gain illustration for 5.760GHz amateur dish sizes,
# using η=.55 and a Gaussian main-beam approximation.
f_point = 5.760e9
lam_point = C / f_point
for dish_m in (3.0, 5.0):
    eta_point = 0.55
    area = eta_point * math.pi * (dish_m / 2) ** 2
    gain = 4 * math.pi * area / lam_point**2
    hpbw_deg = 70.0 * lam_point / dish_m
    print(f"conditional_5760MHz_dish_D{dish_m:g}m_eta.55: gain_dbi={db(gain):.2f}; approximate_HPBW_deg={hpbw_deg:.2f}")
    for off in (0.1, 0.25):
        loss = 12.04 * (off / hpbw_deg) ** 2
        print(f"  point-source_mainbeam_loss_at_offset_{off:.2f}deg_dB={loss:.2f}; not_integrated_lunar_disk_loss")

# Conditional rain check using ITU-R P.838-3 Table 5 values linearly
# interpolated between 5.5 and 6 GHz; circular polarization uses tau=45 deg.
# Each terrestrial station is assumed to cross the same 1-km vertical rain
# layer at 30-degree elevation, i.e. 2-km slant path per Earth endpoint.
kH = 0.0003909 + 0.6 * (0.0007056 - 0.0003909)
aH = 1.6499 + 0.6 * (1.5900 - 1.6499)
kV = 0.0003115 + 0.6 * (0.0004878 - 0.0003115)
aV = 1.5882 + 0.6 * (1.5728 - 1.5882)
k_circ = (kH + kV) / 2
a_circ = (kH * aH + kV * aV) / (kH + kV)
total_rain_path_km = 2 * (1.0 / math.sin(math.radians(30.0)))
print(f"conditional_ITU_P838_5.8GHz_circular: k={k_circ:.7f}; alpha={a_circ:.4f}; combined_two_endpoint_rain_path_km={total_rain_path_km:.1f}")
for rain_mm_h in (25.0, 100.0):
    specific = k_circ * rain_mm_h ** a_circ
    total_loss = specific * total_rain_path_km
    print(f"  rain_rate_mm_h={rain_mm_h:.0f}; gamma_R_dB_km={specific:.3f}; one_way_earth_endpoint_loss_dB={specific*2:.2f}; both_ends_combined_loss_dB={total_loss:.2f}")
