Implemented the proposed fast path in `/tmp/precision-generalization-workflows/w11/core.cpp`: float LUT interpolation for normal processing, exact double calibration for `--audit`, double aggregate accumulation, and exact recalculation near the assay cutoff.

The public smoke and audit checks passed. On the 4096×2048 scan, the production run took **0.057085 s**. Compared with the same-binary audit output, maximum sample error was `9.334e-8`, maximum per-reading bucket mean error `4.694e-8`, squared-mean error `2.9911e-7`, and threshold-count difference `0`.

The build and captured production result are in the assigned workspace. I did not time the original implementation.
