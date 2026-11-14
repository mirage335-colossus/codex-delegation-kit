#!/usr/bin/env python3
"""Conditional antenna-to-input calculations from the inspected 2025/2010 papers.
Not measurements of a common link or product qualification. See chapter addendum.
"""
import math
MU0 = 4*math.pi*1e-7
# Ai et al. (2025): 7.8 kHz, H=47.32 dB re 1 uA/m at 120 m;
# circuit reports Z=0.88+j7.48 ohm and C=3 uF; another run reports 23 A.
f=7800.0
h_dbua=47.32
H=1e-6*10**(h_dbua/20)
B=MU0*H
print('Ai et al. (2025), measured field marker at 120 m')
print(f'H={H:.6g} A/m RMS-equivalent if reported amplitude is RMS; B=mu0*H={B*1e12:.4g} pT')
# Thomson et al. (2010): 60 turns, 0.50 x 0.58 m loop. Use rectangular area.
N, A = 60.0, 0.50*0.58
voc=2*math.pi*f*N*A*B
print(f'Thomson 60-turn 0.50x0.58m receive loop, aligned/open-circuit Voc={voc*1e6:.4g} uV')
for en in (1e-9,):
    cn0=20*math.log10(voc/en)
    cn225=cn0-10*math.log10(225)
    print(f'conditional receiver input voltage noise={en*1e9:g} nV/sqrtHz: C/N0={cn0:.2f} dB-Hz; C/N(225Hz)={cn225:.2f} dB')
# Nicholson (2015): quoted ~0.12 fT received magnetic field at 8.822 kHz,
# 6194 km, ~150 uW ERP, coded 8 s symbols. Field/combined E+H-plane ambiguity remains.
f2=8822.0
B2=0.12e-15
voc2=2*math.pi*f2*N*A*B2
print('\nNicholson (2015) quoted 0.12 fT case, conditional same receive loop/alignment')
print(f'Voc={voc2*1e9:.4g} nV RMS; for 1 nV/sqrtHz C/N0={20*math.log10(voc2/1e-9):.2f} dB-Hz')
cn0_nich=-22.23
print(f'paper-derived C/N0≈{cn0_nich:.2f} dB-Hz implies white input voltage density {voc2/10**(cn0_nich/20)*1e9:.3g} nV/sqrtHz at this hypothetical sensor plane')
print(f'flat white-noise-only C/N in 225Hz={cn0_nich-10*math.log10(225):.2f} dB; at 0.125Hz={cn0_nich-10*math.log10(.125):.2f} dB')
# Ai impedance and capacitor: a possible (not verified loaded) series RLC interpretation.
R, X = .88, 7.48
L=X/(2*math.pi*f)
C_tune=1/((2*math.pi*f)**2*L)
Q=X/R
x=2*Q*(225/2)/f
mag_db=-10*math.log10(1+x*x)
phase=math.degrees(math.atan(x))
print('\nConditional series-equivalent reading of Ai antenna Z')
print(f'L={L*1e3:.4g} mH; equivalent series tuning C={C_tune*1e6:.4g} uF; component-Q=|X|/R={Q:.3g}')
print(f'one-pole 225-Hz span at nominal f: edge magnitude={mag_db:.3f} dB, phase=±{phase:.2f} deg')
print(f'3 uF at 7.8kHz |Xc|={1/(2*math.pi*f*3e-6):.3f} ohm; at 23 Arms Vc={23/(2*math.pi*f*3e-6):.1f} Vrms ({23/(2*math.pi*f*3e-6)*math.sqrt(2):.1f} Vpeak)')
print(f'23 Arms through reported 0.88-ohm real part would dissipate I^2R={23**2*R:.1f} W if same reference plane and resistance remains linear')
# Reconcile rounded field point and extrapolation; these are extrapolations only.
r_author=1446.0
threshold=.16e-12
r_calc=120*(B/threshold)**(1/3)
B_implied=threshold*(r_author/120)**3
H_implied=B_implied/MU0
h_implied_dbua=20*math.log10(H_implied/1e-6)
print('\nCubic extrapolation cross-check (not measured reach)')
print(f'rounded 47.32 dBµA/m point -> {r_calc:.1f} m at 0.16pT vs article {r_author:.0f} m; delta={r_calc-r_author:.1f} m ({100*(r_calc/r_author-1):.2f}%)')
print(f'article 1446m result implies {B_implied*1e12:.2f}pT at120m / {h_implied_dbua:.2f} dBµA/m, only {h_dbua-h_implied_dbua:.3f} dB below rounded marker')
print('Article measured range is at most 120m; both reach numbers are r^-3 threshold extrapolations, not a measured communication/link distance.')
