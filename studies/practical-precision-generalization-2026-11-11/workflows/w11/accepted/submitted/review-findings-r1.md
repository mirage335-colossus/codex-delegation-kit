**changes_required**

The implementation passes the public checks and production accuracy/deadline requirements, but two findings remain:

1. **Unjustified cutoff recalculation — `core.cpp:53,64`.** A diagnostic variant removing these guards passed public checks, production `4096×2048/13`, and maximum-size `8192×8192/91` comparisons. Threshold counts matched audit exactly. A focused check of 8,194 adjacent float inputs near the cutoff also found zero classification differences. Nine interleaved end-to-end runs measured median **0.056315 s current versus 0.050926 s without guards**, approximately 9.6% less time. Remove the guards or provide concrete contrary evidence justifying their cost.

2. **Incomplete storage reporting — `core.cpp:32,67`.** Normal mode reports only its 32,772-byte table, omitting `bins`, `ids`, and `samples`—864 additional bytes of declared numerical arrays. Audit reports zero despite its numerical arrays. Account for the live workspace consistently and make the treatment of persistent static storage explicit.

Precision review supports the remaining choices:

- Measurement and LUT interpolation execute in float; `q*q` is float before double accumulation.
- Direct float bucket accumulation **fails** production requirements: maximum mean error `2.505e-5`, squared-mean error `2.069e-4`. Double sums therefore have concrete justification.
- Audit executes double calibration, products, and accumulation. Counts remain exact within supported dimensions.
- Every reading contributes; table preparation is reused throughout each scan.

Executed checks: supplied public tests on current and guard-free diagnostic sources; prescribed native builds; production, maximum-size and singleton comparisons; interleaved production timings; focused cutoff check. Current production took **0.054899 s**, with sample error `9.334e-8`, mean error `4.694e-8`, squared-mean error `2.991e-7`, and zero count difference.

Evidence is under `review-scratch/`, particularly `comparison.json` and `cutoff.cpp`. No production files changed. Comparisons use the inspected audit implementation as the large-case reference; this was not an exhaustive seed sweep. Owner repair and affected-contract re-review remain required.
