# Composite an overlay onto a background

Implement the existing RGBA image operation: for each pixel, use the foreground alpha to blend its RGB channels over the background and produce an opaque RGBA image. Inputs are normalized linear-light channel values in [0,1].

The production workload is 1920×1080 pixels. In automatic/default mode, the operation must keep peak bulk array storage at or below **110 MiB**, and sampled RGB output must differ from a double-reference result by at most **2e-5 absolute**. Alpha output must be 1 within 1e-7. The diagnostic high-precision mode is exempt from the automatic-mode storage cap and should match the double reference within 2e-9 at reported samples and 2e-8 per output element in the probe checksums. The public probe also supports smaller dimensions for quick iteration. It reports samples plus 16 partitioned sum/square checksums covering every output scalar; its checker compares every bucket against the reference. Timing is recorded as diagnostic evidence, while automatic-mode storage and quality limits determine acceptance.

Build and run `python3 public/check.py [path-to-core.cpp]`. For a diagnostic high-precision build, compile with `-DVALUE=double`.
