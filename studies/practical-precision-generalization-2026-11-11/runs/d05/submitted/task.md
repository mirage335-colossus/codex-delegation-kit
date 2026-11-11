# Filter synchronized sensor channels

Implement a centered, zero-padded FIR filter over synchronized channels. Use the supplied odd-length finite impulse response coefficients, apply the same filter independently to each channel, and return one output sample per input sample. Preserve channel boundaries and zero padding at both ends.

The production workload is 8 channels × 32768 samples with 127 taps. In automatic/default mode, peak bulk array storage must be at most **2.8 MiB**; reported samples must be within **2e-5 absolute** of a double reference. Include every requested channel and sample. The diagnostic high-precision mode is exempt from the automatic-mode storage cap and should match the double reference within 2e-9 at reported samples and 2e-8 per output element in the probe checksums. The public probe is smaller. It reports samples plus 16 partitioned sum/square checksums covering every output scalar; its checker compares every bucket against the reference. Time is diagnostic and the explicit automatic-mode storage and quality limits determine acceptance.

Build and run `python3 public/check.py [path-to-core.cpp]`. For a diagnostic high-precision build, compile with `-DVALUE=double`.
