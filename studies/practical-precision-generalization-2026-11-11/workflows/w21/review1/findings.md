**changes_required**

The implementation passes the product’s accuracy and deadline checks, but normal-mode aggregation at `core.cpp:55` promotes each float output to double before `q*q`. The retained wider product lacks a demonstrated practical benefit.

A scratch-only variant using `T q=output[i]` preserves double accumulation and audit arithmetic while computing normal-mode products in float. It passed public checks and production accuracy: mean-square error `5.48e-9` per reading, with identical threshold counts. Twelve alternating end-to-end runs were effectively tied: median `0.068504 s` versus submitted `0.067858 s`. Under the supplied guidance, prefer the qualified narrower product. The owner should make that scoped change and revalidate.

Double accumulation has concrete justification: naïve float accumulation failed production mean-square tolerance (`2.071e-4` versus `2e-5`). A blocked float diagnostic passed and improved throughput, but matched blocked-double timings show the improvement primarily comes from loop organization; this does not establish a precision-specific speedup.

Verified:

- Submitted public smoke, boundary, and audit checks passed.
- Production comparisons for seeds 13 and 91, maximum dimensions for seed 7, and `1×1` passed against the preserved audit path.
- Submitted production timings remained below `0.12 s`.
- Measurement generation and interpolation execute in float; calibration preparation and audit execute in double.
- Every reading contributes. Interpolation stays within table bounds. Threshold counters remain exact at supported sizes.
- Reported production storage correctly includes output and table: `33,816,580` bytes.

Evidence and temporary variants remain under `review-scratch/`. Production source was unchanged. Full-size comparisons used the preserved audit implementation; independent Python reference coverage comes from the supplied public checks. No universal performance claim is made from these noisy local timings.
