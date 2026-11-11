**accepted**

The repair resolves the original finding: normal-mode `q*q` now executes in float before conversion to double; bucket accumulation and audit arithmetic remain double. Threshold comparisons and exact counts are preserved.

Independent checks passed:

- Supplied public smoke, boundary, and audit checks.
- Production scans for seeds 13 and 91, maximum dimensions for seed 7, and `1×1`.
- Maximum observed mean-square error: `5.492e-9` per reading; threshold counts matched.
- Three default end-to-end runs: `0.075837`, `0.070577`, and `0.071099 s`, below `0.12 s`.
- Storage accounting matched output plus lookup-table allocations.

Evidence: `review-scratch/round2/verification.json`. Production source remained unchanged during review. Full-size comparisons used the preserved audit path; independent Python reference coverage remains the supplied public checks. No required acceptance checks remain open.
