# Helper finding: projection work for the supplied workload

## Scope and source evidence

- Read only `participant/task.md`, `participant/fixturedata/projection-workload.json`, and files under `participant/tools` and `participant/tests`.
- Workload: 64 samples at 64 Hz; required band is exactly `[0, 0]` Hz; no excluded bands. It is explicitly a constructed deterministic contract slice, not a throughput trace.
- In `tools/triad_dynamic_joint.py`, `BlockProjection.make` builds `np.fft.fftfreq(samples, 1/fs)`, creates a full-length keep mask, and selects all bins within half a bin of each required band (lines 72–88). For this geometry the sole selected DFT row is DC, index 0: bin spacing is 1 Hz and the selection interval is [-0.5, 0.5] Hz.
- `BlockProjection.numpy` currently calculates a full `np.fft.fft(..., norm="ortho")` and only then indexes selected rows (lines 96–102). Thus 63 of 64 transform outputs are discarded in this workload. Existing `valid_rows` does direct indexing, but is not equivalent: it would retain 64 raw samples and change the projection's shape/meaning.
- Equivalent work for this exact selected row is a last-axis sum scaled by `1/sqrt(samples)`. A narrow-bin direct projection can replace the full FFT while preserving the one-row output contract. Preserve FFT behavior for other geometries and accepted inputs; precision/rounding and dtype need explicit compatibility checks before changing the path.
- The receiver's existing erased-block/zero-basis branch already bypasses projection and Gram work (`ProjectedJointReceiver` around lines 219–230); it does not apply to nonzero basis data and does not eliminate the observed-data projection in this workload. No production edit was made.

## Discriminator attempt and limits

Attempted a small NumPy comparison using the assigned interpreter and actual `BlockProjection` against the direct DC reduction, including batched leading dimensions. The invocation failed during module import before assertions because the module imports sibling `triad_gaussian_prepared` as a top-level module and `tools` was not on `sys.path` (`ModuleNotFoundError`). Therefore this check executed **zero assertions** and supplies no runtime equivalence evidence. A rerun with `PYTHONPATH=tools` or working directory `tools` is the minimal next discriminator. No workload throughput was measured, and no claim about end-to-end speedup is supported.

The included receiver test uses nonzero bands and does not establish the sparse-DC optimization's contract. The public API must continue to validate its existing input lengths/shapes and preserve selected-row result shape and dtype; those behaviors remain unverified here.
