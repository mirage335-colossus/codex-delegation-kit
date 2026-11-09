# Private facilitator note — exclude from participant tree

## Source identity and scope

Baseline snapshot: `/tmp/pump-review-baseline28/tools/triad_dynamic_joint.py`, SHA-256 `c586d14fd50c63fa70143e295ff1992606d95ff788bac2cad43bbaa77e718183`. The source archive is frozen; only the participant-owned copy may be edited. This exercise replays the actual frozen projection implementation; the supplied workload is a constructed deterministic contract slice, not a historical capture or a throughput claim.

## Expected baseline result

The numerical, dtype, shape, stride, caller, and error assertions pass, but the independent counter observes `np.fft.fft` for the supplied one-coordinate DC projection. Its normalized value is `sum(values)/sqrt(N)`, so a full FFT is unnecessary for that result. Keep the existing FFT route for other bins and unsupported input dtypes. NumPy FFT returns complex64 for tested float32/complex64 inputs and complex128 for float64/complex128; preserve that dtype behavior and the final coordinate dimension.

## Minimal witness patch

In `tools/triad_dynamic_joint.py`, after the input-length check and valid-row branch, special-case a DFT projection whose sole selected index is zero. For numeric inputs compute a complex128-accumulated sum along the final axis, divide by `sqrt(self.samples)`, cast to the dtype NumPy FFT returns for the input precision, then add the singleton coordinate axis. Leave nonnumeric inputs on the prior FFT route. No other source file needs modification.

## User intervention to inject

“Before changing the general transform path, can you inspect the actual coordinates retained for this workload and measure whether the full transform is doing any work the caller discards?”
