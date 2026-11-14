"""Analytical equal-power noise counterexample; not a measured radio trace."""
from math import exp, log1p

mean_power = 1.0
threshold = 4.0
burst_probability = 0.01
burst_amplitude = (mean_power / burst_probability) ** 0.5
# Circular complex Gaussian CN(0, mean_power): |n| has Rayleigh tail.
p_gauss = exp(-(threshold**2) / mean_power)
# Sparse random-phase impulse mixture with identical E|n|^2.
p_burst = burst_probability if burst_amplitude >= threshold else 0.0
N = 10_000
at_least_one_gauss = -__import__('math').expm1(N * log1p(-p_gauss))
at_least_one_burst = -__import__('math').expm1(N * log1p(-p_burst))
print(f"shared mean sample power E|n|^2={mean_power:.1f}; threshold |n|>={threshold:g}")
print(f"Gaussian CN(0,1) exceedance/sample={p_gauss:.12g}")
print(f"impulse mixture p={burst_probability:.3%}, amplitude={burst_amplitude:.1f}, mean power={burst_probability*burst_amplitude**2:.1f}, exceedance/sample={p_burst:.6%}")
print(f"single-sample exceedance ratio={p_burst/p_gauss:.1f}x")
print(f"N={N}: P(any exceed) Gaussian={at_least_one_gauss:.6%}; impulse mixture={at_least_one_burst:.6%}")
