#!/usr/bin/env python3
"""At 5.760 GHz, compare angular power laws, observing conditions, and reductions.

Standalone reference calculation. Uses the prior exact retarded two-leg point
function and declared Gaussian beam, and the sibling atmosphere reference when
available. No product code or receiver is loaded.
"""
import argparse
import bisect
import cmath
import importlib.util
import math
from pathlib import Path
from typing import NamedTuple
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent

def from_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Its CLI accepts a positional radial count and parses it at import time.
saved_argv = sys.argv
try:
    sys.argv = [sys.argv[0]]
    geom = from_file("prior_geometry", ROOT / "eme/eme_joint_delay_doppler.py")
finally:
    sys.argv = saved_argv
atmosphere = from_file("endpoint_case", ROOT / "eme-atmosphere/endpoint_case.py")
C, F, D, R = geom.C, geom.F_HZ, geom.D_M, geom.R_MOON_M
LAMBDA, K_B = C/F, 1.380649e-23
T_SKY, T_GROUND, T_MOON = 5., 290., 210.  # Rayleigh-Jeans K, conditional
CLEAR_SPILL = .05
T_RX = 100 - (1-CLEAR_SPILL)*T_SKY - CLEAR_SPILL*T_GROUND
ORIENT = "transverse_y_orthogonal_stress"
GRAD = geom.SOURCE_GRADIENTS_HZ_PER_M["Sun2020_Zv_90Hz_1118km_scaled"]
DELAY = (.05368, .17832, 1., 11.591)
FREQ = (50., 112.5)
CHECKS = ((.4,30.), (3.,75.))        # not boundaries used in tap fitting
PHASE = ((0.,75.,0.), (0.,150.,0.), (.005,0.,0.), (.02,0.,0.),
         (.1,0.,0.), (1.,0.,0.), (.02,150.,0.), (0.,0.,10.), (0.,0.,50.))
TAU = 2*math.pi

class Row(NamedTuple):
    delay_ms: float
    f_grad: float
    f_exact: float
    x: float
    y: float
    rho2: float
    ring: int

def b_db(ratio):
    return 10*math.log10(ratio) if ratio > 0 else -math.inf

def sample_grid(n, nphi):
    """The previous orthographic hemisphere/ring grid, with identical path function."""
    t0, f0 = geom.retarded_echo((0.,0.,-R), ORIENT)
    az = [(math.cos((j+.5)*TAU/nphi), math.sin((j+.5)*TAU/nphi))
          for j in range(nphi)]
    rings, rows = [], []
    for i in range(n):
        slo, shi = i/n, (i+1)/n
        u = (.5*(slo+shi))**2
        ds = shi**2-slo**2
        m = 1-u
        rho2 = 1-m*m
        r = math.sqrt(rho2)
        rings.append((u, m, rho2, 2*ds/nphi))
        for co, si in az:
            x, y = r*co, r*si
            t, f = geom.retarded_echo((x*R, y*R, -m*R), ORIENT)
            rows.append(Row(1000*(t-t0), GRAD*x*R, f-f0, x, y, rho2, i))
    return rings, rows, t0, f0

def shape_h(c, m):
    return (c/2) / (m**4+c*(1-m*m))**1.5

def bare_rings(rings, nphi, dish, hpbw):
    rings_w, norms = {}, {}
    l_m = 11720.7 if dish==3 else 11786.6
    def add(name, weights):
        integral = math.fsum(weights)*nphi
        norms[name] = integral
        rings_w[name] = [w/integral for w in weights]
    def raw_h(c):
        return [shape_h(c,m)*area for _,m,_,area in rings]
    add("U", [m*area for _,m,_,area in rings])
    add("E", [math.exp(-R*u/l_m)*m*area for u,m,_,area in rings])
    add("D2", [m*m*area for u,m,_,area in rings])
    add("H32", raw_h(32.))
    add("H100", raw_h(100.))
    # Match *one* observed statistic of the earlier illustrative law (its
    # centered on-beam first-window mass), using the prior geometry's u cutoff
    # here for the fit. Retarded same-window mass is independently reported.
    core_u = 5*1609.344/R
    q = 4*math.log(2)*(.25/hpbw)**2
    beam = [math.exp(-2*q*rho2) for _,_,rho2,_ in rings]
    def beam_cdf(w):
        weighted = [a*b for a,b in zip(w,beam)]
        return math.fsum(x for (u,_,_,_),x in zip(rings,weighted) if u<=core_u)/math.fsum(weighted)
    target = beam_cdf(rings_w["E"])
    lo, hi = 100., 2000.
    for _ in range(36):
        c = .5*(lo+hi)
        if beam_cdf(raw_h(c)) < target:
            lo = c
        else:
            hi = c
    cfit = .5*(lo+hi)
    add("Hfit", raw_h(cfit))
    rings_w["H100+D20"] = [.8*a+.2*b for a,b in zip(rings_w["H100"], rings_w["D2"])]
    assert abs(norms["U"]-1)<2/len(rings)**2 and abs(norms["D2"]-2/3)<2/len(rings)**2
    for v in rings_w.values():
        assert abs(math.fsum(v)*nphi-1)<2e-14
    return rings_w, norms, cfit, target

class Station(NamedTuple):
    dish: float
    power: float
    gain: float
    hpbw: float
    main_eff: float
    pr_unbeam: float

def station(dish, power):
    gain = 4*math.pi*.55*math.pi*(dish/2)**2/LAMBDA**2
    hpbw = math.degrees(geom.station_beam_gain(dish))
    omega_g = math.pi*math.radians(hpbw)**2/(4*math.log(2))
    eff_mb = gain*omega_g/(4*math.pi)
    pr = power*gain**2*LAMBDA**2*(.06*math.pi*R**2)/((4*math.pi)**3*D**4)
    return Station(dish,power,gain,hpbw,eff_mb,pr)

def beams(rows, station, tx=(0.,0.), rx=(0.,0.)):
    q0=4*math.log(2)/station.hpbw**2
    btx, brx = tx[0]**2+tx[1]**2, rx[0]**2+rx[1]**2
    gauss_tx = [math.exp(-q0*(.25**2*r.rho2-.5*(r.x*tx[0]+r.y*tx[1])+btx)) for r in rows]
    gauss_rx = [math.exp(-q0*(.25**2*r.rho2-.5*(r.x*rx[0]+r.y*rx[1])+brx)) for r in rows]
    return [a*b for a,b in zip(gauss_tx,gauss_rx)], gauss_rx

def apply_beam(rows, bare, beamprod):
    return [bare[r.ring]*b for r,b in zip(rows,beamprod)]

def quantile(values, weights, total, order, sizes):
    ans=[]; acc=0.; i=0
    for j in order:
        acc += weights[j]
        while i<len(sizes) and acc>=sizes[i]*total:
            ans.append(values[j])
            i+=1
        if i==len(sizes):
            return ans
    raise ValueError("quantile outside mass")

def rectangle(t, f, w, delay, freq, shift_ms=0., shift_hz=0.):
    return math.fsum(p for u,v,p in zip(t,f,w)
                     if 0<=u+shift_ms<=delay and abs(v+shift_hz)<=freq)

def summarize(t,f,w,ti,fi):
    total = math.fsum(w)
    t50,t90,t99 = quantile(t,w,total,ti,(.50,.90,.99))
    f01,f99 = quantile(f,w,total,fi,(.01,.99))
    return total, t50,t90,t99,f01,f99

def field_characteristic(t,f,x,w,queries):
    total=math.fsum(w)
    return [sum(p*cmath.exp(1j*TAU*(b*sec-a*.001*hz-u*R/(D*LAMBDA)*base))
                for a,b,u,p in zip(t,f,x,w))/total
            for sec,hz,base in queries]

def look_stats(t,f,x,w,gap,m,coherent=0.):
    rho=field_characteristic(t,f,x,w,[(i*gap,0.,0.) for i in range(1,m)])
    var_one=(1-coherent)**2+2*coherent*(1-coherent)
    off=[(1-coherent)**2*abs(v)**2+2*coherent*(1-coherent)*v.real for v in rho]
    cv_sum=math.sqrt((m*var_one+2*sum((m-l)*v for l,v in enumerate(off,1)))/m**2)
    return abs(rho[0]), math.sqrt(var_one), cv_sum, var_one/cv_sum**2

def grids(t,f,x,w, delay_edges=(), freq_edges=()):
    bins={}
    for a,b,u,p in zip(t,f,x,w):
        if p==0:
            continue
        bin_id=(bisect.bisect_left(delay_edges,a),bisect.bisect_left(freq_edges,b))
        row=bins.setdefault(bin_id,[0.,0.,0.,0.])
        row[0]+=p; row[1]+=a*p; row[2]+=b*p; row[3]+=u*p
    return tuple(zip(*[(a/p,b/p,u/p,p) for p,a,b,u in bins.values()]))

def moment_cells(t,f,x,w,queries):
    """Local Gaussian characteristic in a few joint bins, retaining cross moments.

    This is only a covariance proxy: it has no compact positive-delay support
    and is not used for window power, phase synthesis or a runtime tap model.
    """
    bins={}
    for a,b,u,p in zip(t,f,x,w):
        if p==0:
            continue
        key=(bisect.bisect_left((.05368,.17832,1.,4.),a),
             bisect.bisect_left((-50.,0.,50.),b))
        m=bins.setdefault(key,[0.]*10)
        for j,v in enumerate((1.,a,b,u,a*a,b*b,u*u,a*b,a*u,b*u)):
            m[j]+=p*v
    masses=[m[0] for m in bins.values()]
    means=[tuple(v/m[0] for v in m[1:4]) for m in bins.values()]
    ans=[]
    for sec,hz,base in queries:
        A,B,X=-.001*hz,sec,-R/(D*LAMBDA)*base
        z=0j
        for m,(a,b,x) in zip(bins.values(),means):
            mu=A*a+B*b+X*x
            var=(A*A*m[4]+B*B*m[5]+X*X*m[6]+2*(A*B*m[7]+A*X*m[8]+B*X*m[9]))/m[0]-mu**2
            z+=m[0]*cmath.exp(1j*TAU*mu-.5*TAU**2*max(0.,var))
        ans.append(z/math.fsum(masses))
    return len(bins),ans

def approx(t,f,x,w,label):
    ref=field_characteristic(t,f,x,w,PHASE)
    training=tuple((d,f) for d in DELAY[:3] for f in FREQ)
    total=math.fsum(w)
    ref_rect=[rectangle(t,f,w,d,v)/total for d,v in training+CHECKS]
    print(f"covariance {label} (phase-aware abs); queries_t_ms_f_Hz_baseline_m="+
          ",".join(f"{dt*1000:g}/{df:g}/{b:g}" for dt,df,b in PHASE)+
          "; abs_rho="+",".join(f"{abs(z):.4f}" for z in ref))
    # Preserve the physical common phase/reference for the scalar. Centroid
    # cells preserve mean mass and joint-bin moments, not within-cell variance.
    methods=[("point",((0.,),(0.,),(0.,),(total,))),
             ("two_delay",grids(t,f,x,w,(.17832,),())),
             ("9cell",grids(t,f,x,w,(.17832,1.),(-50.,50.))),
             ("20cell",grids(t,f,x,w,(.05368,.17832,1.,4.),(-50.,0.,50.)))]
    for name,(tc,fc,xc,wc) in methods:
        chk_r=[rectangle(tc,fc,wc,d,v)/math.fsum(wc) for d,v in training+CHECKS]
        vals=field_characteristic(tc,fc,xc,wc,PHASE)
        difftr=max(abs(a-b) for a,b in zip(ref_rect[:len(training)],chk_r[:len(training)]))
        diffho=[abs(a-b) for a,b in zip(ref_rect[len(training):],chk_r[len(training):])]
        es=[abs(a-b) for a,b in zip(ref,vals)]
        print(f"reduce {label} {name}: K={len(tc)} max_grid_pp={difftr*100:.2f} "
              f"holdout_pp={diffho[0]*100:.2f},{diffho[1]*100:.2f} "
              f"rho_err75_150={max(es[:2]):.3f} rho_err_5_20ms={max(es[2:4]):.3f} "
              f"rho_err_100_1000ms={max(es[4:6]):.3f} rho_err_joint20ms150Hz={es[6]:.3f}")
    k,vals=moment_cells(t,f,x,w,PHASE)
    es=[abs(a-b) for a,b in zip(ref,vals)]
    print(f"reduce {label} Gaussian_bins (covariance_only): K={k} "
          f"rho_err75_150={max(es[:2]):.3f} rho_err_5_20ms={max(es[2:4]):.3f} "
          f"rho_err_100_1000ms={max(es[4:6]):.3f} rho_err_joint20ms150Hz={es[6]:.3f}")
    for gap in (.005,.025,.1):
        for coh in (0.,.5):
            cor,one,cv,eff=look_stats(t,f,x,w,gap,4,coh)
            print(f"looks {label} gap_ms={gap*1000:g} coherent_power={coh:g} |rho1|={cor:.4f} CV1={one:.4f} CV4={cv:.4f} N_eff={eff:.3f}")

def temperatures(s, moon_coupling, ground_fraction, eta_rx=1., emit=0.):
    # Spill and non-main-beam cold sky explicitly bypass modeled beam slab.
    side_sky = 1-s.main_eff-ground_fraction
    assert side_sky>=0
    off=T_RX+side_sky*T_SKY+ground_fraction*T_GROUND+s.main_eff*(eta_rx*T_SKY+emit)
    on=off+s.main_eff*eta_rx*(T_MOON-T_SKY)*moon_coupling
    return off,on

def run(n,nphi,overview):
    rings,rows,t0,f0=sample_grid(n,nphi)
    t=[r.delay_ms for r in rows]; f=[r.f_grad for r in rows]; fe=[r.f_exact for r in rows]; x=[r.x for r in rows]
    ti=sorted(range(len(t)),key=t.__getitem__); fi=sorted(range(len(f)),key=f.__getitem__)
    fei=sorted(range(len(fe)),key=fe.__getitem__)
    print(f"reference RF={F/1e9:.3f} GHz lambda={LAMBDA:.6f}m t0={t0:.9f}s "
          f"common={f0-F:+.3f}Hz geometry={ORIENT} points={len(rows)} ({n}x{nphi}) "
          f"sampled tau_max={max(t):.6f}ms gradient max={max(f):.3f}Hz retarded max={max(fe):.3f}Hz")
    print("weights: U=uniform projected; E=prior exponential depth; D2=cos^2 per surface; "
          "Hnn=Hagfors C; Hfit=single on-beam early fraction fit; H100+D20=80/20 unilluminated OC power")
    print("quantiles: t50/90/99 ms, f01/99 Hz; windows (first0.05368ms,0.17832ms,1ms,11.591ms) x (+/-50,+/-112.5Hz).")
    main_data=None
    for d,pt in ((3.,37.),(5.,70.)):
        s=station(d,pt)
        bare,norm,cfit,target=bare_rings(rings,nphi,d,s.hpbw)
        b,rxb=beams(rows,s)
        q=4*math.log(2)*(.25/s.hpbw)**2
        up=apply_beam(rows,bare["U"],b)
        assert abs(math.fsum(up)-(-math.expm1(-2*q)/(2*q))) < 4/n**2
        prior=rectangle(t,f,up,1.,50.)/math.fsum(up)
        assert abs(prior-.212171)<.003 if d==5 else prior>.1
        coupling=q*math.fsum(apply_beam(rows,bare["U"],rxb))
        assert abs(coupling-(-math.expm1(-q)))<4/n**2
        print(f"station dish={d:g}m Pt={pt:g}W G={b_db(s.gain):.5f}dBi HPBW={s.hpbw:.6f}deg "
              f"main_eff={s.main_eff:.6f} T_rx={T_RX:.2f}K unweighted_Pr={b_db(s.pr_unbeam/1e-3):.5f}dBm main_Moon_f={coupling:.6f}")
        print(f"normalization Cfit={cfit:.5f} core_target={target:.6f} geometric_integrals_sigma0/(pi R^2): "
              + " ".join(f"{k}={v:.7f}" for k,v in norm.items()))
        for label,weight in bare.items():
            w=apply_beam(rows,weight,b)
            for tag,fr,fidx in (("Zv",f,fi),("retarded_stress",fe,fei)):
                mass,*quant=summarize(t,fr,w,ti,fidx)
                win=[rectangle(t,fr,w,tau,nu)/mass for tau in DELAY for nu in FREQ]
                marginal_f=rectangle(t,fr,w,12.,50.)/mass
                separated=(rectangle(t,fr,w,1.,1000.)/mass)*marginal_f
                print(f"profile {d:g}m {label:8s} {tag:15s} BtxBrx={mass:.6f} "
                      f"Pr={b_db(s.pr_unbeam*mass/1e-3):.3f}dBm "
                      f"t={','.join(f'{p:.6f}' for p in quant[:3])} "
                      f"f={','.join(f'{p:+.3f}' for p in quant[3:])} "
                      f"J={','.join(f'{p:.5f}' for p in win)} J1ms50_minus_product_pp={(win[4]-separated)*100:+.3f}")
        if d==5:
            main_data=(s,q,bare)
    s,q,bare=main_data
    for name,tx,rx,ground in (("center",(0.,0.),(0.,0.),.05),
                               ("same15",(.15,0.),(.15,0.),.05),
                               ("rx30",(0.,0.),(.30,0.),.05),
                               ("opposed30",(-.30,0.),(.30,0.),.05),
                               ("same30",(.30,0.),(.30,0.),.05),
                               ("same30_spill",(.30,0.),(.30,0.),.15)):
        product,rxb=beams(rows,s,tx,rx)
        moon=q*math.fsum(apply_beam(rows,bare["U"],rxb))
        off,on=temperatures(s,moon,ground)
        print(f"pointing {name:13s} TX/RX_x_deg={tx[0]:+.2f}/{rx[0]:+.2f} ground={ground:.2f} "
              f"eta_MBdisk={s.main_eff*moon:.6f} T_off={off:.3f}K T_on={on:.3f}K Y={b_db(on/off):.3f}dB")
        for label in ("U","H100+D20","Hfit"):
            w=apply_beam(rows,bare[label],product); mass,*quant=summarize(t,f,w,ti,fi)
            fr=rectangle(t,f,w,1.,50.)/mass
            p=s.pr_unbeam*mass
            print(f"  pointing_profile {label:8s} t90={quant[1]:.6f}ms df01/99={quant[3]:+.3f}/{quant[4]:+.3f}Hz "
                  f"Pr={b_db(p/1e-3):.3f}dBm CN0={b_db(p/(K_B*on)):.3f}dBHz joint_1ms50={fr:.5f}")
    for label in ("E","Hfit","H100+D20","D2"):
        if overview:
            break
        b,_=beams(rows,s)
        w=apply_beam(rows,bare[label],b)
        approx(t,f,x,w,label)
    for label in ("U","E","Hfit","H100+D20","D2"):
        b,_=beams(rows,s)
        w=apply_beam(rows,bare[label],b)
        # Surface behind the true horizon in the sphere's finite-distance
        # monostatic geometry: bound effect of using prior orthographic cap.
        frac=math.fsum(p for r,p in zip(rows,w) if rings[r.ring][1]<R/D)/math.fsum(w)
        print(f"far_cap {label}: orthographic power in mu<R/D sliver={frac:.8g}")
    print(f"fresnel: spherical_quadratic_half_wave_m={math.sqrt((LAMBDA/2)/(1/R+1/(D-R))):.2f} "
          f"flat_screen_half_wave_m={math.sqrt(LAMBDA*(D-R)/2):.2f} "
          f"radial_perturbation_pi_phase_mm={1000*LAMBDA/4:.3f} "
          f"fractional_RF_25Hz_ppm={25/F*1e6:.6f}")
    sec=t0
    for fs in (960,6000):
        hist=(math.ceil(max(t)*.001*fs)+64)*16
        bulk=(math.ceil((sec+max(t)*.001)*fs)+64)*16
        print(f"cost Fs={fs} hypothetical_shared_tail_bytes={hist} "
              f"hypothetical_ring_if_bulk_also_stored_bytes={bulk} replay_75s_bytes={75*17*fs}")
        for paths in (1,2,9,20,len(rows)):
            print(f"  paths={paths} upper_fractional_interp_taps_per_s={paths*16*fs} "
                  f"state_at_64B_per_path={paths*64}")
    scenario(rows,t,f,s,q,bare)

def scenario(rows,t,f,s,q,bare):
    print("SCENARIO 5m 70W: same co-located geometry and shape H100+D20 "
          "OC held fixed; SC power shape D2 with unilluminated RCS 0.2*OC; "
          "independent OC and SC fields, illustrative.")
    def dbm(p):
        return b_db(p/1e-3)
    def cn0(p,temperature):
        return b_db(p/(K_B*temperature))
    for name,el,wet,delta,ground,mix,dt,df in (
        ("clear",60.,False,0.,.05,1.,0.,0.),
        ("wet",10.,True,.30,.15,.75,.050,25.),
    ):
        atmos=atmosphere.compute_case(el,wet)
        path_tx=10**(-atmos["tx_leg_loss_db"]/10)
        path_rx=10**(-atmos["rx_leg_loss_db"]/10)
        assert abs(path_rx-atmos["eta"])<5e-8
        b, rxb=beams(rows,s,(delta,0.),(delta,0.))
        moon=q*math.fsum(apply_beam(rows,bare["U"],rxb))
        w_oc=apply_beam(rows,bare["H100+D20"],b)
        w_sc=apply_beam(rows,bare["D2"],b)
        w=[mix*a+.20*(1-mix)*v for a,v in zip(w_oc,w_sc)]
        mass=math.fsum(w)
        mass_oc=math.fsum(w_oc)
        captured0=rectangle(t,f,w,1.,50.)/mass
        captured1=rectangle(t,f,w,1.,50.,dt,df)/mass
        captured2=rectangle(t,f,w,.17832,50.,dt,df)/mass
        p=s.pr_unbeam*mass*path_tx*path_rx
        off,on=temperatures(s,moon,ground,path_rx,atmos["emit_K"])
        print(f"arm {name} apparent_deg={el:.0f} aperture_offset_deg_TX_RX={delta:.2f}/{delta:.2f} "
              f"ground_frac={ground:.2f} gas_cloud_rain_db_per_leg="
              f"{atmos['gas_db']:.4f}/{atmos['cloud_db']:.4f}/{atmos['rain_db']:.4f}; "
              f"TX_RX_signal_loss_dB={atmos['tx_leg_loss_db']:.4f}/{atmos['rx_leg_loss_db']:.4f} "
              f"eta_rx={path_rx:.6f} E_rx={atmos['emit_K']:.3f}K")
        print(f"  P_unbeam_OC={dbm(s.pr_unbeam):.3f}dBm beam_loss={-b_db(mass_oc):.3f}dB "
              f"net_pol_loss={-b_db(mass/mass_oc):.3f}dB P_antenna={dbm(p):.3f}dBm "
              f"T_off={off:.3f}K T_on={on:.3f}K T_moon_excess={on-off:.3f}K "
              f"T_rx_main_emission={s.main_eff*atmos['emit_K']:.3f}K "
              f"T_ground={ground*T_GROUND:.3f}K Y={b_db(on/off):.3f}dB "
              f"CN0={cn0(p,on):.3f}dBHz CN100={cn0(p,on)-20:.3f}dB")
        print(f"  residual={dt:.3f}ms/{df:+.1f}Hz joint_1ms50_ideal={captured0:.5f} "
              f"joint_1ms50_offset={captured1:.5f} joint_178us50_offset={captured2:.5f} "
              f"captured_CN0_1ms50={cn0(p*captured1,on):.3f}dBHz "
              f"captured_CN0_178us50={cn0(p*captured2,on):.3f}dBHz")
        if wet:
            # Signal extinction remains fixed. Sensitivity to a lower source
            # function; not a scattering solver or a rain-emission estimate.
            off_half,on_half=temperatures(s,moon,ground,path_rx,.5*atmos["emit_K"])
            wet_center=rectangle(t,f,w,1.,112.5,dt,df)/mass
            print(f"  wet emission_half_sensitivity_Ton={on_half:.3f}K "
                  f"captured_CN0_1ms50={cn0(p*captured1,on_half):.3f}dBHz "
                  f"joint_1ms112p5_offset={wet_center:.5f}")
    print(f"visibility at 10deg: unobstructed if modeled 8deg local skyline; "
          "12deg blocking skyline is a separately masked physical absence: "
          "signal zero, thermal and observation validity persist if recording.")
    print(f"timing sensitivity: {25/F*1e6:.6f}ppm RF for +25Hz, independent of "
          f"1ppm sample clock accumulating {75*1e-6*1e6:.1f}us over 75s; "
          f"sampled atmospheric-excess scales 60/10degs=~18/~89ns round trip (conditional).")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radial",type=int,default=1000)
    parser.add_argument("--azimuth",type=int,default=180)
    parser.add_argument("--overview",action="store_true")
    args=parser.parse_args()
    run(args.radial,args.azimuth,args.overview)
if __name__=="__main__":
    main()
