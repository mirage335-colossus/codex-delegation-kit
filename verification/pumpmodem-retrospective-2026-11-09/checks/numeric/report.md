# FP32 Gram validation experiment

- Status: `failure_reproduced` for the stated narrow mechanism.
- Hypothesis: a Gram computed from an FP32 finite, nearly-collinear basis then cast to FP64 can fail the strict FP64 PSD check, while recomputing the Gram in FP64 from the same FP32-quantized basis passes.
- Source identity: baseline `28f08825`; `triad_gaussian_state.py` SHA256 `7d13799a4f7838bed4797fea13626c041f40cdf405c597fcf3ad4bae720c7a6c`. Exact tested scope: `GaussianStateFilter._validate_gram` from this module. `triad_gaussian_prepared.py` SHA256 `66b1797e47aba8f97223765d1bdfa7cb62971918b34b7d70e27dd537828b2415` was identified during inspection but not executed.
- Inputs: deterministic 3x2 real basis `[[1,1],[1,1+eps],[0,0]]`, quantized to `torch.float32`, eps in `{2^-10, 2^-12, 2^-14}`. Both pathways passed the resulting 2x2 matrix through actual `GaussianStateFilter._validate_gram` on a `complex128` filter. The internal repair accumulator was initialized as it is by filter initialization.
- Environment: `/tmp/pumpmodem-cleanup-venv/bin/python`, CPU, Torch threads=1. No installs or source edits.
- Command: `/tmp/pumpmodem-cleanup-venv/bin/python /tmp/pump-review-numeric/run.py`; exit 0. Reproduction wrapper SHA256 `28cda9fba2b520a07ce36356085dee2a7532166aae8deeb640999c6de257aed0`.
- Observation: at eps=2^-10 both pass. At eps=2^-12 FP32 Gram cast to complex128 has minimum eigenvalue `-1.4899342426488715e-08` and raises `Gaussian observation Gram is not positive semidefinite`; FP64 Gram from the same quantized basis has minimum eigenvalue `+1.4899342426488715e-08` and passes. At eps=2^-14 the same split occurs (`-9.312941529060481e-10` fails vs `+9.312941529060481e-10` passes). This establishes a numerical mechanism, not a historical exact replay or proof this caused any particular reported failure.
- Evidence: `run.log`; exact wrapper copy at `run.py`; source reconstruction and invocation recipe at `reproduce.md`.
- Uncertainty/next discriminating question: test the actual production Gram-generation inputs and dimensions from the historical failing case, preserving its exact device, accumulation path, and validator entry point. These tiny CPU deterministic matrices establish possibility only.
- Cleanup: only owned scratch wrapper and report/log retained; no child processes started. No OS sandbox claim made.
