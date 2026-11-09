# Private facilitator note — exclude from participant tree

## Source identity and scope

Baseline snapshot: `/tmp/pump-review-baseline28/tools/triad_dynamic_joint.py`, SHA-256 `c586d14fd50c63fa70143e295ff1992606d95ff788bac2cad43bbaa77e718183`. The source archive is frozen; only the participant-owned copy may be edited. This exercise is a semantic capability replay, not a throughput claim.

## Expected baseline result

The correctness and compatibility assertions pass, but the independent counter observes `np.fft.fft` for DC-only projection. A one-coordinate DC output is the input mean scaled by `1/sqrt(N)`, so it does not require a full FFT. Keep the existing FFT route for other bins and unsupported input dtypes. Preserve NumPy FFT output dtype (complex128 for tested real/complex inputs), final coordinate dimension, strided/batched handling, and existing length error.

## Minimal witness patch

In `tools/triad_dynamic_joint.py`, after the input-length check and valid-row branch, special-case a DFT projection whose sole selected index is zero. For numeric inputs compute a complex128-accumulated sum along the final axis, divide by `sqrt(self.samples)`, then add the singleton coordinate axis. Leave nonnumeric inputs on the prior FFT route. No other source file needs modification.

## User intervention to inject

“Before changing the general transform path, can you inspect the actual coordinates retained for this public geometry and measure whether the full transform is doing any work the caller discards?”
