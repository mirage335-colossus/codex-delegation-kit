# C6 executable-falsifier review

Scope: C6 packet only; no execution or other artifacts inspected.

1. **Unbound `sources` may stop the wrapper before any measurement.** The shown `evidence` initializer reads `input_artifacts=sources`, but the packet’s wrapper excerpt contains no assignment to `sources`. If it is not guaranteed by the enclosing runner, this raises `NameError` before fixture preparation and yields no fit or holdout. Cheapest check: statically confirm the binding in the actual wrapper, or add a zero-cost `assert 'sources' in locals()` immediately before constructing `evidence`. Treat a missing binding as setup failure; do not interpret it as a fit result.

2. **The exact-input preflight establishes historical equality, but not freshness of the planned receiver work.** The byte and validity hashes are compared with the remote GPU row and old holdout, which is a useful matched-input check. The fit uses `public_work_coordinates(receiver, coordinates)` after acquisition; the packet checks only that the acquired coordinates equal the remote row. Cheapest pre-measurement check: verify the receiver’s public work coordinates against the same canonical coordinates used by the remote row before calling `measure_fine_stratum`. If that relation is not exposed by the API, record it as unverified rather than treating the acquisition-coordinate equality as proof. Preserve the single fresh holdout after sealing.

3. **CPU execution conditions are recorded but not gated.** `before` and `operating_conditions_before_holdout` are captured, while the fit is accepted based on its trial count and downstream prediction guards. A thread-pool or CPU-budget change could therefore contaminate the fit without invalidating the sealed prediction. Cheapest check: before fit, assert the effective numerical-thread configuration and available CPU count still match the intended 12-worker setup; compare the post-fit conditions with `before` and mark the fit unusable on a material change. Keep 12 workers and the existing thresholds fixed.

These are hypotheses from the supplied wrapper and validator excerpt; no runtime behavior was observed.
