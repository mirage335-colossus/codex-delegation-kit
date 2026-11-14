#!/usr/bin/env python3
"""Conditional 61 m VLF top-loaded monopole reference case; no site data.
Inputs and applicability boundaries are documented in chapter.md.
"""
import math
c=299_792_458.0
f=8822.0
h=61.0
a=0.003
lam=c/f
w=2*math.pi*f
# NPL DEM-EM 005 thin bare monopole self-capacitance (pF), low-frequency limit.
Cbare_pf=55.6*h/(math.log(h/a)-1)
Cbare=Cbare_pf*1e-12
# Conditional top-hat capacitance scenarios, not geometry predictions.
Cscenarios=(0.4e-9,0.8e-9,1.6e-9)
heff=0.70*h
Rrad=160*math.pi**2*(heff/lam)**2
Dmono=3.0 # ideal short monopole over perfect conducting ground, linear gain
ERP_factor=Dmono/1.64 # directivity relative to half-wave dipole, for D=3
I=1.0
Rwire=2.0
Rground=5.0
Qcoil=300.0
range_m=10_000.0
loop_NA=60*0.50*0.58
noise=1e-9
print(f'f={f:g} Hz; lambda={lam/1000:.3f} km; h={h:g} m; h/lambda={h/lam:.6f}; heff={heff:.2f} m (assumed 0.70h, not solved from this umbrella geometry)')
print(f'NPL bare 3-mm-radius vertical-wire capacitance estimate={Cbare_pf:.1f} pF (top wires increase C; NPL says simple-rod formula not applicable to top-loaded geometry)')
print(f'Rrad=160*pi^2*(heff/lambda)^2={Rrad:.6f} ohm, conditional ideal-ground short-monopole form')
print('C_total_nF  Xc_kohm  L_H  Rcoil_ohm(Q=300)  Rloss_total_ohm(plus2+5)  eta_pct  Pin_W@1A  Prad_mW  ERP_mW  Vcap_kVrms@1A')
for C in Cscenarios:
    X=1/(w*C)
    L=1/(w*w*C)
    Rcoil=X/Qcoil
    Rtot=Rrad+Rcoil+Rwire+Rground
    eta=Rrad/Rtot
    Prad=I*I*Rrad
    ERP=ERP_factor*Prad
    V=X*I
    print(f'{C*1e9:9.2f} {X/1e3:8.2f} {L:5.3f} {Rcoil:16.2f} {Rtot:21.2f} {100*eta:7.5f} {I*I*Rtot:9.2f} {Prad*1e3:8.3f} {ERP*1e3:7.3f} {V/1e3:12.2f}')
# Nominal midrange case and conditional radiative receive chain.
C=0.8e-9
X=1/(w*C)
L=1/(w*w*C)
Rcoil=X/Qcoil
Rtot=Rrad+Rcoil+Rwire+Rground
Ql=X/Rtot
BW=f/Ql
x_edge=2*Ql*(225/2)/f
edge_db=-10*math.log10(1+x_edge*x_edge)
edge_phase=math.degrees(math.atan(x_edge))
x_carrier=2*Ql*75/f
carrier_db=-10*math.log10(1+x_carrier*x_carrier)
carrier_phase=math.degrees(math.atan(x_carrier))
tau=Ql/(math.pi*f)
settle=math.log(100)*tau
# ideal free-space far-field reference, broadside, perfect ground image, no soil/guide loss
E=math.sqrt(30*Dmono*I*I*Rrad)/range_m
B=E/c
Voc=w*loop_NA*B
cn0=20*math.log10(Voc/noise)
cn225=cn0-10*math.log10(225)
# 50 to Rtot lossless transformer at tune
ratio=math.sqrt(Rtot/50)
print('\nNominal conditional case: Ctotal=0.8nF, Qcoil=300, Rwire=2ohm, Rground=5ohm, Ibase=1Arms')
print(f'Rcoil={Rcoil:.2f}ohm; Rrad={Rrad:.6f}ohm; eta={100*Rrad/Rtot:.5f}%; input real power={Rtot:.2f}W; radiated={Rrad*I*I*1e3:.3f}mW; ERP={ERP_factor*Rrad*I*I*1e3:.3f}mW')
print(f'lossless tuned 50ohm-to-{Rtot:.2f}ohm resistive match voltage ratio secondary/primary={ratio:.3f}; practical matcher losses omitted')
print(f'loaded Q={Ql:.1f}; 3dB bandwidth approx {BW:.1f}Hz; one-pole ±112.5Hz edge={edge_db:.2f}dB, phase=±{edge_phase:.1f}deg; at ±75Hz carrier offset={carrier_db:.2f}dB, phase=±{carrier_phase:.1f}deg')
print(f'field at {range_m/1000:g}km ideal free-space/perfect-ground broadside reference: E={E*1e6:.2f}uV/m; B=E/c={B*1e15:.2f}fT (not an Earth-ionosphere path prediction)')
print(f'Thomson 60-turn 0.50x0.58m loop at same-plane field: open-circuit Voc={Voc*1e9:.2f}nV; assumed 1nV/sqrtHz input noise -> C/N0={cn0:.2f}dB-Hz; C/N225={cn225:.2f}dB; no site noise or polarization loss')
print(f'circulating capacitor/antenna RMS voltage at 1Arms={X/1000:.2f}kV (peak={X*math.sqrt(2)/1000:.2f}kV); mean potential gradient over 61m={X/h:.0f}V/m, not local conductor surface field')
print(f'tank amplitude ringdown tau=Q/(pi*f)={tau*1e3:.2f}ms; 1-percent settle={settle*1e3:.1f}ms (linear one-pole estimate; tuner/PA may take longer)')
# Detuning and resonator frequency sensitivity.
df_10deg=f*math.tan(math.radians(10))/(2*Ql)
df_1db=f*math.sqrt(10**0.1-1)/(2*Ql)
df_cap=f*(1-math.sqrt(1/1.01))
x_cap=2*Ql*df_cap/f
cap_db=-10*math.log10(1+x_cap*x_cap)
cap_phase=math.degrees(math.atan(x_cap))
eta_ground50=Rrad/(Rrad+Rcoil+Rwire+50)
print(f'center detune for 10deg phase≈{df_10deg:.1f}Hz; for 1dB voltage-response loss≈{df_1db:.1f}Hz; +1% C alone shifts f downward by≈{df_cap:.1f}Hz, which is {cap_db:.1f}dB/{cap_phase:.1f}deg in this model')
print(f'if nominal ground loss is 50ohm instead of assumed5ohm, eta_rad={100*eta_ground50:.5f}%')
print('Assumptions that dominate: 0.70h effective height, top-loaded C scenarios, coil Q=300, added conductor/ground R=2/5ohm, ideal image/pattern and no propagation loss, and hypothetical 1nV/sqrtHz receive noise. None are site measurements.')
