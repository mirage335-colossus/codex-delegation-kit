# Separately directed feasibility witness

This was an independently instructed witness, not a baseline or candidate
actor and not evidence that any tested generic prompt caused its work. The
original `RESULT.md`, `WITNESS.md`, `witness_slice.py`, and four JSON outputs
are retained unchanged. `RESULT.md` records the initial failed CMake setup as
well as the subsequent successful configure/build, commands, dependencies,
measurement boundaries, and 9/9 FFT-screen unit tests. Build products and the
separate exploratory calendar scripts are not retained.

To reproduce, first reconstruct the historical source as described in the
parent README, then copy `witness_slice.py` into the root of that reconstructed
source and execute the commands in `RESULT.md` from there. The absolute Python
interpreter path and toolchain reflect the original local environment and may
need an equivalent replacement. The flat JSON records predate the addition of
the optional scenario argument, but use the same reported flat inputs.

An independent reviewer reran all four cases and observed native samples and
templates passed to FFTScreen. The `hf-worst` exporter's margined descriptor
is 21 ms delay spread and 90 Hz Doppler spread; the case list's raw values are
7 ms and 30 Hz. Therefore the example does not reproduce the full listed
case's raw conditions. Its high C/N0, truth-narrowed window, one epoch, one
frequency/clock candidate, short segment, and lack of full tracking or
parallel saturation further limit the demonstration. The timings are not
whole-receiver capacity measurements.
