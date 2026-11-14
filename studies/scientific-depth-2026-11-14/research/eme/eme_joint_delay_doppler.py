#!/usr/bin/env python3
"""Conditional monostatic lunar surface joint delay/Doppler desk model.

This is not an ephemeris or measured 5.76-GHz RCS. It extends the retarded
two-leg path convention in research/lead/comparisons.py::moon() to projected
surface points, with a declared synthetic lunar center orbit and rigid spin.
"""
import math
import sys

C = 299_792_458.0
F_HZ = 5.760e9
D_M = 384_400_000.0
R_MOON_M = 1_737_400.0
T_SPIN_S = 27.321661 * 86400.0
OMEGA = 2 * math.pi / T_SPIN_S
V_ORBIT_MPS = 1022.0
V_RADIAL_MPS = 30.0
THETA_MOON_RAD = math.radians(0.25)  # same approximate 0.5-degree disk as link budget
RADIAL_CELLS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
AZIMUTH_CELLS = 360
FREQ_WINDOWS_HZ = (50.0, 112.5)
DELAY_WINDOWS_MS = (0.05368, 0.17832, 1.0, 11.591)
F_SOURCE_GHZ = 7.209125
SOURCE_GRADIENTS_HZ_PER_M = {
    # Predicted DE436 spans over the two illuminated footprint diameters in
    # Sun et al. §2.3, frequency-scaled to 5.760 GHz.
    "Sun2020_Km_35Hz_503km_scaled": (35.0 / 503_000.0) * (F_HZ / (F_SOURCE_GHZ * 1e9)),
    "Sun2020_Zv_90Hz_1118km_scaled": (90.0 / 1_118_000.0) * (F_HZ / (F_SOURCE_GHZ * 1e9)),
}


def station_beam_gain(dish_m):
    lam = C / F_HZ
    hpbw = math.radians(70 * lam / dish_m)
    return hpbw


def surface_state(t_s, x_body, y_body, z_body, orientation):
    """Earth-centered local Cartesian state; z points downlink, x/y transverse."""
    a = OMEGA * t_s
    ca, sa = math.cos(a), math.sin(a)
    if orientation == "transverse_y_orthogonal_stress":
        # Spin axis is along the synthetic transverse center velocity, so its
        # Doppler gradient is orthogonal to the orbital-projection gradient.
        x = ca * x_body + sa * z_body
        y = y_body
        z = -sa * x_body + ca * z_body
        vx_spin, vy_spin, vz_spin = OMEGA * z, 0.0, -OMEGA * x
    elif orientation == "orbit_normal_prograde_sync":
        # Center motion is +y at the receive epoch; orbit angular momentum and
        # prograde synchronous spin are therefore about -x.
        x = x_body
        y = ca * y_body + sa * z_body
        z = -sa * y_body + ca * z_body
        vx_spin, vy_spin, vz_spin = 0.0, OMEGA * z, -OMEGA * y
    else:
        raise ValueError(orientation)
    return ((x, V_ORBIT_MPS * t_s + y, D_M + V_RADIAL_MPS * t_s + z),
            (vx_spin, V_ORBIT_MPS + vy_spin, V_RADIAL_MPS + vz_spin))


def range_rate(t_s, body, orientation):
    pos, vel = surface_state(t_s, *body, orientation)
    rng = math.sqrt(sum(v * v for v in pos))
    vr = sum(a * b for a, b in zip(pos, vel)) / rng
    return rng, vr


def retarded_echo(body, orientation):
    """For transmit epoch 0, solve up-leg scatter time and return arrival, Doppler."""
    t_s = D_M / C
    for _ in range(7):
        rng, _ = range_rate(t_s, body, orientation)
        t_s = rng / C
    rng, vr = range_rate(t_s, body, orientation)
    t_rx = t_s + rng / C
    # For co-located TX/RX and a moving point, exact first-order-in-path
    # retardation is the product of retarded up/down radial factors.
    f_rx = F_HZ * (1.0 - vr / C) / (1.0 + vr / C)
    return t_rx, f_rx


def make_geometry(orientation):
    # Point at lunar subradar surface is the time origin for excess delay and
    # common two-way Doppler. The Earth observer is static in this conditional
    # local inertial frame; the Moon's center follows the lead's synthetic
    # 30 m/s radial + 1022 m/s transverse motion.
    center = (0.0, 0.0, -R_MOON_M)
    t0, f0 = retarded_echo(center, orientation)
    records = []
    dphi_weight = 1.0 / AZIMUTH_CELLS
    for i in range(RADIAL_CELLS):
        s_lo = i / RADIAL_CELLS
        s_hi = (i + 1) / RADIAL_CELLS
        # u=s^2 concentrates cells near subradar delays while preserving
        # projected-area integration through the exact bin width in u.
        s_mid = (s_lo + s_hi) / 2
        u = s_mid * s_mid
        du = s_hi * s_hi - s_lo * s_lo
        rho_norm = math.sqrt(2 * u - u * u)
        z_body = -R_MOON_M * (1.0 - u)
        area_mass = 2.0 * (1.0 - u) * du * dphi_weight
        for j in range(AZIMUTH_CELLS):
            phi = (j + 0.5) * (2 * math.pi / AZIMUTH_CELLS)
            rho_m = R_MOON_M * rho_norm
            x_body = rho_m * math.cos(phi)
            y_body = rho_m * math.sin(phi)
            t_rx, f_rx = retarded_echo((x_body, y_body, z_body), orientation)
            delay_ms = 1000 * (t_rx - t0)
            df_hz = f_rx - f0
            records.append((u, rho_norm, delay_ms, df_hz, x_body / R_MOON_M, area_mass))
    print(f"geometry: orientation={orientation}; F_RF_Hz={F_HZ:.0f}; D_km={D_M/1000:.0f}; lunar_radius_km={R_MOON_M/1000:.1f}; spin_period_days={T_SPIN_S/86400:.6f}; omega_rad_s={OMEGA:.9g}")
    print(f"geometry: synthetic center Vrad_mps={V_RADIAL_MPS:.1f}; Vtrans_mps={V_ORBIT_MPS:.1f}; observer static; subradar body point at x=y=0,z=-R; removed common two-leg center Doppler={f0-F_HZ:+.3f}Hz; center roundtrip_s={t0:.9f}")
    print(f"geometry: points={len(records)}; radial_cells={RADIAL_CELLS} with u=s^2 quadrature (Δu near 5mi={2*math.sqrt(5*1609.344/R_MOON_M)/(RADIAL_CELLS):.7f}); delay=retarded receive epoch minus central-point receive epoch for a pulse sent at t=0; Doppler=exact radial up/down frequency ratio minus central-point frequency; no station separation, libration, terrain or target ephemeris; orientation is constructed, not actual Moon geometry")
    print(f"geometry: sampled_support_max_delay_ms={max(x[2] for x in records):.6f}; sampled_max_abs_differential_Doppler_Hz={max(abs(x[3]) for x in records):.3f}")
    return records


def beam_weight(rho_norm, hpbw):
    theta = THETA_MOON_RAD * rho_norm
    one_way = math.exp(-4 * math.log(2) * (theta / hpbw) ** 2)
    return one_way * one_way


def weighted_quantile(pairs, q):
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    acc = 0.0
    for x, w in pairs:
        acc += w
        if acc >= q * total:
            return x
    return pairs[-1][0]


def summarize(records, orientation, dish_m, scattering, L_m=None, doppler_law="retarded_two_leg", projected_gradient=None):
    hpbw = station_beam_gain(dish_m)
    weighted = []
    total = 0.0
    for u, rho, delay, df_retarded, xnorm, area_mass in records:
        sw = math.exp(-R_MOON_M * u / L_m) if L_m else 1.0
        w = area_mass * beam_weight(rho, hpbw) * sw
        df = projected_gradient * (xnorm * R_MOON_M) if projected_gradient is not None else df_retarded
        weighted.append((delay, df, w))
        total += w

    delay_pairs = [(tau, w) for tau, _, w in weighted]
    freq_pairs = [(nu, w) for _, nu, w in weighted]
    t_mean = sum(t * w for t, w in delay_pairs) / total
    f_mean = sum(f * w for f, w in freq_pairs) / total
    t_rms0 = math.sqrt(sum(t*t*w for t, w in delay_pairs) / total)
    t_spread = math.sqrt(max(0.0, sum((t-t_mean)**2*w for t, w in delay_pairs) / total))
    d_q = [weighted_quantile(delay_pairs, q) for q in (0.5, 0.9)]
    f_q = [weighted_quantile(freq_pairs, q) for q in (0.01, 0.99)]
    print(f"profile: doppler_law={doppler_law}; orientation={orientation}; dish_m={dish_m:g}; scatter={scattering}; L_m={L_m if L_m else 'none'}; t50_ms={d_q[0]:.6f}; t90_ms={d_q[1]:.6f}; tmean_ms={t_mean:.6f}; tRMS0_ms={t_rms0:.6f}; tRMSspread_ms={t_spread:.6f}; df_q01_q99_Hz={f_q[0]:+.3f},{f_q[1]:+.3f}; dfmean_Hz={f_mean:+.3f}")
    for w_tau in DELAY_WINDOWS_MS:
        tau_fraction = sum(w for t, _, w in weighted if t <= w_tau) / total
        for w_f in FREQ_WINDOWS_HZ:
            f_fraction = sum(w for _, f, w in weighted if abs(f) <= w_f) / total
            joint = sum(w for t, f, w in weighted if t <= w_tau and abs(f) <= w_f) / total
            factorized = tau_fraction * f_fraction
            print(f"window: doppler_law={doppler_law}; orientation={orientation}; dish_m={dish_m:g}; scatter={scattering}; delay_ms<= {w_tau:.5g}; |df_Hz|<= {w_f:.5g}; Fdelay={tau_fraction:.6f}; Fdoppler={f_fraction:.6f}; Fjoint={joint:.6f}; Ffactorized={factorized:.6f}; coupled_minus_product_pp={(joint-factorized)*100:+.3f}")


def main():
    print("windows: spectral half-width ±112.5Hz is the existing 225Hz three-carrier default; ±50Hz is a tighter sensitivity; delays are first-53.68us historical-core scale, 0.17832ms exponential-profile t90 scale, 1ms sensitivity, and 11.591ms infinite-range geometric support (not all project acceptance windows)")
    for orientation in ("transverse_y_orthogonal_stress", "orbit_normal_prograde_sync"):
        records = make_geometry(orientation)
        for dish in (3.0, 5.0):
            summarize(records, orientation, dish, "uniform_projected_albedo")
            # L from the previous conditional exponential profile fit to its
            # historical 50%-within-5mi constraint; not a 5.76-GHz calibration.
            L = 11720.7 if dish == 3.0 else 11786.6
            summarize(records, orientation, dish, "exp_depth_50pct_first5mi", L)
        if orientation == "transverse_y_orthogonal_stress":
            for law, gradient in SOURCE_GRADIENTS_HZ_PER_M.items():
                print(f"velocity_law_definition: {law}; K_Hz_per_km={gradient*1000:.6f}; delta_f=K*x_along_projected_gradient; source spans are DE436 model-predicted 35Hz/503km or 90Hz/1118km at 7.209125GHz, frequency-scaled to 5.760GHz; this linear extrapolation over the lunar disk is a conditional shape, not a full-disk observation")
                for dish in (3.0, 5.0):
                    summarize(records, orientation, dish, "uniform_projected_albedo", doppler_law=law, projected_gradient=gradient)
                    L = 11720.7 if dish == 3.0 else 11786.6
                    summarize(records, orientation, dish, "exp_depth_50pct_first5mi", L, law, gradient)
    print("point_alternative: a delta at the subradar point gives 100% in each listed positive delay/frequency rectangle; it suppresses all distributed delay/Doppler tails and is not an empirical lunar profile")
    print("falsifier: a time-tagged coded echo or independently referenced CW spectrum across multiple lunar pointings/epochs should test joint (delay, differential Doppler) occupancy; if no coupling survives after exact geometry/beam normalization, retain factorized marginals")


if __name__ == "__main__":
    main()
