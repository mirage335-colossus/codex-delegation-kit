**changes_required**

One local precision change remains: [core.cpp:12](/tmp/precision-generalization-workflows/w22/core.cpp:12) scales generated samples in FP64 before default-mode conversion to float at lines 51–52. Assembly confirms these double multiplications and conversions execute.

A scratch-only FP32 scaling variant satisfies the practical contract:

- Two 500,000-frame captures passed; worst error `1.913e-7` against `2e-6`.
- Audit output remained exact against the supplied reference.
- Boundary cases, maximum unsigned seed, invalid overrides, and resident-memory checks passed.
- Twenty-three alternating timing observations showed no consistent wider-path benefit; the two batches reversed their ordering.

Under the supplied guidance’s preference for narrower arithmetic when qualified choices tie, use float scaling for default mode while preserving double scaling for audit. No speedup is established.

The submitted implementation otherwise passes independently: exact integer timeline/count, complete channel output, audit behavior, and full-capture RSS (`3,776 KiB`). The original cumulative-phase problem is removed. All nine public checks passed.

Diagnostics and results are retained only in `review-scratch/`; production files were unchanged. Re-review needs the local repair and affected quality/resource checks. Used eight execution calls.

Separate provenance issue: supplied owner history records an earlier repository-wide listing/search outside this workspace, beyond the disclosed failed Git command. I followed none of those paths.
