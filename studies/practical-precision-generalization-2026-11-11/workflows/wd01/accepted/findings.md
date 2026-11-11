**accepted**

Both original findings are resolved:

- Normal scoring arithmetic now executes in float, including horizontal products, accumulation, variance and `std::sqrt(float)`. Audit and reporting arithmetic remain unchanged.
- `storage_bytes` includes all four live vector capacities: **24,576,000 bytes** for production.

The repaired numerical implementation exactly matches the previously qualified diagnostic variant; remaining differences are its comment and corrected resource accounting.

Independent checks passed:

- Documented compiler flags and supplied public smoke, four boundary cases, and strict audit checks.
- Production: five end-to-end runs, **0.0522–0.0631 s**, median **0.0553 s**, below 0.20 seconds.
- Production errors versus audit: samples **9.53e-5**, bucket means **6.66e-6**, mean squares **1.33e-5**, threshold-count difference **0**.
- Maximum-width/height one-dimensional cases, clipped radius-127 case, and production radius zero passed numerical and storage assertions.

Results are preserved in `review-scratch/round2/verification-results.json`. No source edits. Four shell-tool invocations used. Qualification remains bounded to this CPU/build and tested inputs; the entire CLI domain was not enumerated.
