# Private preflight record

## Boundaries

Participant-safe tree: `/tmp/recovery-projection-transfer/participant/` (task, fixturedata, selected frozen source modules, and the existing incremental-receiver test). It contains no evaluator or oracle. Evaluator is `/tmp/recovery-projection-transfer/evaluator.py`; private oracle is `/tmp/recovery-projection-transfer/oracle.md`. `validation/baseline/` and `validation/witness/` are disposable private copies.

For an owner candidate tree, copy `participant/` to a disposable root, copy `evaluator.py` to that root, then run:

```sh
/tmp/pumpmodem-cleanup-venv/bin/python -B evaluator.py
```

Run the existing integration fixture from the candidate's `tests/` directory with the command in `task.md`.

## Identity and workload

The frozen source file SHA-256 is `c586d14fd50c63fa70143e295ff1992606d95ff788bac2cad43bbaa77e718183`; the copied participant source has the same hash. No production baseline files were edited. The public workload is explicitly a constructed deterministic contract slice using the actual frozen `BlockProjection` API, `samples=64`, `sample_rate_hz=64`, required interval `[0,0]`, and no exclusions. It is not a historical capture or throughput trace. The historical public multi-bin geometry that was briefly considered is retained only as audit material under `preflight/` and is not represented as this workload. Existing caller coverage uses the repository's unchanged incremental-receiver fixture.

## Checks

- Baseline private evaluator: `/tmp/pumpmodem-cleanup-venv/bin/python -B evaluator.py` from `validation/baseline/` — failed as intended after the equality/dtype/shape/stride/error checks; FFT counter found 8 `np.fft.fft` calls for the supplied DC geometry. Output: `preflight/baseline-evaluator-final.out`.
- Witness private evaluator: same invocation from `validation/witness/` — passed exact contract checks and observed zero FFT calls. Output: `preflight/witness-evaluator-final.out`.
- Baseline integration: from `participant/tests/`, `/tmp/pumpmodem-cleanup-venv/bin/python -B -m unittest test_triad_incremental_receiver.IncrementalReceiverTests.test_batch_equivalence_dft_static_and_ou` — 1 passed.
- Witness integration: same method from `validation/witness/tests/` — 1 passed.
- Evaluator covers float64/complex128 and float32/complex64, 1D/2D/3D batches, strided input, DC and nonzero singleton, multibin DFT, valid raw rows, input-length errors, dtype/shape/nonmutation, plus independent `np.fft.fft` instrumentation. Single precision uses `rtol=atol=2e-6`; double precision uses `1e-12`.

A preflight version initially failed before assertions due to a malformed strided-array reshape. That evaluator setup issue is documented in `preflight/setup-failure.txt`; it was corrected with a 4*n backing allocation. The final baseline/witness outcomes above are from the corrected evaluator. Original pre-expansion evaluator is retained at `preflight/evaluator-before-dtype-coverage.py`.
