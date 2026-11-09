# H0 helper check record

This records the already completed bounded helper check. The check was not rerun while preparing this record. Its earlier execution used the coordinator-supplied frozen extraction `/tmp/pump-review-baseline28` for task baseline `pumpModem 28f08825`; that extracted directory has no `.git` metadata, so the short revision could not be independently resolved.

## Reproduction

`command.txt` contains the exact command and stdin program from the recorded execution. `h0_check.py` is a standalone copy of that same program for later reproduction. It imports only `GaussianPrior` and `GaussianStateFilter` from the extracted baseline. Execute from `/tmp/pump-review-baseline28` with `/tmp/pumpmodem-cleanup-venv/bin/python`, `-B`, and one-thread OMP/OpenBLAS/MKL settings as captured in `command.txt`.

The check constructs the zero-observation H0-shaped tensor (`3` hypotheses, `4` candidate rows, `2` taps), uses finite `0.5 s` coherence, applies three blocks with elapsed times `.25, .25, .5 s`, and asserts that every likelihood increment and mean is exactly zero and covariance remains the diagonal stationary power prior to `1e-15` absolute tolerance. The output reports 0.247079 process CPU seconds for the original execution; it is not a receiver timing or speedup measurement.

## Recorded stdout

Exact stdout from the original execution is preserved in `observed.stdout`:

```text
{'check': 'zero-H0 Gaussian update invariance', 'blocks': 3, 'models': 1, 'candidate_rows': 4, 'max_cpu_seconds': 0.247079, 'score_zero': True, 'posterior_stationary_prior': True}
```

## SHA-256

Hashes identify the inspected baseline source, minimal check, and preserved artifacts:

- `baseline/tools/triad_gaussian_state.py`: `7d13799a4f7838bed4797fea13626c041f40cdf405c597fcf3ad4bae720c7a6c`
- `baseline/tools/triad_incremental_receiver.py`: `5937cbcdbe2617d48b3855e04afee087e2f7cd17355cdcb59e23bfd073367d2e`
- `baseline/tools/triad_tracking_receiver.py`: `ed7dadc2b9c8eee5503de108d5ce66650a830a0ea674727fd920125247887506`
- `h0_check.py`: `3803f7db1a4d01877a8711a6a392f457ffcee0184352a91cd62a1a9753b02cf8`
- `command.txt`: `1c60fbe086fcc0893865694ab7edd57081813acb57d66e9af255a66f08b9bb00`
- `observed.stdout`: `191ae350fb54394ef282c1b68eb018daea8e274f0185391e72131b04128f09c6`

## Interpretation limits

This demonstrates only the Gaussian helper's zero-input invariance for the stated shape, precision, model, and three time steps. It does not demonstrate a receiver-level H0-elision score/posterior equivalence or any receiver gain. Shared projection across lanes and H0-elided receiver updates remain implementation hypotheses pending matched receiver checks. Skipping adaptive tracking changes the existing full-output contract (the fixed two-lane mixture and adaptive diagnostics); treat it only as a separate reduced-output mode, not as an equivalent full-work optimization.
