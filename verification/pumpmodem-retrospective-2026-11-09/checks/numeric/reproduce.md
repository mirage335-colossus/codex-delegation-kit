# Reproducing the validator experiment

This reproduces the local numerical comparison against the actual source at baseline `28f08825` (short hash). It exercises exactly `GaussianStateFilter._validate_gram` from `tools/triad_gaussian_state.py`; it does not execute `PreparedGaussianDesign` or its validator.

From the repository root, with the recorded venv available:

```sh
mkdir -p /tmp/pump-review-baseline28
git archive 28f08825 tools/triad_gaussian_state.py | tar -x -C /tmp/pump-review-baseline28
PYTHON=/tmp/pumpmodem-cleanup-venv/bin/python
"$PYTHON" verification/pumpmodem-retrospective-2026-11-09/checks/numeric/run.py
```

`run.py` imports the reconstructed module from `/tmp/pump-review-baseline28/tools`, sets Torch CPU threads to one, constructs three deterministic FP32-quantized bases, then calls the validator on each Gram pathway. The source revision can be independently identified with `git rev-parse 28f08825`; the executed module SHA256 was `7d13799a4f7838bed4797fea13626c041f40cdf405c597fcf3ad4bae720c7a6c`. The paired `triad_gaussian_prepared.py` hash in the report is source identity only; that module was not imported or executed.
