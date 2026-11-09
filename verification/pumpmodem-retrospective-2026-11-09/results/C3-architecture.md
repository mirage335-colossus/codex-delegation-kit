# C3 architecture review

Revision: `28f08825670b76472628b50d98cd648a87aa62e4` (per packet). Review uses only the supplied excerpts; no runtime behavior is observed.

## Concerns

1. **Score parity can be true for differently shaped arrays.** At `tools/triad_gpu_workload.py:167-169`, `np.allclose` permits NumPy broadcasting; equal lane names do not establish equal array shapes or elementwise correspondence. If shapes are broadcast-compatible, `scores_match` could be true even though the lane score outputs have different structure. Predicted outcome: a mismatched-shape pair can pass the score boolean (subject to values meeting tolerance). Cheapest decisive check: call `compare_work` with one lane array shaped `(n, 1)` and the other `(n, m)` with repeated matching values. If it passes, require exact shape equality before `allclose`; keep tolerance for same-shaped values. This is an unverified hypothesis about reachable record shapes, not an observed defect.

2. **The final status can pass vacuously if parity checks are absent.** At `tools/triad_gpu_workload.py:274-276`, `all(...)` is true for an empty set of checks. Thus a CUDA report with positive peak allocation and no cases, or cases whose parity maps contain no checks, can be labeled `short_fine_work_parity_observed`. The excerpt does not show whether upstream validation rules out either input. Cheapest decisive check: inspect the smallest accepted case-list path and confirm that zero cases / empty parity maps are rejected before this status branch. If they are accepted, require at least one case and one check per expected stratum before reporting parity. This is a conditional risk, not evidence that an empty report occurred.

3. **The status cannot establish timing-comparison readiness.** At `tools/triad_gpu_workload.py:270-276`, status depends on source stability, row errors, CUDA allocation and parity booleans; it does not gate on timing samples, synchronization, or matched timing inputs. Meanwhile `_case_probe` at `:177-198` acquires coordinates on CPU and then samples named fine-work strata on each device. Accordingly, the status supports the narrow claim in its name (fine-work parity observed), not the user's full receiver-throughput comparison contract, which includes acquisition and recurring setup/quiet-slot work. Cheapest decisive check: compare the timing acceptance caller's required fields and strata against this status predicate. If it treats this status as timing acceptance, require valid matched timing evidence and complete-work coverage there; otherwise keep the status explicitly parity-only. The excerpt does not establish that the caller overclaims.

## Choice to preserve

Keep work equality, score closeness, and timing as separate concepts (`compare_work` docstring at `:163`) and retain the explicit `short_fine_work_parity_observed` status wording (`:276`). This makes the scope limitation legible and avoids presenting parity itself as a speed result.
