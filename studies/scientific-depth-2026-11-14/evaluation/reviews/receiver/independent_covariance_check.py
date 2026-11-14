#!/usr/bin/env python3
"""Independent exact check of the receiver chapter's 3-carrier covariance and scan arithmetic."""
import cmath, math
centers = (-75.0, 0.0, 75.0)
tau = 0.007
R = [[0.5 * (1.0 + cmath.exp(-2j * math.pi * (f-g) * tau)) for g in centers] for f in centers]
def det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
          - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
          + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))
print('independent exact check; equal per-carrier power; shared two-tap vs independent flat gain')
print('rho_adjacent=',abs(R[0][1]))
print('rho_outer=',abs(R[0][2]))
for snr in (1.0, 10.0):
    P=[[snr*R[i][j] + (1.0 if i == j else 0.0) for j in range(3)] for i in range(3)]
    # Q=(1+snr)I; trace(Q^-1 P)=3 exactly, so KL is log(det(Q)/det(P)).
    kl=math.log((1.0+snr)**3/det3(P).real)
    print(f'SNR={snr:g} linear; KL(CN(0,P)||CN(0,(1+SNR)I))={kl:.9f} nats')
M=1000; p=1e-4; alpha=1e-3
print(f'independent Exp(1) tests: familywise P_FA={1-(1-p)**M:.9f}')
print(f'familywise alpha={alpha:g}; exact exponential-score threshold={-math.log(1-(1-alpha)**(1/M)):.9f}')
print(f'Bonferroni threshold={math.log(M/alpha):.9f}')
print('Limits: conditioned common shift; one 3-complex-sample covariance identification, not modem bit-error or natural channel prevalence; independent tests are an illustrative null, not the actual correlated receiver scan.')
