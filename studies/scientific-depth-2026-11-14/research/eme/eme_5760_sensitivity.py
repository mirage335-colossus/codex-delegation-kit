#!/usr/bin/env python3
"""Conditional 5.760 GHz EME antenna-plane/sensitivity reference; not calibration."""
import math

C = 299_792_458.0
K = 1.380649e-23
F = 5.760e9
R = 384_400_000.0
R_MOON = 1_737_400.0
THETA_MOON_DEG = 0.5
T_MOON_CASES = (140.0, 210.0, 280.0)
T_SYS_OFF_MOON = 100.0  # assumed baseline receiver+sky+spillover temperature
B = 100.0              # illustrative receiver noise bandwidth, not a mode threshold
ALBEDO_OC_REF = 0.06    # locally measured at 7.209GHz; carried only as conditional sensitivity

lam = C / F
area_disk = math.pi * R_MOON**2

def db(x):
    return 10.0 * math.log10(x)

def station(dish_m, power_w, eta=0.55):
    area = eta * math.pi * (dish_m / 2) ** 2
    gain = 4 * math.pi * area / lam**2
    hpbw_deg = 70 * lam / dish_m
    hpbw_rad = math.radians(hpbw_deg)
    moon_rad = math.radians(THETA_MOON_DEG)
    beam_solid_angle = 1.133 * hpbw_rad**2
    moon_solid_angle = math.pi * moon_rad**2 / 4
    # Approximate antenna temperature coupling for a uniform disk in a wide
    # Gaussian beam; does not model measured sidelobes or surface temperature map.
    solid_angle_ratio = min(1.0, moon_solid_angle / beam_solid_angle)
    # Gaussian beam-average power gain across a circular uniform projected disk.
    a = math.radians(THETA_MOON_DEG / 2)
    q = 4 * math.log(2) * (a / hpbw_rad) ** 2
    disk_mean_gain = (1 - math.exp(-q)) / q if q else 1.0
    # Radar return from each projected surface element is weighted by the
    # product of one-way transmit and receive power patterns. For identical,
    # co-boresighted Gaussian patterns, <B_tx B_rx>=<B^2>, not <B>^2.
    disk_mean_gain_product = (1 - math.exp(-2*q)) / (2*q) if q else 1.0
    # Antenna temperature is the integral of brightness times normalized beam
    # gain. The solid-angle ratio alone assumes B(theta)=1 over the Moon; apply
    # the disk-average Gaussian gain as well.
    coupling = solid_angle_ratio * disk_mean_gain
    return area, gain, hpbw_deg, coupling, disk_mean_gain, disk_mean_gain_product


def echo_power(power_w, gtx, grx, sigma):
    return power_w * gtx * grx * lam**2 * sigma / ((4 * math.pi) ** 3 * R**4)

print(f"f_GHz={F/1e9:.3f}; lambda_m={lam:.6f}; range_km={R/1e3:.0f}; B_Hz={B:.0f}; Tsys_offmoon_K_assumed={T_SYS_OFF_MOON:.0f}")
print(f"projected_lunar_disk_area_km2={area_disk/1e6:.0f}; albedo_reference={ALBEDO_OC_REF:.2f} (measured locally at 7.209GHz; no cross-frequency calibration claimed)")
print("Assumptions: balanced TX/RX station class; Pt delivered at each feed/antenna reference plane; eta_ap=.55; no feedline, weather, pointing, clock, RFI or polarization mismatch loss; sigma=.06 over a uniform lunar projected disk (conditional sensitivity, not measured 5.760GHz total RCS or strict bound).")
for label, diameter_m, power_w in (("reported_3m_37W_class", 3.0, 37.0), ("reported_5m_70W_class", 5.0, 70.0)):
    ae, g, hpbw, coupling, disk_gain, disk_gain_product = station(diameter_m, power_w)
    tmoon_mid = 210 * coupling
    sigma_ref = ALBEDO_OC_REF * area_disk * disk_gain_product
    pr = echo_power(power_w, g, g, sigma_ref)
    noise = K * (T_SYS_OFF_MOON + tmoon_mid) * B
    cnb = pr / (K * (T_SYS_OFF_MOON + tmoon_mid))
    print(f"{label}: Pt_W={power_w:.0f}; D_m={diameter_m:.1f}; eta=.55_assumed; G_dBi={db(g):.2f}; HPBW_deg={hpbw:.2f}; disk_mean_B_for_noise={disk_gain:.3f}; disk_mean_BtxBrx_for_signal={disk_gain_product:.3f}; sigma_eff_m2={sigma_ref:.4e}")
    print(f"  Tmoon_beam_K={tmoon_mid:.1f} at 210K brightness; coupling={coupling:.3f}; noise_in_{B:.0f}Hz_dBm={db(noise/1e-3):.2f}; lunar_noise_penalty_dB={db((T_SYS_OFF_MOON+tmoon_mid)/T_SYS_OFF_MOON):.2f}")
    print(f"  Pr_dBm={db(pr/1e-3):.2f}; C/N0_dBHz={db(cnb):.2f}; C/N_dB_in_{B:.0f}Hz={db(pr/noise):.2f}")
    for phase_t in T_MOON_CASES:
        t_m = phase_t * coupling
        n = K * (T_SYS_OFF_MOON + t_m) * B
        print(f"  lunar_brightness_K={phase_t:.0f}; Tmoon_ant_K={t_m:.1f}; moon_noise_penalty_dB={db((T_SYS_OFF_MOON+t_m)/T_SYS_OFF_MOON):.2f}; C/N_dB={db(pr/n):.2f}")
    for a in (0.03, 0.06, 0.12):
        s = a * area_disk * disk_gain_product
        p = echo_power(power_w, g, g, s)
        print(f"  albedo_sensitivity={a:.2f}; sigma_eff_m2={s:.4e}; Pr_dBm={db(p/1e-3):.2f}; delta_from_0.06_dB={db(a/ALBEDO_OC_REF):+.2f}")

# Delay-profile comparison. Uniform surface radar albedo gives power per
# projected area proportional to 2(1-u), with u=delay/max_delay. The balanced
# bistatic beam weighting is Btx*Brx; here both have the ideal Gaussian beam
# specified above. A second illustrative profile multiplies by exp(-depth/L),
# with L fitted to the classical 50%-within-5-mile observation. This is an
# old, frequency-unspecified calibration of the shape, not 5.76GHz evidence.
depth_m = 5 * 1609.344
tau_core = 2 * depth_m / C
full_surface_delay = 2 * R_MOON / C
delay_fraction = tau_core / full_surface_delay
# Resolve radial delay profiles for each dish with midpoint integration.
N = 100_000
du = 1.0 / N
moon_radius_rad = math.radians(THETA_MOON_DEG / 2)
range_m = R

def profile_stats(hpbw_deg, scale_m=None):
    hpbw = math.radians(hpbw_deg)
    values = []
    norm = first_moment = second_moment = 0.0
    for i in range(N):
        u = (i + 0.5) * du
        mu = 1.0 - u
        theta = moon_radius_rad * math.sqrt(max(0.0, 2*u - u*u))
        beam_one_way = math.exp(-4 * math.log(2) * (theta / hpbw) ** 2)
        w = 2 * (1-u) * beam_one_way**2
        if scale_m is not None:
            w *= math.exp(-(R_MOON * u) / scale_m)
        values.append((u, w))
        norm += w * du
        first_moment += u * w * du
        second_moment += u*u * w * du
    mean_u = first_moment / norm
    std_u = math.sqrt(max(0.0, second_moment / norm - mean_u*mean_u))
    def quantile(qv):
        c = 0.0
        for u, w in values:
            c += w * du / norm
            if c >= qv:
                return u
        return 1.0
    return {"t50_ms": quantile(0.5)*full_surface_delay*1e3,
            "t90_ms": quantile(0.9)*full_surface_delay*1e3,
            "mean_ms": mean_u*full_surface_delay*1e3,
            "rms_about_zero_ms": math.sqrt(second_moment / norm)*full_surface_delay*1e3,
            "rms_spread_ms": std_u*full_surface_delay*1e3,
            "f_first5mi": sum(w*du for u,w in values if u <= delay_fraction)/norm}

def fit_scale(hpbw_deg, target_fraction=0.5):
    lo, hi = 1.0, R_MOON * 100
    for _ in range(64):
        mid = (lo + hi) / 2
        if profile_stats(hpbw_deg, mid)["f_first5mi"] < target_fraction:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

print(f"delay_geometry: tau_max_ms={full_surface_delay*1e3:.3f}; first_5mi_two_way_us={tau_core*1e6:.2f}; u_5mi={delay_fraction:.6f}; uniform_projected_area_fraction={2*delay_fraction-delay_fraction**2:.6f}")
for label, diameter_m, power_w in (("3m", 3.0, 37.0), ("5m", 5.0, 70.0)):
    _, _, hpbw, _, _, _ = station(diameter_m, power_w)
    for name, scale in (("uniform_albedo_beam_weighted", None),):
        s = profile_stats(hpbw, scale)
        print(f"delay_profile: beam={label}; model={name}; L_m={scale if scale is not None else 'none'}; t50_ms={s['t50_ms']:.5f}; t90_ms={s['t90_ms']:.5f}; mean_ms={s['mean_ms']:.5f}; rms_about_zero_ms={s['rms_about_zero_ms']:.5f}; rms_spread_ms={s['rms_spread_ms']:.5f}; first5mi_fraction={s['f_first5mi']:.6f}")
    for target_fraction in (0.4, 0.5, 0.6):
        lfit = fit_scale(hpbw, target_fraction)
        s = profile_stats(hpbw, lfit)
        print(f"delay_profile: beam={label}; model=exp_depth_sensitivity_fitted_to_classic; target_first5mi_fraction={target_fraction:.1f}; L_m={lfit:.1f}; t50_ms={s['t50_ms']:.5f}; t90_ms={s['t90_ms']:.5f}; mean_ms={s['mean_ms']:.5f}; rms_about_zero_ms={s['rms_about_zero_ms']:.5f}; rms_spread_ms={s['rms_spread_ms']:.5f}; first5mi_fraction={s['f_first5mi']:.6f}")
print("delay_profile_limit: exponential profile is a conditional one-parameter shape, not a measured law; 0.4/0.5/0.6 fractions are sensitivity cases, not uncertainty bounds; historical datum has no stated error bars; ideal Gaussian beams; target-band spatial/polarization/frequency dependence remains unknown")
