#!/usr/bin/env python3
"""Small reproducible ITU-method EME atmospheric endpoint sensitivity."""
import math

F_GHZ = 5.760
P_RAIN_MM_H = 100.0
SLAB_KM = 1.0
CLOUD_LWC_G_M3 = 0.2
SLAB_T_K = 273.15
GAS_ZENITH_DB = 0.040  # Rounded P.676 Fig. 4 standard-atmosphere chart read.

def interp(y0, y1, f=(F_GHZ - 5.5) / 0.5):
    return y0 + (y1 - y0) * f

# P.838-3 Table 5, linearly interpolated from 5.5 to 6.0 GHz.
k_h = interp(0.0003909, 0.0007056)
a_h = interp(1.6499, 1.5900)
k_v = interp(0.0003115, 0.0004878)
a_v = interp(1.5882, 1.5728)
# P.838-3 polarization-averaged circular case, tilt tau=45 degrees.
k_c = (k_h + k_v) / 2
a_c = (k_h * a_h + k_v * a_v) / (k_h + k_v)
gamma_rain = k_c * P_RAIN_MM_H**a_c

# P.840-9 Eq. (2)-(10), double-Debye liquid-water model at 273.15 K.
eps0 = 77.66 + 103.3 * (300.0 / SLAB_T_K - 1.0)
eps1 = 0.0671 * eps0
eps2 = 3.52
fp = 20.20 - 146.0 * (300.0 / SLAB_T_K - 1.0) + 316.0 * (300.0 / SLAB_T_K - 1.0) ** 2
fs = 39.8 * fp
eps_im = F_GHZ * (eps0 - eps1) / (fp * (1.0 + (F_GHZ / fp) ** 2)) + F_GHZ * (eps1 - eps2) / (fs * (1.0 + (F_GHZ / fs) ** 2))
eps_re = (eps0 - eps1) / (1.0 + (F_GHZ / fp) ** 2) + (eps1 - eps2) / (1.0 + (F_GHZ / fs) ** 2) + eps2
water_eta = (2.0 + eps_re) / eps_im
k_cloud = 0.819 * F_GHZ / (eps_im * (1.0 + water_eta**2))  # (dB/km)/(g/m3)

def compute_case(elevation_deg, wet):
    path_km = SLAB_KM / math.sin(math.radians(elevation_deg))
    # P.676 chart-read zenith gas estimate; >=5 deg uses cosecant scaling.
    gas = GAS_ZENITH_DB / math.sin(math.radians(elevation_deg))
    cloud = k_cloud * CLOUD_LWC_G_M3 * path_km if wet else 0.0
    rain = gamma_rain * path_km if wet else 0.0
    one_way = gas + cloud + rain
    trans = 10 ** (-one_way / 10.0)
    emitted = SLAB_T_K * (1.0 - trans)
    base_signal_dbm = -143.38  # Existing conditional 5m/70W reference output.
    echo_dbm = base_signal_dbm - one_way - one_way
    return {
        "elevation_deg": elevation_deg, "path_km": path_km,
        "gas_db": gas, "cloud_db": cloud, "rain_db": rain,
        "one_way_db": one_way, "eta": trans, "emit_K": emitted,
        "tx_leg_loss_db": one_way, "rx_leg_loss_db": one_way,
        "echo_before_weather_dbm": base_signal_dbm,
        "echo_after_two_legs_dbm": echo_dbm,
    }

if __name__ == "__main__":
    print(f"f_GHz={F_GHZ:.3f}; rain_R_mm_h={P_RAIN_MM_H:.1f}; slab_vertical_km={SLAB_KM:.1f}; cloud_LWC_g_m3={CLOUD_LWC_G_M3:.2f}; slab_T_K={SLAB_T_K:.2f}")
    print(f"P838_interp: kH={k_h:.8f}; alphaH={a_h:.6f}; kV={k_v:.8f}; alphaV={a_v:.6f}; circular_k={k_c:.8f}; circular_alpha={a_c:.6f}; gamma_rain_dB_km={gamma_rain:.6f}")
    print(f"P840_double_Debye: Kcloud_dB_km_per_g_m3={k_cloud:.8f}")
    print(f"GAS_INPUT: zenith_gas_dB={GAS_ZENITH_DB:.4f} (rounded chart read from P.676-13 Fig. 4 standard atmosphere, 1013.25hPa/15C/7.5g_m3; replace with site/profile output)")
    for label, elevation, wet in (("clear_reference", 60.0, False), ("broad_rain_cloud_stress", 10.0, True)):
        result = compute_case(elevation, wet)
        print(f"{label}: elevation_deg={elevation:.1f}; layer_path_km={result['path_km']:.3f};")
        print(f"  one_way_gas_dB={result['gas_db']:.4f}; cloud_dB={result['cloud_db']:.4f}; rain_dB={result['rain_db']:.4f}; total_dB={result['one_way_db']:.4f}; transmission={result['eta']:.6f}")
        print(f"  T_emit_rx_K={result['emit_K']:.2f}; tx_leg_loss_dB={result['tx_leg_loss_db']:.3f}; rx_leg_loss_dB={result['rx_leg_loss_db']:.3f};")
        print(f"  echo_before_weather_dBm={result['echo_before_weather_dbm']:.2f}; echo_after_two_signal_legs_dBm={result['echo_after_two_legs_dbm']:.2f}")
    print("Assumption: apparent elevations, reciprocal colocation; slab must span full path projection. The 10deg wet case needs a broad cell about 5.67km across for a 1km vertical slab. Conditional stress case only; no joint probability or universal worst case.")
    print("Radiative transfer: use RX T_out = T_in*transmission + T_emit on Moon/sky main-beam brightness once; ground spillover bypasses atmosphere. Keep RX atmospheric emission distinct from receiver noise. Do not transform aggregate Tsys that already includes sky/ground.")
