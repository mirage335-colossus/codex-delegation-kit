#!/usr/bin/env python3
"""Deterministic desk checks; transport models only, no pump DSP or qualification."""
from cmath import exp
from math import atan, cos, degrees, log, log10, pi, sin, sqrt
from statistics import NormalDist


C = 299_792_458.0
K = 1.380649e-23
DEFAULT_B = 3 * 1.25 * (36 / 6) * 10
DEFAULT_DELTA = DEFAULT_B / 3
EDGE = DEFAULT_B / 2


def db10(p):
    return 10 * log10(p)


def antenna():
    print('loaded linear-resonator transfer: default band edge +/-112.5 Hz')
    for fc in (5000, 8000):
        for q in (10, 50, 200, 1000):
            x = 2 * q * EDGE / fc
            xoff = 2 * q * (EDGE + 12) / fc
            tau = q / (pi * fc)
            print(f'{fc/1000:g}k Q={q:4d}: edge {db10(1/(1+x*x)):7.2f}dB '
                  f'with 12Hz detune {db10(1/(1+xoff*xoff)):7.2f}dB; '
                  f'edge phase {degrees(-atan(x)):6.2f}deg; center group delay '
                  f'{1000*tau:6.3f}ms; settling 1% {-1000*tau*log(.01):7.2f}ms')
    q = 200
    fc = 8000
    tau = q / (pi * fc)
    # Removing a nominal common delay does not remove amplitude or dispersion.
    x = 2 * q * EDGE / fc
    print(f'8k/Q200 after removing local center delay: unwrapped edge phase residual '
          f'{degrees(x-atan(x)):.2f}deg, amplitude {sqrt(1/(1+x*x)):.4f}')
    print()


def two_components():
    print('coherent two-component transfer, deterministic relative phase pi at center')
    tau = .007
    for r in (.3, .9, .99, 1.01):
        # H(f)=1-r exp(-i 2 pi f tau), sum-of-ray energy=1+r^2.
        h0 = 1 - r
        slope_group_delay = -tau*r/(1-r)
        phases = [abs(1-r*exp(-2j*pi*f*tau))**2/(1+r*r) for f in (0, 75, 112.5)]
        print(f'r={r:4.2f} center/75/112.5 power vs tap-power sum '
              + '/'.join(f'{db10(p):.2f}dB' for p in phases)
              + f'; effective center group delay {1000*slope_group_delay:+.2f}ms, actual support 0/7ms')
        assert h0 != 0
    print('local independent equal-power taps: center covariance vs band-flat mismatch')
    for us in (100, 300, 1000, 3000, 7000, 10000):
        tau = us / 1e6
        adjacent_rho = abs((1+exp(-2j*pi*DEFAULT_DELTA*tau))/2)
        separated_rho = abs((1+exp(-4j*pi*DEFAULT_DELTA*tau))/2)
        delta = DEFAULT_DELTA / 2  # nominal within one carrier
        thru_center = 2*sin(pi*delta*tau)**2
        print(f'{us:5d}us |rho_adj|={adjacent_rho:.4f} |rho_outer|={separated_rho:.4f} '
              f'center-gain within-edge error/P={thru_center:.4f}')
    print()


def group_phase():
    print('path Doppler and LO error; algebraic examples')
    for f in (8000, 1e6, 30e6, 5.8e9):
        ppm = .1e-6
        print(f'{f:g}Hz RF: 0.1ppm={f*ppm:9.4g}Hz, 1m/s geometry={-f/C:11.6f}Hz')
    tecu = 1e16
    f = 5.8e9
    print(f'5.8GHz straight-plasma asymptote, one leg, 1 TECU: group delay {1e12*40.3*tecu/(C*f*f):.4g}ps; '
          f'at 1 TECU/s carrier phase derivative +{40.3*tecu/(C*f):.4g}Hz')
    print('HF synthetic falsifier: d(tau_group)/dt=0, d(phi)/(2pi dt)=+5 Hz; fixed delay+NCO reproduces it.')
    print('A geometric-only delay slope forcing +5 Hz at 10 MHz would falsely impose -0.5 us/s in group delay.')
    print()


def moon():
    print('synthetic retarded-leg discriminator (not ephemeris): equatorial planar site/Moon geometry')
    f = 5.8e9
    earth_r = 6_378_137.0
    d = 384_400_000.0
    w = 2*pi/86164.0905
    v_orbit = 1022.0
    # Local inertial Cartesian analytic geometry. x radial recedes 30m/s.
    def moon_pos(t):
        return d + 30*t, v_orbit*t

    def site(t, lon):
        return earth_r*cos(lon+w*t), earth_r*sin(lon+w*t)

    def dist(a, b):
        return sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

    def path(t_rx, txlon, rxlon):
        tb = t_rx
        for _ in range(6):
            tb = t_rx-dist(moon_pos(tb), site(t_rx, rxlon))/C
        te = tb
        for _ in range(6):
            te = tb-dist(moon_pos(tb), site(te, txlon))/C
        return (dist(moon_pos(tb),site(te,txlon)) + dist(moon_pos(tb),site(t_rx,rxlon))), te

    def same_epoch(t, txlon, rxlon):
        return dist(moon_pos(t),site(t,txlon)) + dist(moon_pos(t),site(t,rxlon))

    def derivative(fn):
        h=0.5
        return (fn(h)-fn(-h))/(2*h)

    for ta, ra in ((30, 30), (30, -60), (0, 0)):
        a,b=ta*pi/180,ra*pi/180
        ret,te=path(0,a,b)
        snap=same_epoch(0,a,b)
        ret_hz=-f/C*derivative(lambda t:path(t,a,b)[0])
        snap_hz=-f/C*derivative(lambda t:same_epoch(t,a,b))
        geo_hz=-2*f*30/C
        print(f'Tx/Rx long {ta:+d}/{ra:+d}deg path {ret/C:.9f}s; '
              f'retarded {ret_hz:+.3f}Hz; simultaneous topocentric {snap_hz:+.3f}Hz; '
              f'retard delta {(ret-snap)/C*1e6:+.3f}us; geocenter {geo_hz:+.3f}Hz')
        assert abs(ret/C + te) < 2e-14
    lunar_radius = 1_737_400.
    tau = 2*lunar_radius/C
    print(f'monostatic center-to-near-surface delay difference (and plane-wave near-to-limb span): {tau*1e3:.4f}ms')
    print('full-depth bound is not RMS or a power quantile; pointing/scatter/polarization weight the observed taps')
    # Falsifier: a *digital* NCO cannot recover information discarded before
    # ADC/decimation. Aliased centers below apply only to the unfiltered ideal.
    fs=960.
    for df in (150., 390., 580., 2013.225, -9955.473):
        alias=(df+fs/2)%fs-fs/2
        band_inside=abs(df)+EDGE < fs/2
        print(f'960sps complex capture, center {df:+.3f}Hz: default band fits strict Nyquist {band_inside}; '
              f'if accidentally unfiltered, center aliases to {alias:+.3f}Hz (never validated recovery)')
    rate = .5  # Hz/s; deliberate conditional residual-slope example.
    print(f'Accounting for constant CFO alone with {rate:g}Hz/s linear residual slope leaves '
          f'{.5*rate*(16/2)**2:.1f} cycles at 16s aperture edge (center reference).')
    print('Group time shear for pure nondispersive geometry with |fc shift|=10kHz at 5.8GHz:')
    relative = 1e4/f
    for span in (16, 256, 2048):
        tau_change = relative*span
        print(f't={span:4d}s: tau changes {1e6*tau_change:8.3f}us, {fs*tau_change:6.3f} capture samples; '
              f'far edge drift after RF-only correction {EDGE*tau_change:6.4f} cycles')
    print()


def referenced_noise():
    print('one loss with physical temp + reference move; both planes yield same C/N0')
    for ta in (35., 290., 1e5):
        loss, tp, tr = 10**(.8/10), 290., 65.
        p = 10**(-143/10)*.001
        tin = ta+(loss-1)*tp+loss*tr
        tout = ta/loss+(1-1/loss)*tp+tr
        cn0in = db10(p/(K*tin))
        cn0out = db10((p/loss)/(K*tout))
        assert abs(cn0in-cn0out) < 1e-12
        print(f'Ta={ta:9.1f}K T_in={tin:10.3f}K T_out={tout:10.3f}K C/N0={cn0in:+.3f} dB-Hz '
              f'vs ignoring feeder and Rx {db10(p/(K*ta)):+.3f}')
    print('complex IQ: for unit power before the selected channel filter, C/N0=40 dB-Hz and B=225 Hz,')
    for fs in (960, 1920, 12000):
        var = fs/1e4
        print(f'Fs={fs:5d}: total unfiltered complex var {var:.4g}, in-B var {var*225/fs:.4g}, '
              f'SNR at unit power {db10(1/(var*225/fs)):+.3f}dB')
    # Jan 2015 primary operator report, 8.822 kHz, post-sferic-blanking estimate.
    # Scaling is conditional on equal received power and unchanged effective noise PSD.
    vlf_snr_db, vlf_b, symbol_s, symbols = -13.2, .125, 8., 3040
    cn0 = vlf_snr_db + db10(vlf_b)
    print(f'8.822kHz operator report: at {vlf_b:g}Hz, SNR {vlf_snr_db:+.2f}dB -> C/N0 {cn0:+.2f}dB-Hz; '
          f'equal-power flat-PSD at 225Hz -> {cn0-db10(225):+.2f}dB; '
          f'150 bits/{symbols*symbol_s/3600:.4f}h -> {150*3600/(symbols*symbol_s):.2f}bit/h')
    print()


def outage_identifiability():
    normal = NormalDist()
    fa = .01
    z = normal.inv_cdf(1-fa)
    print('optimistic known signal/phase and iid proper complex Gaussian noise, alpha=.01')
    for rho in (0., .001, .1, 1., 5., 10.):
        # rho=sum |s|^2 / sigma_c^2; Re<s,n> has variance sigma_c^2 ||s||^2/2
        det = 1-normal.cdf(z-sqrt(2*rho))
        print(f'whole-observation residual E/N0={rho:5g}: optimal P(data|link on)={det:.6f}; miss={1-det:.6f}')
    print('zero residual, valid noise-only: exactly P(data|true quiet), so DATA/quiet distinction needs extra observations.')
    print('independent erasure masks may inform observation validity; propagation-truth masks are oracle leakage.')


def polarization_observability():
    print('hypothetical calibrated dual receive projection, correlated equal noise variance (known phasing)')
    s=1/sqrt(2)
    for c in (0.,.5,.9):
        for delta in (0.,pi/2,pi):
            h0,h1 = s, s*exp(1j*delta)
            # R=[[1,c],[c,1]]. Give the DIRECTIONAL result, not only effective
            # channel-power trace. A fixed sum loses all opposite-signed signal.
            opt=(abs(h0)**2+abs(h1)**2-2*c*(h0.conjugate()*h1).real)/(1-c*c)
            summing=abs(h0+h1)**2/(2*(1+c))
            use_one=abs(h0)**2
            assert opt+1e-14>=summing and opt+1e-14>=use_one
            print(f'noise rho={c:.1f}, signal relative phase {degrees(delta):3.0f}deg: '
                  f'one port {use_one:.3f}, uncalibrated equal sum {summing:.3f}, ideal whitened combiner {opt:.3f}')
    print('These are SNR in units of single-port signal norm/noise variance; capabilities require both sampled ports.')


if __name__ == '__main__':
    assert DEFAULT_B == 225 and DEFAULT_DELTA == 75
    for fn in (antenna, two_components, group_phase, moon, referenced_noise, outage_identifiability):
        fn()
    print()
    polarization_observability()
