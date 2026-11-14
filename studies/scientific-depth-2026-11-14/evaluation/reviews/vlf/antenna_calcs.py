#!/usr/bin/env python3
"""Independent checks of first-pass VLF antenna arithmetic; not RF qualification."""
import math

c = 299_792_458.0
mu0 = 4.0 * math.pi * 1e-7

print("geometry: inner=36 Hz, Added Symbols=10")
fine = (36.0 / 6.0) * 10.0
spacing = 1.25 * fine
occupied = 3.0 * spacing
edge = occupied / 2.0
print(f"fine_rate={fine:.9g} Hz, carrier_spacing={spacing:.9g} Hz, occupied={occupied:.9g} Hz, edge={edge:.9g} Hz")

print("one-pole Q bounds")
for f0 in (3000.0, 5000.0, 8000.0, 9000.0):
    amp = [f0 / (2.0 * edge) * math.sqrt(10.0 ** (db / 10.0) - 1.0) for db in (0.5, 1.0, 3.0)]
    phase = [f0 / (2.0 * edge) * math.tan(math.radians(deg)) for deg in (5.0, 10.0)]
    print(f"{f0/1000:g} kHz: Q@0.5/1/3dB={amp[0]:.3f}/{amp[1]:.3f}/{amp[2]:.3f}; Q@5/10deg={phase[0]:.3f}/{phase[1]:.3f}")

print("one-pole response at 5 kHz and ±112.5 Hz")
for q in (10.0, 25.0, 100.0, 300.0):
    x = 2.0 * q * edge / 5000.0
    gain_db = -10.0 * math.log10(1.0 + x * x)
    phase_deg = -math.degrees(math.atan(x))
    tau = q / (math.pi * 5000.0)
    print(f"Q={q:g}: {gain_db:.4f} dB, {phase_deg:.3f} deg, tau={tau*1e3:.4f} ms, 1% settle={math.log(100)*tau*1e3:.4f} ms")

print("small-loop free-space radiation resistance, ideal uniform current")
for f in (3000.0, 5000.0, 8000.0):
    lam = c / f
    for turns, area in ((10.0, 1.0), (1.0, 56.0), (10.0, 1000.0)):
        rr = 31_200.0 * (turns * area / lam**2)**2
        print(f"f={f/1000:g} kHz, N={turns:g}, A={area:g} m2: Rrad={rr:.7g} ohm")

print("receive-loop open-circuit voltage, uniform RMS B=1 pT at 5 kHz")
for turns, area in ((1.0, 1.0), (60.0, 0.29), (10.0, 1000.0)):
    voc = 2.0 * math.pi * 5000.0 * turns * area * 1e-12
    print(f"N={turns:g}, A={area:g} m2: Voc={voc*1e9:.6g} nV")

print("Ai et al. 2025 field conversion and conditional range from 120 m")
h_dbua = 47.32
h = 10.0 ** (h_dbua / 20.0) * 1e-6
b = mu0 * h
print(f"H={h:.8g} A/m, B=mu0H={b:.8g} T={b*1e12:.5f} pT")
for threshold_pt in (0.16, 1.0, 10.0):
    for exponent in (3.0, 2.0, 1.0):
        distance = 120.0 * (b * 1e12 / threshold_pt) ** (1.0 / exponent)
        print(f"threshold={threshold_pt:g} pT, assumed r^-{exponent:g}: {distance:.2f} m")
