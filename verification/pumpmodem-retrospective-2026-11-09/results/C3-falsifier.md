# C3 falsifier review

## Concern: empty case reports can pass the CUDA acceptance predicate

**Mechanism (conditional defect):** At lines 274–276, both `all(...)` calls are vacuously true when `report['cases']` is empty. With stable sources and `cuda_peak_allocated_bytes > 0`, the final status becomes `short_fine_work_parity_observed` despite there being no compared case or parity check. The excerpt does not establish whether an earlier guard guarantees a nonempty case list, so treat this as an unverified implementation risk, not evidence that a production run was misreported.

**Cheapest decisive check:** Evaluate the exact status predicate with `stable=True`, positive CUDA peak allocation, and `cases=[]`. It predicts the parity status. Then check the acceptance caller's case-list precondition; if none exists, add a nonempty-case requirement (and a regression for this fixture) before allowing that status.

## Choice worth preserving

`compare_work` reports `work_match` and `scores_match` separately (lines 163–169), and the final label is explicitly limited to `short_fine_work_parity_observed` (line 276). Preserve that separation and narrow claim: parity alone should not be presented as complete-receiver throughput qualification.
