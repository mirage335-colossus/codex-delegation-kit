"""Research desk calculations and matched ITU-R D1 analysis. Python 3.10+."""

import csv
import datetime as dt
import math as m
from pathlib import Path
import statistics as stat


ROOT = Path(__file__).resolve().parent
R_EARTH_KM = 6371.0
C_KM_S = 299792.458
P533_POLE = (78.5, -68.2)


def unit_vector(lat_lon):
    lat, lon = map(m.radians, lat_lon)
    return m.cos(lat) * m.cos(lon), m.cos(lat) * m.sin(lon), m.sin(lat)


def lat_lon(xyz):
    x, y, z = xyz
    return m.degrees(m.atan2(z, m.hypot(x, y))), m.degrees(m.atan2(y, x))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def path_geometry(tx, rx, long_way=False):
    a, b = unit_vector(tx), unit_vector(rx)
    angle = m.acos(min(1.0, max(-1.0, dot(a, b))))
    midpoint = lat_lon([(a_i + b_i) * (-1 if long_way else 1)
                        for a_i, b_i in zip(a, b, strict=True)])
    if long_way:
        angle = m.tau - angle
    return angle * R_EARTH_KM, midpoint


def magnetic_latitude(position, pole):
    return m.degrees(m.asin(dot(unit_vector(position), unit_vector(pole))))


def rise_or_set_utc(position, day, rise):
    """P.1147-4 Appendix 1 §2. Result is UTC modulo 24 hours."""
    lat, lon = position
    assert abs(lat) < 65
    y = day.timetuple().tm_yday + ((6 if rise else 18) - lon / 15) / 24
    anomaly = m.radians(0.985600*y - 3.289)
    sun_lon = anomaly + m.radians(1.916*m.sin(anomaly) + 0.020*m.sin(2*anomaly) + 282.634)
    ra = m.degrees(m.atan2(0.91746*m.sin(sun_lon), m.cos(sun_lon))) % 360
    sin_declination = 0.39782*m.sin(sun_lon)
    cos_declination = m.sqrt(1 - sin_declination**2)
    latitude = m.radians(lat)
    x = (m.cos(m.radians(90.8333)) - sin_declination*m.sin(latitude))
    x /= cos_declination*m.cos(latitude)
    if abs(x) > 1:
        return None
    hour_angle = m.degrees(m.acos(x))
    if rise:
        hour_angle = 360 - hour_angle
    return ((hour_angle + ra)/15 - 0.065710*y - 6.622 - lon/15) % 24


def transition_loss(event, relative_hours):
    if event == "sunset" and -1 < relative_hours < 4:
        t = relative_hours
        return 12.40 - 9.248*t + 2.892*t*t - 0.3343*t**3
    if event == "sunrise" and -3 < relative_hours < 1:
        t = relative_hours
        return 9.6 + 12.2*t + 5.62*t*t + 0.86*t**3
    if event == "night":
        return 0.0
    raise ValueError((event, relative_hours))


def mf_field(distance_km, geomagnetic_lat, solar_index, height_km, cmf_db, lt):
    """Conditional interior North American P.1147-4 reference, d<2000 km.

    Fixed average terminal ground, no sea gain and |I|>45 degrees both ends.
    Height 220 km is Annex 1 sensitivity conditional on F reflection.
    """
    assert 50 <= distance_km < 2000
    p = m.hypot(distance_km, 2*height_km)
    k = 2*m.pi + 4.95*m.tan(m.radians(min(60.0, abs(geomagnetic_lat))))**2
    la = k*p/1000
    b = max(0.0, (abs(geomagnetic_lat) - 45)/3)
    lr = b*solar_index/100*p/1000
    return 107 + cmf_db - 20*m.log10(p) - la - lt - lr, p, la, lr


def mf_checks():
    print("P.1147-4 conditional reference, 1000 kHz unless stated, ground-level loop")
    # WMM2025 degree-one dipole at nominal 2025.0 epoch, NOAA Table 2.
    pole = lat_lon((1410.8, -4545.4, 29351.8))
    print(f"WMM2025 epoch dipole pole lat,lon {pole[0]:.3f},{pole[1]:.3f}")
    day = dt.date(2025, 10, 15)
    next_day = day + dt.timedelta(days=1)
    for name, tx, rx in (
        ("short-inland", (42, -94), (39, -91)),
        ("longer-inland", (42, -94), (35, -88)),
    ):
        distance, midpoint = path_geometry(tx, rx)
        geomag = magnetic_latitude(midpoint, pole)
        dips = [m.degrees(m.atan(2*m.tan(m.radians(magnetic_latitude(pos, pole)))))
                for pos in (tx, rx)]
        assert all(abs(dip) > 45 for dip in dips)
        sunrise = rise_or_set_utc(midpoint, next_day, True)
        sunset = rise_or_set_utc(midpoint, day, False)
        print(f"{name}: TX{tx} RX{rx} D={distance:.2f} km midpoint="
              f"({midpoint[0]:.3f},{midpoint[1]:.3f}) geomag={geomag:.2f} "
              f"endpoint dip proxies={dips[0]:.1f}/{dips[1]:.1f} deg")
        print(f"  UTC decimal hours {day} sunset={sunset:.4f}, {next_day} sunrise={sunrise:.4f}")
        for event, t, utc in (
            ("sunset", 0, sunset),
            ("sunset", 2, sunset + 2),
            ("night", 6, sunset + 6),
            ("sunrise", -1, sunrise - 1),
            ("sunrise", 0, sunrise),
        ):
            lt = transition_loss(event, t)
            for r12 in (12, 100):
                e, p, la, lr = mf_field(distance, geomag, r12, 100.0, 0.0, lt)
                print(f"  {event:7s}{t:+d}h UTC={utc % 24:.4f} R12={r12:3d} "
                      f"p={p:.2f}km La={la:.2f} Lt={lt:.2f} Lr={lr:.2f} E={e:.2f} dBuV/m")
        e, p, _, _ = mf_field(distance, geomag, 12, 100, 0, 0)
        # The source c.m.f. is normalized to 300 V IN the skyward direction.
        # For a fixed short vertical with 300 V in the horizontal direction,
        # ideal PEC image/dipole amplitude factor is cos(elevation).
        e_fixed = e + 20*m.log10(distance/p)
        e_f, p_f, _, _ = mf_field(distance, geomag, 12, 220, 0, 0)
        e_f_fixed = e_f + 20*m.log10(distance/p_f)
        delta_10 = min(10.0, max(6.0, 0.2*abs(geomag)-2.0))
        delta_01 = min(15.0, max(11.0, 0.2*abs(geomag)+3.0))
        print(f"  reference E-mode sky-direction E={e:.2f}, E10={e+delta_10:.2f}, "
              f"E01={e+delta_01:.2f}; fixed-monopole E={e_fixed:.2f}")
        print(f"  F-mode conditional slant E={e_f:.2f}, fixed-monopole E={e_f_fixed:.2f}, "
              f"F-minus-E={e_f_fixed-e_fixed:.2f}dB; geometric excess E/F "
              f"{1000*(p-distance)/C_KM_S:.3f}/{1000*(p_f-distance)/C_KM_S:.3f} ms")
        # Flat single-hop geometric incidence at the 100-km equivalent mirror.
        cos_incidence = 200/p
        print(f"  Maximum foE for E penetration: 1.00MHz→{cos_incidence:.3f}MHz, "
              f"1.65MHz→{1.65*cos_incidence:.3f}MHz, flat mirror geometry")
    print(f"  300 V c.m.f. relative to 1 kW EIRP free-space c.m.f.: "
          f"{20*m.log10(300/m.sqrt(30*1000)):.3f} dB")


def checked_rows(name, header, width):
    with (ROOT / "scratch" / name).open(newline="") as f:
        table = csv.reader(f)
        if header:
            assert len(next(table)) == width, name
        result = list(table)
    assert all(len(row) == width for row in result), name
    return result


def coord(item):
    # D1 labels these D.M. Period separates degrees from arcminutes.
    degree, minute = map(int, item[:-1].split("."))
    assert 0 <= minute < 60 and item[-1] in "NSEW"
    return (degree + minute/60) * (-1 if item[-1] in "SW" else 1)


def available_dbm(field_dbuv_m, f_mhz, rx_dbi=0.0):
    return field_dbuv_m + rx_dbi - 20*m.log10(f_mhz) - 107.2 + 30.0


def d1_checks():
    meta = checked_rows("D1_Table1.csv", True, 12)
    obs = checked_rows("D1_Table2.csv", True, 27)
    pred = checked_rows("D1Comp.csv", False, 27)
    groups = {}
    keys = set()
    by_id = {}
    by_route_time = {}
    missing = 0
    extreme = []
    for a, b, c in zip(meta, obs, pred, strict=True):
        key = tuple(int(a[i]) for i in (0, 10, 11))
        assert key == tuple(map(int, b[:3])) == tuple(map(int, c[:3])) and key not in keys
        keys.add(key)
        identifier, year, month = key
        f_mhz, report_distance, r12 = map(float, (a[3], a[8], a[9]))
        tx = coord(a[4]), coord(a[5])
        rx = coord(a[6]), coord(a[7])
        geometry_distance, midpoint = path_geometry(tx, rx, identifier >= 169)
        mag = abs(magnetic_latitude(midpoint, P533_POLE))
        frequency_band = next(s for upper, s in ((5, "02-05"), (10, "05-10"),
                                                (15, "10-15"), (30, "15-30"))
                              if f_mhz <= upper)
        latitude_band = next(s for upper, s in ((20, "00-20"), (40, "20-40"),
                                              (60, "40-60"), (90, ">60"))
                             if mag <= upper)
        r12_band = "0-44" if r12 < 45 else "45-104" if r12 < 105 else "105+"
        circuit = (identifier, a[1], a[2], f_mhz, report_distance, mag, tx, rx, geometry_distance)
        for hour, (measured, predicted) in enumerate(zip(b[3:], c[3:], strict=True), 1):
            measured, predicted = int(measured), int(predicted)
            if measured == 99:
                missing += 1
                continue
            error = predicted - measured
            for group in ("ALL", f"f {frequency_band}", f"mag {latitude_band}",
                          f"R12 {r12_band}", "long way" if identifier >= 169 else "short way"):
                groups.setdefault(group, []).append(error)
            by_id.setdefault(circuit, []).append((key, hour, r12, measured, predicted))
            if identifier in {16, 17, 18, 19}:
                by_route_time.setdefault((year, month, hour), {})[f_mhz] = (
                    r12, measured, predicted)
            if abs(error) > 50:
                extreme.append((key, hour, f_mhz, measured, predicted, error))

    def report(label, errors):
        large = sum(abs(x) >= 10 for x in errors)
        spread = f"{stat.stdev(errors):6.2f}" if len(errors) > 1 else "   n/a"
        print(f"  {label:10s} n={len(errors):5d} bias={stat.mean(errors):+7.2f} "
              f"SD={spread} RMSE={m.sqrt(stat.mean(x*x for x in errors)):6.2f} "
              f"|error|>=10: {large}/{len(errors)}")

    print("\nD1 measured/reference prediction compared in dBuV/m (1 kW EIRP)")
    assert len(keys)*24 == len(groups["ALL"]) + missing
    print(f"  path-frequency IDs={len({k[0] for k in keys})}, unique ID/month={len(keys)} "
          f"1964-1985, observed cells={len(groups['ALL'])}, missing cells={missing}, "
          f"|error|>50 retained={len(extreme)}")
    for label, errors in sorted(groups.items()):
        report(label, errors)
    print(f"  Largest |error| rows kept (ID,YY,MM), hour, f_MHz, observed,predicted,delta: "
          f"{sorted(extreme, key=lambda x:-abs(x[-1]))[:5]}")

    for circuit, records in by_id.items():
        identifier, txname, rxname, f_mhz, dist, mag, tx, rx, geometry_distance = circuit
        if identifier not in {2, 3, 16, 17, 18, 19, 51, 100, 101, 154, 179}:
            continue
        print(f"  #{identifier} {txname} {tx} -> {rxname} {rx} "
              f"f={f_mhz}MHz published D={dist:.0f}km geom D={geometry_distance:.1f}km "
              f"|mid geomag|={mag:.2f}deg")
        report(str(identifier), [p - o for _, _, _, o, p in records])
        for key, hour, r12, observed, predicted in records[:1]:
            print(f"    observed/predicted {observed}/{predicted} dBuV/m -> "
                  f"{available_dbm(observed, f_mhz):.2f}/{available_dbm(predicted, f_mhz):.2f} "
                  f"dBm lossless 0dBi, 19{key[1]}-{key[2]:02d} hour {hour:02d} UTC, R12={r12:.0f}")

    matched = [item for item in sorted(by_route_time.items()) if len(item[1]) >= 3]
    print(f"  Oslo->Norddeich matched >=3 measured frequencies at same hour/month n={len(matched)}")
    for (yr, mn, hour), fs in matched[:5]:
        print(f"    19{yr}-{mn:02d}, UTC h={hour:02d}: "
              + ", ".join(f"{f:g} MHz {o}/{p} dBuV/m"
                          for f, (r12, o, p) in fs.items())
              + f", R12={next(iter(fs.values()))[0]:.0f}")
    # Conditional overlay on the exact first Oslo 17.1-MHz field pair. The
    # receiver-equivalent noise figure and required SNR here are test inputs.
    assert matched[0][0] == (82, 7, 1)
    r12, measured, predicted = matched[0][1][17.1]
    assert (r12, measured, predicted) == (115, -21, -8)
    fa_db, bandwidth_hz, threshold_db = 35.0, 100.0, 6.0
    noise_dbm = -174 + fa_db + 10*m.log10(bandwidth_hz)
    print(f"  Same-plane stress overlay 17.1MHz: Fa={fa_db:g}dB B={bandwidth_hz:g}Hz "
          f"input noise {noise_dbm:.2f}dBm, hypothetical threshold {threshold_db:g}dB")
    for label, field in (("observed median", measured), ("predicted median", predicted)):
        snr_db = available_dbm(field, 17.1) - noise_dbm
        dl, du = 10.0, 8.0
        margin_db = snr_db-threshold_db
        bcr = (min(100.0, 130 - 80/(1+margin_db/dl)) if margin_db >= 0
               else max(0.0, 80/(1-margin_db/du) - 30))
        print(f"    {label}: median SNR={snr_db:+.2f}dB margin={margin_db:+.2f}dB, "
              f"illustrative BCR(Dl=10,Du=8)={bcr:.1f}%")


def db_sum(values):
    return 10*m.log10(sum(10**(x/10) for x in values))


def mirror_geometry(distance_km, height_km, hops, code_delay=False):
    psi = distance_km/(hops*2*R_EARTH_KM)
    delta = m.atan((m.cos(psi)-R_EARTH_KM/(R_EARTH_KM+height_km))/m.sin(psi))
    sign = -1 if code_delay else 1
    p = 2*R_EARTH_KM*hops*m.sin(psi)/m.cos(delta+sign*psi)
    return m.degrees(delta), p, 1000*p/C_KM_S


def propagation_support(f_over_muf, delta_l, delta_u):
    if f_over_muf <= 1:
        return min(1, 1.3 - 0.8/(1+(1-f_over_muf)/(1-delta_l)))
    return max(0, 0.8/(1+(f_over_muf-1)/(delta_u-1))-0.3)


def muf_loss(ratio, layer, distance, literal):
    if ratio <= 1:
        return 0.0
    x = ratio - 1
    if literal:
        return min(130*x*x, 81) if layer == "E" else min(36*m.sqrt(x), 62)
    if layer == "E":
        return min(46*m.sqrt(x) + 5, 58)
    if distance <= 3000:
        return min(36*m.sqrt(x) + 5, 60)
    return min(70*x + 8, 80)


def digital_checks():
    print("\nP.533-14 geometry/units, conditional mode-power fixture (not climatology)")
    # Oslo -> Norddeich 686-km reference distance, f and antenna exercise inputs.
    distance, f_mhz = 686.0, 6.4
    modes = [("1E", 110, 1, 23, -4), ("1F2", 260, 1, 25, 3), ("2F2", 260, 2, 18, 3)]
    for name, h, n, ew, gain in modes:
        angle, p, tau = mirror_geometry(distance, h, n)
        _, _, code_tau = mirror_geometry(distance, h, n, code_delay=True)
        print(f"  {name} h={h}km delta={angle:.2f}° p={p:.3f}km tau={tau:.6f}ms "
              f"source tau={code_tau:.6f}ms (converted from s), Ew={ew}dBuV/m Gr={gain:+d}dBi "
              f"Pr={available_dbm(ew,f_mhz,gain):.3f}dBm")
    available = [available_dbm(ew, f_mhz, gain) for _, _, _, ew, gain in modes]
    widest = db_sum(available)
    code_aggregated_field = 5*m.log10(sum(10**(ew/5) for _, _, _, ew, _ in modes))
    print(f"  E sum={db_sum([x[3] for x in modes]):.3f}dBuV/m, "
          f"correct Pr per-mode sum={widest:.3f}dBm, "
          f"same selected set code arithmetic={available_dbm(code_aggregated_field,f_mhz,3):.3f}dBm")
    print(f"  Equal-field, equal-gain two-mode combining increase is "
          f"{10*m.log10(2):.3f}dB power sum vs {5*m.log10(2):.3f}dB source digital arithmetic")
    printed_start = mirror_geometry(distance, 110, 1)[-1]
    code_start = mirror_geometry(distance, 110, 1, True)[-1]
    # Exactly the same candidate set in both delay-window selectors.
    assert max(available) - min(available) < 10.0
    mode_counts = []
    for window_ms in (0.1, 0.4, 0.6, 1.6, 2.0):
        physical = [name for name,h,n,_,_ in modes
                    if mirror_geometry(distance,h,n)[-1]-printed_start <= window_ms]
        literal_code = [name for name,h,n,_,_ in modes
                        if mirror_geometry(distance,h,n,True)[-1]-code_start <= window_ms]
        mode_counts.append((len(physical), len(literal_code)))
        print(f"  TW={window_ms:g}ms standard geometry/threshold={physical}; "
              f"source expressions at same input={literal_code}")
    assert mode_counts == [(1, 1), (1, 2), (2, 2), (2, 3), (3, 3)]
    assert m.isclose(propagation_support(.95, .95, 1.05), .90)
    assert m.isclose(propagation_support(1.0, .95, 1.05), .50)
    assert m.isclose(propagation_support(1.05, .95, 1.05), .10)
    print("  MUF support with exact E factors (.95,1.05): "
          + ", ".join(f"{r:.3f}:{100*propagation_support(r,.95,1.05):.1f}%"
                      for r in (.92, .95, .99, 1, 1.01, 1.05, 1.08)))
    for ratio in (1.001, 1.05, 1.25, 1.5, 2):
        print(f"  f/BMUF={ratio:g}: P.533 vs source Lm dB E "
              f"{muf_loss(ratio,'E',686,True):.2f}/{muf_loss(ratio,'E',686,False):.2f}, "
              f"F2 <=3000 {muf_loss(ratio,'F2',686,True):.2f}/{muf_loss(ratio,'F2',686,False):.2f}, "
              f"F2 >3000 {muf_loss(ratio,'F2',5000,True):.2f}/{muf_loss(ratio,'F2',5000,False):.2f}")
    # P.533 Table 2(a), 62.5 <= Gn < 67.5, Northern Hemisphere.
    # A geometrically admissible short path with geomagnetic mid-lat in this row.
    distance2, mid2 = path_geometry((55, -106), (61, -104))
    gm = magnetic_latitude(mid2, P533_POLE)
    assert distance2 <= 2500 and 62.5 <= gm < 67.5
    print(f"  Conditional auroral geometry TX(55,-106) RX(61,-104) "
          f"D={distance2:.1f}km Gn={gm:.2f}° "
          f"midpoint ({mid2[0]:.2f},{mid2[1]:.2f}), 05 LT≈{(5-mid2[1]/15)%24:.2f} UTC")
    for ns, t, loss in (("Jan", 5, 16), ("Jan", 14, 2),
                        ("Jul", 5, 4.8), ("Jul", 14, 4.8)):
        print(f"  Table 2(a), Gn~65°, local h={t:02d}, {ns}: Lh={loss:g}dB, "
              f"field {23-loss:.1f}dBuV/m if pre-Lh field is 23")
    # Attachment 1's conditional boundary level for one dominant F mode.
    for tau_ms, f_hz in ((0, 0), (1, 3), (2, 6), (3, 9)):
        print(f"  Equatorial-scatter edge relative power for Δt={tau_ms}ms, |Δf|={f_hz}Hz: "
              f"{10*m.log10(0.056*m.exp(-0.5*tau_ms**2)):.2f}dB")
    for month in (3, 6):
        occurrence = (0.1+0.008*100)*(0.55+0.45*m.sin(m.radians(60*(month-1.5))))
        print(f"    Model occurrence fraction at |dip|=10deg, 21 LT, R12=100, "
              f"month={month}: {occurrence:.2f}; application conditional on edge crossing")


if __name__ == "__main__":
    mf_checks()
    d1_checks()
    digital_checks()
