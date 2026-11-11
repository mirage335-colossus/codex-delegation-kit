Repair in `/tmp/precision-generalization-workflows/wd01/core.cpp` addresses both review findings:

- `storage_bytes` now includes `horizontal` and `horizontal_squares` capacities. Production reports **24,576,000 bytes**.
- Normal-mode window products, sums, mean, variance, square root, and score calculation now use float arithmetic. Scores remain stored as doubles; audit and aggregate reporting remain double.

Checks passed:

- Build with the documented command and `python3 public/check.py`: smoke, four boundary cases, and audit passed.
- Production (`1280×960`, seed 11, radius 15): **0.075 s** by shell timing; a matched normal/audit comparison measured 0.052 s normal and 0.854 s audit. Maximum sample error was `9.53e-5`, maximum normalized bucket mean error `6.66e-6`, maximum normalized mean-square error `1.33e-5`, with zero threshold-count difference.
- Additional edge cases passed: `4096×1` and `1×2160` at radius 127, clipped `4096×33` at radius 15, and production dimensions at radius 0. All reported storage totals and outputs were finite.

The production timing remains below the 0.20 s requirement.
