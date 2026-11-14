#!/usr/bin/env python3
"""Independent calculations from publicly declared laws + inspected parameters.

No predicted receiver outcomes, pump build, or random generated link samples.
Exact finite autocovariance is calculated by summing FIR kernel products.
The fixed-grid covariance integrates over a shared random knot origin; reported
phase spread shows grid-position sensitivity hidden by the averaged covariance.
"""
from math import ceil, exp, floor, fsum, pi, sqrt


def kernel(radius, scale):
    h = [exp(-(k*scale)**2) for k in range(-radius, radius+1)]
    norm = sqrt(fsum(x*x for x in h))
    return tuple(x/norm for x in h)


def at_lag(h, lag):
    lag = abs(lag)
    return fsum(h[i]*h[i+lag] for i in range(len(h)-lag))


def full_covariances(h):
    return tuple(at_lag(h, lag) for lag in range(len(h)))


def basis(coordinate):
    # Same polynomial convention as the Catmull–Rom design; use friendly exact
    # grid fractions and independently evaluate the small dense Gram sum.
    i = floor(coordinate)
    u = coordinate-i
    u2, u3 = u*u, u*u*u
    cs = (-.5*u+u2-.5*u3, 1-2.5*u2+1.5*u3,
          .5*u+2*u2-1.5*u3, -.5*u2+.5*u3)
    return tuple(zip(range(i-1, i+3), cs))


def fixed_grid_cov(delta, origin, cov):
    a, b = basis(origin), basis(origin+delta)

    def gram(d, e):
        return fsum(x*y*cov[k] for i,x in d for j,y in e
                    for k in (abs(i-j),) if k < len(cov))

    return gram(a,b)/sqrt(gram(a,a)*gram(b,b))


def generator_comparison():
    print('Ideal Gaussian ACF R(d)=exp[-(pi*B*d)^2/2]; no receive/project measurement')
    fcov = full_covariances(kernel(26,pi/16))
    for z in (0.01, .03, .0625, .125, .25, .45, .5, .75, 1., 1.5, 2.):
        values = [fixed_grid_cov(16*z,(j+.5)/128,fcov) for j in range(128)]
        approx = fsum(values)/len(values)
        truth = exp(-.5*(pi*z)**2)
        print(f'B*lag={z:>6g} ideal={truth:.10f} fixed mean={approx:.10f} '
              f'error={approx-truth:+.3e} knot-phase span={max(values)-min(values):.3e}')
        if z==.5:
            assert abs(approx-truth)<1e-4
        assert abs(fixed_grid_cov(0,.37,fcov)-1)<1e-14
    print()
    print('Receive-clock FIR (4096 maximum radius) vs fixed-time 53 terms, physical-time presets:')
    for fs in (960, 12000):
        for width in (.1, .5, 1., 10., 30.):
            r = ceil(5*fs/(pi*width))
            taps = 2*r+1
            knot_hz = 16*width
            # Cache-based estimate of per-second real-kernel terms used to fill
            # new knot values active during ordered capture. Excludes startup,
            # more than one skipped knot, RNG, interp/Gram/sqrt, control and DSP.
            # The queried quartet overlaps for 16B < Fs with smooth stepping.
            assert knot_hz < fs
            fixed_real_terms = 4*53*knot_hz  # two rays, each Re+Im.
            if r>4096:
                direct = 'rejected by tap cap'
            else:
                h = kernel(r, pi*width/fs)
                sigerr = []
                for frac in (.0625, .125, .25, .45, .5, .75, 1., 1.5, 2.):
                    k=round(frac*fs/width)
                    truth=exp(-.5*(pi*width*k/fs)**2)
                    sigerr.append(abs(at_lag(h,k)-truth))
                direct = (f'max error {max(sigerr):.3e} vs ideal ACF at tested sampled lags; '
                          f'{4*fs*taps:,} real kernel terms/s for both rays')
            print(f'Fs={fs:5g} B={width:4g}: requested {taps:6,d} taps ({direct}); '
                  f'fixed grid {knot_hz:g}knots/s, ~{fixed_real_terms:,.0f} new-knot terms/s '
                  'plus per-sample interp and other work')
    print()


def marginal_dwell():
    print('Equal marginal process: two-state Markov latent availability at 1s step, p(outage)=.10 exactly')
    print('Conditional emission: same pair of proper Gaussian gain laws in both models, so all one-row level CDFs match.')
    p = .10
    for q in (.2,.9,.98):
        b = p*(1-q)/(1-p)  # Pr(on -> off)
        stationary = b/(1-q+b)
        assert abs(stationary-p)<1e-14
        print(f'P(off->off)={q:.2f}, P(on->off)={b:.8f}; off-run mean {1/(1-q):.3f}s; '
              f'Pr(stationary start then 16s all off)={p*q**15:.7g}; '
              f'Pr(episode length>=32s|new off)={q**31:.7g}')
    print('The difference is not sample-validity loss or a field probability. Paired block/episode validation must include durations and recovery.')


if __name__=='__main__':
    generator_comparison()
    marginal_dwell()
