import math
c=299_792_458.0
k=1.380649e-23
# Independent reproduction of Sun et al. (2020), Sec. 2, Table 1, 503-km Km footprint.
f=7_209.125e6; lam=c/f; R=384_400e3
Pt=200.; Dtx=18.; etx=.50; Drx=40.; erx=.47; T=96.; B=35.; tau=10.
A_tx=etx*math.pi*Dtx**2/4; A_rx=erx*math.pi*Drx**2/4
Gt=4*math.pi*A_tx/lam**2; Gr=4*math.pi*A_rx/lam**2
sigma=.07*math.pi*(503e3/2)**2
Pr=Pt*Gt*Gr*lam**2*sigma/((4*math.pi)**3*R**4)
noise=k*T*B
dPn=noise/math.sqrt(B*tau)
print(f"Sun2020 7.209125GHz: Pr={Pr:.6e} W ({10*math.log10(Pr/1e-3):.3f} dBm); kTB={10*math.log10(noise/1e-3):.3f} dBm; Pr/kTB={10*math.log10(Pr/noise):.3f} dB")
print(f"paper Eq3: dPn={dPn:.6e} W; Pr/dPn={Pr/dPn:.1f} ({10*math.log10(Pr/dPn):.3f} dB); paper predicted Km=167000, data-integrated Km=177000, Zv=203000")
print(f"albedo .06 vs .07 power delta={10*math.log10(.06/.07):.3f} dB; source reports measured Mare Imbrium OC albedo .06, while .07 is used for pre-observation SNR estimates")
# Conditional target-band link reference, not a calibrated station or 5.8-GHz lunar measurement.
f=5.760e9; lam=c/f; a=1_737.4e3; eta=.065; R=384_400e3; Pt=40.; D=3.; aperture_eff=.55; T=80.
sigma=eta*math.pi*a*a
A=aperture_eff*math.pi*D*D/4; G=4*math.pi*A/lam**2
Pr=Pt*G*G*lam**2*sigma/((4*math.pi)**3*R**4)
N0=k*T
print(f"conditional 5.760GHz,40W,3m/3m,eta=.065,Tsys=80K: sigma={sigma:.6e}m2; G={10*math.log10(G):.3f}dBi; Pr={10*math.log10(Pr/1e-3):.3f}dBm; C/N0={10*math.log10(Pr/N0):.3f}dB-Hz")
# PDS source's factor-of-6--10 calibration offset is a conditional transfer sensitivity only.
for ratio in (6,10): print(f"PDS factor {ratio}: delta={-10*math.log10(ratio):.3f} dB")
