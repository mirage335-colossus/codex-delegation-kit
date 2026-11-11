Implemented the normal path in `/tmp/precision-generalization-workflows/w21/core.cpp`: it uses a float lookup table with linear interpolation, generates readings directly without an input buffer, and retains direct double precision for `--audit`. Storage reporting includes the table.

Checks passed:

- `python3 public/check.py`: smoke, varied shapes, boundaries, and high-accuracy audit.
- Documented build: `c++ -O3 -std=c++17 -DNDEBUG -march=native core.cpp -o ./curve-processing`.
- Production normal mode vs full-shape double audit: max sample delta `9.334e-8`; max mean and mean-square errors per reading `8.70e-10` and `5.40e-9`; threshold counts matched in all 32 buckets.
- Production runs on an AMD Ryzen 5 PRO 5650U: `0.079218 s` in the recorded run, with three repeats at `0.063175–0.065260 s`, below the `0.12 s` limit. Reported storage: `33,816,580` bytes.

Independent acceptance review remains pending.
