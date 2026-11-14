#!/usr/bin/env python3
"""Small analytic receiver-model discriminators; no modem or pump code."""
import cmath
import math
import random


def det3(a):
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def inv3(a):
    d = det3(a)
    cof = [
        [a[1][1] * a[2][2] - a[1][2] * a[2][1], a[0][2] * a[2][1] - a[0][1] * a[2][2], a[0][1] * a[1][2] - a[0][2] * a[1][1]],
        [a[1][2] * a[2][0] - a[1][0] * a[2][2], a[0][0] * a[2][2] - a[0][2] * a[2][0], a[0][2] * a[1][0] - a[0][0] * a[1][2]],
        [a[1][0] * a[2][1] - a[1][1] * a[2][0], a[0][1] * a[2][0] - a[0][0] * a[2][1], a[0][0] * a[1][1] - a[0][1] * a[1][0]],
    ]
    return [[v / d for v in row] for row in cof]


def trace_product(a, b):
    return sum(sum(a[i][j] * b[j][i] for j in range(3)) for i in range(3))


def kl_complex_gaussian(cov_p, cov_q):
    # D(CN(0,P) || CN(0,Q)) for proper complex Gaussian vectors.
    n = 3
    ratio = det3(cov_q).real / det3(cov_p).real
    return (trace_product(inv3(cov_q), cov_p).real - n + math.log(ratio))


def add_scaled_identity(matrix, scalar):
    return [[matrix[i][j] + (scalar if i == j else 0.0) for j in range(3)] for i in range(3)]


def cholesky3(a):
    l = [[0j for _ in range(3)] for _ in range(3)]
    l[0][0] = math.sqrt(a[0][0].real)
    l[1][0] = a[1][0] / l[0][0]
    l[2][0] = a[2][0] / l[0][0]
    l[1][1] = math.sqrt((a[1][1] - abs(l[1][0]) ** 2).real)
    l[2][1] = (a[2][1] - l[2][0] * l[1][0].conjugate()) / l[1][1]
    l[2][2] = math.sqrt((a[2][2] - abs(l[2][0]) ** 2 - abs(l[2][1]) ** 2).real)
    return l


def draw_cn(rng, lower):
    z = [(rng.gauss(0.0, 1.0) + 1j * rng.gauss(0.0, 1.0)) / math.sqrt(2.0) for _ in range(3)]
    return [sum(lower[i][j] * z[j] for j in range(i + 1)) for i in range(3)]


def solve_lower(lower, y):
    x = [0j, 0j, 0j]
    for i in range(3):
        x[i] = (y[i] - sum(lower[i][j] * x[j] for j in range(i))) / lower[i][i]
    return x


def log_likelihood(y, covariance):
    lower = cholesky3(covariance)
    whitened = solve_lower(lower, y)
    logdet = 2.0 * sum(math.log(lower[i][i].real) for i in range(3))
    return -logdet - sum(abs(x) ** 2 for x in whitened)


def equal_prior_bayes_error(cov_path, cov_ind, rng, samples_per_model=25000):
    lower_path = cholesky3(cov_path)
    lower_ind = cholesky3(cov_ind)
    errors = 0
    for truth, lower_truth in ((0, lower_path), (1, lower_ind)):
        for _ in range(samples_per_model):
            y = draw_cn(rng, lower_truth)
            ll_path = log_likelihood(y, cov_path)
            ll_ind = log_likelihood(y, cov_ind)
            chosen = 0 if ll_path >= ll_ind else 1
            errors += chosen != truth
    p = errors / (2.0 * samples_per_model)
    se = math.sqrt(p * (1.0 - p) / (2.0 * samples_per_model))
    return p, se


def main():
    centers_hz = [-75.0, 0.0, 75.0]
    tap_power = 0.5  # two independent, equal-power complex path gains
    channel_power_per_carrier = 1.0
    print("CASE: matched common residual-frequency trajectory; 3 carrier centers [-75, 0, 75] Hz; occupied width 225 Hz")
    print("H_path: two shared complex path gains, delays [0, tau], each power 0.5; H_ind: independent flat complex gain per carrier, variance 1")
    print("Both hypotheses have equal per-carrier average signal power and the same circular complex AWGN variance; the common trajectory is conditioned out identically.")
    print("Bayes model priors are equal (1/2 each); KL is expected model-evidence separation, Bayes error is a finite one-triplet discrimination simulation, not bit decoding.")
    print("tau_ms,delay_rms_ms,adjacent_corr_mag,outer_corr_mag,within_37p5Hz_corr_mag,within_edge_complex_mse_over_P,KL_path_to_ind_SNR0_nats,KL_path_to_ind_SNR10_nats,Bayes_model_error_SNR0,MC_SE,Bayes_model_error_SNR10,MC_SE")
    rng = random.Random(20261114)
    for tau_ms in (0.8, 2.0, 7.0, 8.0):
        tau = tau_ms / 1000.0
        r = []
        for f_k in centers_hz:
            row = []
            for f_l in centers_hz:
                delta = f_k - f_l
                row.append(tap_power * (1.0 + cmath.exp(-2j * math.pi * delta * tau)))
            r.append(row)
        adj = abs(r[0][1])
        outer = abs(r[0][2])
        inband = abs(0.5 * (1.0 + cmath.exp(-2j * math.pi * 37.5 * tau)))
        inband_mse = 2.0 * math.sin(math.pi * 37.5 * tau) ** 2
        snr_results = []
        for snr in (1.0, 10.0):
            # P=1, N0=1/SNR. Divide both covariances by N0: Q is isotropic.
            p_cov = add_scaled_identity([[snr * x for x in row] for row in r], 1.0)
            q_cov = add_scaled_identity([[0.0 for _ in range(len(centers_hz))] for _ in range(len(centers_hz))], 1.0 + snr)
            snr_results.append((
                kl_complex_gaussian(p_cov, q_cov),
                equal_prior_bayes_error(p_cov, q_cov, rng),
            ))
        print(f"{tau_ms:.1f},{tau_ms/2:.1f},{adj:.6f},{outer:.6f},{inband:.6f},{inband_mse:.6f},{snr_results[0][0]:.6f},{snr_results[1][0]:.6f},{snr_results[0][1][0]:.6f},{snr_results[0][1][1]:.6f},{snr_results[1][1][0]:.6f},{snr_results[1][1][1]:.6f}")
    print("NOTE: two-ray toy only; tau is path separation, RMS delay is tau/2. These are not empirical delay distributions or guaranteed disambiguation with one observation.")

    m = 1000
    p_one = 1e-4
    alpha = 1e-3
    familywise = 1.0 - (1.0 - p_one) ** m
    gamma_exact = -math.log(1.0 - (1.0 - alpha) ** (1.0 / m))
    gamma_bonferroni = -math.log(alpha / m)
    print("\nCASE: illustrative event-level false-completion accounting under independent complex-Gaussian normalized correlator tests")
    print(f"M={m}, per_test_Pfa={p_one:g} => familywise_Pfa={familywise:.8f}")
    print(f"For familywise_alpha={alpha:g}: exact_threshold_energy={gamma_exact:.6f}, Bonferroni_threshold_energy={gamma_bonferroni:.6f} (Exp(1) null score)")
    print("NOTE: receiver hypotheses/windows are correlated in practice; calibrate actual event-level false completions on null/noise streams, including repeated windows and final framing checks.")


if __name__ == "__main__":
    main()
