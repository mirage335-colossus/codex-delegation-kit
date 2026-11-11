Changed aggregation so normal mode computes `q*q` in float while keeping double bucket accumulation; audit mode remains double precision.

Public checks pass. Full `4096×2048` comparisons against audit pass for seeds 13 and 91: maximum sample delta `9.334e-8`, mean-square error per reading at most `5.492e-9`, and identical threshold counts. Three production runs took `0.062518–0.063945 s`. Ready for re-review.
