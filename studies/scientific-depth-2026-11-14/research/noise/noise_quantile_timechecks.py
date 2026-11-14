#!/usr/bin/env python3
"""Conditional demonstration: percentile aggregation and time order matter.
Uses standard-library Monte Carlo; no product or hidden data.
"""
import math, random
from statistics import NormalDist

seed, n, sigma_db = 372, 600_000, 9.0
rng = random.Random(seed)
# Two component noise factors with identical lognormal marginals, median 1 (=0 dB)
# and Gaussian dB standard deviation 9 dB. A 90th-deviation is 11.53 dB.
a = [10 ** (rng.gauss(0.0, sigma_db) / 10.0) for _ in range(n)]
b = [10 ** (rng.gauss(0.0, sigma_db) / 10.0) for _ in range(n)]
independent_sum = sorted(x + y for x, y in zip(a, b))
q50 = independent_sum[int(0.5*n)]
q90 = independent_sum[int(0.9*n)]
z90 = NormalDist().inv_cdf(0.9)
component_q90 = 10 ** (z90 * sigma_db / 10.0)
naive_component_q90_sum = 2 * component_q90
perfectly_correlated_q90 = 2 * component_q90

# P.372-15 moment-matched lognormal sum (this version's retrieved alpha uses +sigma²/2).
c = 10 / math.log(10)
sigma_nat = sigma_db * math.log(10) / 10
mean_one = math.exp(sigma_nat**2 / 2)
var_one = mean_one**2 * (math.exp(sigma_nat**2) - 1)
alpha = 2 * mean_one
beta = 2 * var_one
sigma_total = c * math.sqrt(math.log(1 + beta / alpha**2))
median_total_db = c * (math.log(alpha) - sigma_total**2/(2*c**2))
fw_q90_db = median_total_db + z90 * sigma_total

print('INDEPENDENT LOGNORMAL POWER SOURCES (conditional, dB relative to one component median)')
print(f'seed={seed}, n={n}, each median=0dB, dB sigma={sigma_db:g}, individual D90={z90*sigma_db:.3f}dB')
print(f'linear sum then empirical quantiles: median={10*math.log10(q50):.3f}dB, Q90={10*math.log10(q90):.3f}dB')
print(f'naive sum of individual Q90 watts: {10*math.log10(naive_component_q90_sum):.3f}dB')
print(f'P.372-15 moment-matched lognormal sum: median={median_total_db:.3f}dB, D90={fw_q90_db-median_total_db:.3f}dB, Q90={fw_q90_db:.3f}dB')
print(f'perfect common dB fluctuation, same marginals: total Q90={10*math.log10(perfectly_correlated_q90):.3f}dB')
# Literal substitution of the minus sign in the cached P.372-17 equation (21)
# text into equations (18)-(19), for one source, exposes an identity problem.
sigma_v17_text = c * math.sqrt(math.log(1 + (math.exp(-sigma_nat**2/2)**2 * (math.exp(sigma_nat**2)-1)) / math.exp(-sigma_nat**2)))
alpha_v17_text = math.exp(-sigma_nat**2/2)
median_v17_literal = c * (math.log(alpha_v17_text) - sigma_v17_text**2/(2*c*c))
print(f'cached P.372-17 alpha minus-sign literal, one input median=0dB sigma=9dB -> {median_v17_literal:.3f}dB (non-identity; do not use without visual/source resolution)')
print('The simulation sums component power variables as an equivalent-power model; physical voltages have instantaneous cross terms. Power/PSD sums hold in expectation or in an averaged bin/window when cross-spectral terms average to zero. Summing separate quantiles is not the quantile of a sum unless dependence structure happens to make it so.')

print('\nP.372-17 VS NETHERLANDS GRAPH-READ COMPARISON (predecessor median curves, 2700Hz)')
for f, measured in ((1.8, {'city':27.0, 'residential':18.0}), (30.0, {'city':7.0, 'residential':-2.0})):
    print(f'{f:g} MHz:')
    for name, (c0,d0) in {'city':(76.8,27.7), 'residential':(72.5,27.7)}.items():
        fa = c0 - d0*math.log10(f)
        predicted = fa + 20*math.log10(f) + 10*math.log10(2700) - 95.5
        print(f'  {name}: P.372-17 short lossless monopole predicted {predicted:.2f}dBµV/m; Fockens Fig.3 approximate {measured[name]:.1f}; graph difference {measured[name]-predicted:+.2f}dB')
print('Approximate graph read, not a matched-antenna/statistically paired difference; Fockens uses calibrated tuned loops and reports population/site averages.')

print('\nSAME APD / DIFFERENT EVENT CHRONOLOGY (bounded synthetic data-equivalent)')
slots, samples_per_slot, occupancy = 1000, 1600, 0.01
N = slots * samples_per_slot
events = round(N * occupancy)
# Process A spreads events evenly: same amplitude/sample histogram, every slot has 16 events.
events_per_slot_a = events // slots
# Process B groups the exact same count into 10 fully occupied slots.
clustered_slots = math.ceil(events / samples_per_slot)
mean_events = events / slots
var_b = (clustered_slots/slots)*(1-clustered_slots/slots)*samples_per_slot**2
print(f'{slots} windows x {samples_per_slot} samples/window; total event fraction={events/N:.3%}; APD histogram exactly same (event amplitude and zero otherwise)')
print(f'distributed chronology: {events_per_slot_a} event samples/window; {slots}/{slots} windows contain events')
print(f'clustered chronology: {clustered_slots} full-event windows, {slots-clustered_slots} empty; {clustered_slots/slots:.1%} windows contain events')
print(f'both have mean {mean_events:.1f} event samples/window; clustered count SD/window={math.sqrt(var_b):.1f}')
print('This exposes conditional outage clustering only; no signal, decoder or slot-loss probability is modeled.')
