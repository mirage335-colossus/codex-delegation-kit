#!/usr/bin/env python3
"""Conditional VLF antenna desk checks; formulas/assumptions are in chapter.md."""
import math
C=299_792_458.0
MU0=4*math.pi*1e-7
spacing=75.0
occupied=225.0
edge=occupied/2
print('Q flatness bounds for 225-Hz occupied band, one-pole resonator, edge=112.5 Hz')
for f0 in (3000.,5000.,8000.,9000.):
    vals=[]
    for db in (0.5,1.0,3.0):
        xmax=math.sqrt(10**(db/10)-1)
        vals.append(f'Q<={xmax*f0/(2*edge):.3g} at {db:g}dB')
    for deg in (5.,10.):
        vals.append(f'Q<={math.tan(math.radians(deg))*f0/(2*edge):.3g} at {deg:g}deg')
    print(f'f0={f0/1000:g}kHz: '+'; '.join(vals))
print('\nOne-pole detuning response at f0=5kHz and occupied band edge')
for q in (10.,25.,100.,300.):
    x=2*q*edge/5000
    amp_db=-10*math.log10(1+x*x)
    phase_deg=-math.degrees(math.atan(x))
    tau=q/(math.pi*5000)
    settle99=math.log(100)*tau
    print(f'QL={q:g}: edge_amp={amp_db:.3f}dB edge_phase={phase_deg:.2f}deg; tau={tau*1000:.3f}ms; 1%settle={settle99*1000:.2f}ms')
print('\nSmall-loop radiation-resistance scale, Rr=31200*(N*A/lambda^2)^2 ohm')
for f in (3000.,5000.,8000.):
    lam=C/f
    for n,a,label in ((10.,1.,'10turn 1m2'),(1.,56.,'1turn 56m2'),(10.,1000.,'10turn 1000m2')):
        rr=31200*(n*a/(lam*lam))**2
        print(f'f={f/1000:g}kHz {label}: lambda={lam/1000:.1f}km Rrad={rr:.4g}ohm')
print('\nReactive-field scale r=lambda/(2pi) and dipole Hnear/Hfar scale comparison')
for f in (3000.,5000.,8000.):
    lam=C/f
    print(f'f={f/1000:g}kHz lambda={lam/1000:.1f}km r_lambda_2pi={lam/(2*math.pi)/1000:.2f}km')
print('\nLoop open-circuit induced voltage per 1 pT RMS B at f=5kHz, V=2pi*f*N*A*B')
for n,a,label in ((1.,1.,'1turn 1m2'),(60.,.29,'60turn 0.29m2'),(10.,1000.,'10turn 1000m2')):
    v=2*math.pi*5000*n*a*1e-12
    print(f'{label}: {v*1e9:.4g}nV RMS')
print('\n7.8kHz nanocrystalline paper measured field conversion')
h_dbua=47.32
H=1e-6*10**(h_dbua/20)
B=MU0*H
print(f'47.32dB(uA/m) -> H={H:.5g}A/m, B={B:.5g}T={B*1e12:.4g}pT')
for threshold_pt in (.16,1.,10.):
    r=120*(B/(threshold_pt*1e-12))**(1/3)
    print(f'pure 1/r^3 extrapolation to {threshold_pt:g}pT: {r:.1f}m')
