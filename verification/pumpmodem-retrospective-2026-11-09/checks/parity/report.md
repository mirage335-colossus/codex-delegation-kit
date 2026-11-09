# Baseline 28 parity diagnostic

**Outcome:** `behavior_reproduced; caller rejects mismatch`. This is expected comparator behavior, covered by the baseline test, and is not a reproduced defect. Empty-case acceptance is unreachable through the public caller. Shape broadcasting is observed for synthetic records, but the real record constructor validates score shape.

## Identity and setup

- Source: `/tmp/pump-review-baseline28/tools/triad_gpu_workload.py`, SHA-256 `ed2d5c67fe345ee7a9f0c8c6f004f4e2e00c892510eb8dcbd6074947b77d8e21`.
- Test source: `/tmp/pump-review-baseline28/tests/test_triad_gpu_workload.py`, SHA-256 `a5d8f19c9575dc7da7855e7099977338935fac5fc133ec41700720036ce837d5`.
- Python: `/tmp/pumpmodem-cleanup-venv/bin/python`; NumPy available. No GPU or full receiver campaign used.
- Runner: `/tmp/pumpmodem-cleanup-venv/bin/python /tmp/pump-review-parity/check.py`; exit 0. Exact wrapper is preserved at `check.py`; exact stdout JSON is preserved at `stdout.json`. It AST-extracts the actual `compare_work` function and executes it with NumPy and constants `SCORE_RTOL=1e-7`, `SCORE_ATOL=1e-9`; heavy module imports avoided. No check was rerun for this persistence update.
- Source reconstruction recipe (from a source checkout containing the `baseline28` ref; extracts only the needed tool, not docs/campaign): `git -C /path/to/source-repo archive baseline28 tools/triad_gpu_workload.py | tar -x -C /tmp/pump-review-parity/reconstructed`; then compare `sha256sum /tmp/pump-review-parity/reconstructed/tools/triad_gpu_workload.py` with the source hash above. The supplied `/tmp/pump-review-baseline28` copy was not itself a Git checkout, so this recipe was not run here.

## Checks (4)

1. **Reachable comparator case:** same lane score arrays, different `work` dicts -> `{'work_match': false, 'scores_match': true}`. The caller writes this parity result but final status requires `all(check.values())` for every parity check, so this case cannot satisfy `short_fine_work_parity_observed`. The baseline test `test_close_scores_require_identical_work` asserts this exact expected behavior. A later temporary target that changed this test to expect `false/false` would conflict with the frozen baseline behavior; no claim is made about the historical compile error.
2. **Synthetic empty comparator input:** `compare_work([], [])` -> both false, not acceptance. Public `run_probe` requires `1 <= len(selected) <= 3` at lines 212-214 before entering the case loop, so empty records cannot arise from an accepted zero-case run. No evidence supports the claim that an empty-case vacuous `all()` can yield acceptance here.
3. **Synthetic shape case:** score shapes `(1,2)` and `(2,)` with values equal -> both match true because `np.allclose` broadcasts. Actual comparator behavior reproduced. `_complete_record` validates real scores are `(2,)` finite vectors (lines 64-67), so production-generated lane-score shape mismatch appears precluded at record creation; this is not a demonstrated end-to-end acceptance defect.
4. **Caller acceptance topology:** static read of `run_probe` and the status branch confirms 1..3 selected rows, GPU peak allocation >0, and every parity dict value true are needed for parity status. No full caller campaign executed.

## Exact evidence locations

- Comparator and score validation: `tools/triad_gpu_workload.py:64-68,162-169`.
- Selection guard: `tools/triad_gpu_workload.py:212-214`.
- Final parity status gate: `tools/triad_gpu_workload.py:276-282`.
- Existing tests: `tests/test_triad_gpu_workload.py:17-31`.
- Reproducible output: `/tmp/pump-review-parity/check.py` (rerun command above).

## Limits and next discriminating question

This was a bounded diagnostic, not the original acceptance campaign; no historical compile error was exercised or inferred. The mismatch result is expected comparator output and correctly vetoes overall parity. To determine whether shape broadcasting matters beyond synthetic inputs, establish whether any supported production path can bypass `_complete_record`'s exact `(2,)` validation before records reach `compare_work`.
