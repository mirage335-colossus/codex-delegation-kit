# Objective and measured-tradeoff review

## Scope and provenance

- Assignment: historical evidence review, packet `/tmp/objective-recovery-runs/u763/packet`; source checkpoint `c54e24698c69c79805b5aad86205abdd36d2ca7c` and later ABBA archive says base revision `488c26aae4abc05b5d25f88844562d88cf1ab06` plus a dirty source closure.
- I read `conversation.json`, both predeclarations, the independent audit, screen/qualification receipts and qualification log, plus the c54 trace receipt/log. No later conversation, live project, network, build, or reproduction was used. Archived private candidate/runner/native input are unavailable, so the ABBA result is auditable but not reproducible from this packet.
- Original user objective: quickly get full-suite CPU forecasts for complete receiver work, use all 12 visible logical threads productively, measure CPU margin under parallel work, demonstrate fast GPU-assisted forecasting, address the receiver bottleneck, and avoid another ineffective multi-hour loop. Later user messages emphasize default all-thread use, sustained synthetic scaling research, lower-precision GPU forecasting, and drastic utilization improvement.

## Decision versus objective

The documented proposed decision is to retire the wider-controller experiment after its confirmation failed the adoption gate, retain the measured descriptor improvement, keep the full-hardware-thread default and 18/24-worker overrides, then refresh affected forecasts on final code.

Retiring the wider controller is supported by the predeclared rule: screen selection only nominated `p3w18`; qualification required at least 15% median resident-service gain, both paired ratios below 1, and no more than 5% cold whole-lifecycle regression. Qualification had both pair ratios below 1 and cold lifecycle improved, but resident gain was only 3.89%, so the experiment correctly failed the primary performance gate. The screen's 10.05% point gain was explicitly only a selection threshold, not adoption evidence. Removing/declining that candidate is consistent with the user's speed and measurement-integrity priorities.

This decision only resolves that candidate tradeoff. It does not fulfill the broader objective by itself: the packet contains no complete manually specified suite forecast, no sustained synthetic scaling campaign or external research, no GPU/RunPod comparison, and no full-12-thread throughput demonstration. The candidate ABBA's busy-core equivalents rose from about 4.12 to 5.78 of 12 while resident service improved little; that is evidence of more CPU activity, not effective maximum utilization or CPU margin. Preserving an all-hardware-thread default is consistent with the user's explicit preference, but the supplied measurements do not establish it as near-optimal. Explicit 18/24 overrides remain unqualified by this ABBA for general throughput.

## Arithmetic checked (calculated from archived receipts)

- Median resident reduction: `(18.61343620948901 - 17.889080125984037) / 18.61343620948901 = 0.03891576`, i.e. 3.8916%, below the 15% requirement.
- Cold complete-lifecycle reduction: `(41.1629585289993 - 38.40945439549978) / 41.1629585289993 = 0.06689277`, i.e. 6.6893% faster, within the gate's maximum 5% regression (improvement is not regression).
- Pair ratios from qualification log: `17.857663119983044 / 18.887908185002743 = 0.945455`; `17.92049713198503 / 18.338964233975275 = 0.977182`; both are below 1, as audit records.
- Screen point gain is recorded as 0.1004769979 = 10.0477%, just over the predeclared 10% screen threshold; this does not conflict with the qualification result because the screen only chooses a single candidate to qualify.
- The audit reports 9 looks and exact recomputation of 87 jobs' five selected spans/unions/envelopes/gaps, parity and memory checks; 12 effective logical CPUs (6 physical cores), common 5 GiB cap, and zero fallbacks/retries. These strengthen receipt integrity but do not increase generality beyond the single configured-calendar row-7 fixture.

## Independent earlier checkpoint

The c54 trace's matched control and trace outer times were 18.892250648 s and 18.864654315 s. The recorded overhead `-0.00146072` (trace about 0.146% faster) is negligible; numeric difference was zero. Its predeclaration explicitly says this was a chart/timing trace, not a throughput adoption trial. Its `thread_time_ns` deltas and callable spans are not OS CPU-running intervals, so it cannot establish thread utilization. It used five windows and a selected fine cycle, not the complete requested suite.

## Limits / remaining acceptance evidence

- No contrary arithmetic found in supplied audit/log. Source/candidate correctness and exact run reproduction cannot be independently rebuilt because the private candidate, runner and native input were not reconstructed.
- These archives support declining the 3-owner/18-worker candidate for default adoption. They neither show that the current 2-owner/12-worker path is optimal nor justify general deployment of worker overrides based on performance.
- To claim the original objective complete still requires matched complete-suite CPU forecasts on final source, a supported sustained scaling/margin result for this CPU, representative evidence of productive use of all 12 logical threads (using actual OS CPU telemetry, not callable intervals), and GPU-assisted forecast timing/accuracy evidence. The archived results cannot substitute for those checks.
