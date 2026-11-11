**changes_required**

1. **Incorrect resource report — `core.cpp:93`.** `storage_bytes` omits `horizontal` and `horizontal_squares`, both still live. Production reports **14,745,600 bytes**, while live vector payload totals **24,576,000 bytes**. Include both capacities.

2. **Wider normal-mode arithmetic lacks practical justification — `core.cpp:55–81`.** Horizontal `q` is double, so products and compound additions/subtractions execute in double before rounding to float. Final division, variance, square root and score calculation also use double. The owner’s comparison did not qualify narrower arithmetic for these operations.

   A scratch-only variant makes those operations float while preserving double score storage, reporting aggregates and unchanged audit. It passes the public checks and every additional case tested. Across nine alternating production runs, median end-to-end time was **0.06265 s**, versus **0.06907 s** currently. Production errors against audit were at most **9.53e-5** at samples, **1.33e-5** in normalized aggregates, and **zero** threshold-count differences. Adopt qualified narrower operations or establish a concrete benefit for retained wider work.

Independent validation:
- Both implementations passed all four public boundary cases and strict audit checks.
- Production cases with seeds 11 and 91 passed numerical limits; measured normal runs met 0.20 seconds.
- Maximum-width/height one-dimensional cases, radius 127, a clipped `4096×33` case, and production radius zero passed.
- Source tracing confirms all pixels contribute. Vertical accumulation is float; audit and reporting arithmetic remain double; threshold counts remain exactly representable.

Diagnostic sources and results are retained under `review-scratch/`. Production source was unchanged. Timing is a bounded local comparison, not exhaustive hardware qualification; the entire accepted CLI domain was not enumerated. The owner’s earlier accidental audit narrowing failed and was repaired before this review.

Used **10 shell-tool invocations** within the assigned budget. Re-review should check corrected resource accounting and the owner’s chosen arithmetic repair against these same contracts.
