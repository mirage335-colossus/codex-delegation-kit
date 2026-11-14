"""Independent analytic references. Run with python3 desk.py."""
from math import cos, exp, log10, pi, sqrt

c = 299792458.0
eps0 = 8.8541878128e-12
k = 1.380649e-23
fs = 12000.0

def db(power_ratio):
    return 10 * log10(power_ratio)

print("Illustrative analytic references; no source build, field prediction, or qualification.")
frequency = 8000.0
wavelength = c / frequency
height, loss_r, loop_area = 10.0, 10.0, 100.0
monopole_r = 40*pi*pi*(height/wavelength)**2
loop_r = 320*pi**4*(loop_area/wavelength**2)**2
print("8 kHz ideal triangular-current monopole and single-turn loop Rr (ohm), monopole efficiency with 10 ohm loss (dB):",
      monopole_r, loop_r, db(monopole_r/(monopole_r+loss_r)))

print("Electrical ground conductivity to displacement ratio sigma/(2*pi*f*eps0), at 1/30 MHz:")
for frequency in [1e6, 30e6]:
    print(frequency, [(sigma, sigma/(2*pi*frequency*eps0)) for sigma in [.005, 5.]])

print("Gain mismatch of equal-power uncorrelated symmetric-delay rays, projected at center, as mean squared fraction of summed ray power:")
for delay in [.0001, .007, .01159]:
    for edge in [10, 100, 500]:
        phase = pi*edge*delay
        print(delay, edge, 2*(1-cos(phase)), phase**2)

print("Gaussian ray B=2sigma numerical comparison (2x midpoint quadrature), T=16 s. Pair: Gaussian coherence retained, OU with same 1/e lag:")
duration, steps = 16.0, 200000
interval = duration / steps

def matched_energy_fraction(covariance):
    return sum(2*(duration-(index+.5)*interval)*covariance((index+.5)*interval)*interval/duration**2
               for index in range(steps))

for width in [.1, .5, 1, 10, 30]:
    lag = sqrt(2)/(pi*width)
    gauss = matched_energy_fraction(lambda time: exp(-.5*(pi*width*time)**2))
    ou = matched_energy_fraction(lambda time: exp(-time*pi*width/sqrt(2)))
    print(width, lag, gauss, ou)

print("0.1 ppm residual in Hz at 8 kHz, 1, 30 and 5800 MHz:", [f*1e-7 for f in [8e3, 1e6, 3e7, 5.8e9]])
frequency = 5.8e9
wavelength = c/frequency
radius, distance = 1_737_400., 384_400_000.
dish_gain = .55*(pi*3/wavelength)**2
cross_section = .07*pi*radius**2
received_w = 1000*dish_gain*dish_gain*wavelength*wavelength*cross_section/((4*pi)**3*distance**4)
print("EME conditional receiver reference: delay center round trip, excess diameter front surface, dish gain dBi, received dBm, C/N0 dB-Hz, residual Hz per m/s total route rate")
print(2*distance/c, 2*radius/c, db(dish_gain), db(received_w)+30,
      [db(received_w/(k*temperature)) for temperature in [35, 150]], frequency/c)

cn0 = 32.
variance = fs/(10**(cn0/10))
print("Nominal unit-mean useful signal power received at synthetic 32 dB-Hz, 12 kHz complex sampling, sample complex noise variance and per-axis sigma:",
      variance, sqrt(variance/2))
print("If TX gain is reduced 6 dB and receiver N0 unchanged, realized C/N0 (dB-Hz):",
      db(fs*10**(-6/10)/variance))
print("If a 1000-Hz blocker exceeds a 100 Hz modeled half-band by 20 dB at the physical first stage, a downstream brickwall may remove it but cannot identify an earlier clip.")

# A bounded deterministic contrast: weak survivor + preselector blocker.
# An early clip can erase a weak input contribution before a later ideal LPF.
# Both blockers are exact DFT-bin sinusoids so an ideal 100-Hz LPF projects them out.
from math import sin, expm1, log
sample_rate, count = 12000, 12000
wanted_frequency, blocker_frequency = 37, 1000
wanted_peak = .08
wanted = [sin(2*pi*wanted_frequency*i/sample_rate) for i in range(count)]
blocker = [sin(2*pi*blocker_frequency*i/sample_rate) for i in range(count)]
for blocker_peak in [.5, 1.5, 3.0]:
    first_stage = [wanted_peak*w + blocker_peak*b for w, b in zip(wanted, blocker)]
    clipped = [min(1., max(-1., sample)) for sample in first_stage]
    clip_count = sum(abs(sample) > 1 for sample in first_stage)
    dot_clipped = 2/count * sum(w*x for w, x in zip(wanted, clipped))
    print('First-stage hard clip before ideal LPF, one second. Blocker peak, clips, wanted-tone recovered peak, amplitude delta dB:',
          blocker_peak, clip_count, dot_clipped, 20*log10(dot_clipped/wanted_peak))
print('Independent Bernoulli episodes with zero events: exact one-sided 95% upper bounds for n=30,300,3000:',
      [-expm1(log(.05)/n) for n in [30, 300, 3000]])
