# Bounded continuation result

## Decision

The proposed disposition should stand in its operational sense: **do not adopt or advertise the wider-owner/18-worker route as the receiver default**. Keep the user's requested 12-hardware-thread default. Preserve the ABBA finding as a promising but unqualified comparison, and avoid using its predeclared 15% threshold as though it were a user requirement. The qualification missed that experiment's acceptance rule, but it did not show that the candidate was harmful: both paired resident ratios favored it, median resident service improved 3.892%, full lifecycle improved 6.689%, and busy-core equivalents rose from 4.116 to 5.778 of 12. Those results are evidence worth retaining, not enough to qualify/adopt a changed scheduler. Explicit 18/24-worker overrides are also not validated defaults: the screen covered them, while the winner was the 3-owner/18-worker route and that route failed qualification.

This is not evidence that the receiver now uses all 12 hardware threads effectively. Neither archive measured 12 busy cores; the measured candidate reached only 5.778 busy-core equivalents. The 15% resident-gain gate was part of the experiment design, not a stated user acceptance requirement. The user-level goals—complete CPU forecasting for the manually specified suite and productive use of available hardware—remain unmet by this packet.

## Evidence checked

- Read the historical conversation excerpts, provenance note, predeclarations, screen and qualification receipts, logs, independent audit, frozen source extracts, and earlier c54 timing trace.
- The independent receipt audit reports exact source/driver/input checks for the later comparison, 66 frozen source files, nine looks (five screen plus four ABBA), 87 jobs with all five ordered spans, exact recomputation of union/envelope/gap metrics, parity, and no fallback/retry. It confirms the experiment's `performance_gate_rejected` result. The archived result is not a re-runnable test here: the exact dirty candidate source, runner and raw input are absent, as the provenance explicitly says.
- Screen selected p3w18 at a 10.0477% point gain; qualification resident reduction was 3.8916% against its predeclared 15% threshold. The two paired resident ratios were 0.945455 and 0.977182. Cold lifecycle reduction was 6.6893%, within the predeclared no-more-than-5% regression rule. Candidate busy-core equivalents increased from 4.11594 to 5.77779.
- The earlier c54 trace is a distinct source checkpoint and experiment (revision `c54e24698c69c79805b5aad86205abdd36d2ca7c`) from the ABBA source revision `488c26aae4abc05b5d25f88844562d88cf1ab06c`. It reports unchanged source/input, zero numerical difference, and successful matched control/trace. Its selected fine cycle is explicitly an early fixed cycle, not a representative warm average; the trace is useful for dependency diagnosis, not for attributing later ABBA gains.
- The frozen scheduler source shows two-owner maximum, shared aggregate worker permits, no hidden queue, and dispatch of a second public window only after its full input is available. With two ready windows, permits are split (e.g. 6+6 at total 12); a lone job can use all permits. The trace's quiet slot 3 had serial parent input assembly/transport and ordered commit around overlapped child scoring, while the sampled fine-basis phases submitted six statically partitioned jobs and joined every future. In the selected cycle, basis phase was about 20–22 ms; worker wall spans were roughly 4–8 ms. These are narrow sampled intervals, not evidence of whole-run OS scheduling or a sustained-utilization ceiling. Source inspection and trace point to a useful next measurement: separate ingress/dispatch waiting, child scoring, and the underfilled/within-owner fine work across the actual suite before changing scheduling.
- Executed [`check_evidence.py`](check_evidence.py). It checked the headline receipt/audit claims, ratios, gate comparison, source and input integrity flags, and the trace's limited scope; output is recorded below.

## Requirements, experiment choices, and assumptions

**Historical user requirements:** complete receiver-work forecasts over the manually specified tests; effective use of available 12 CPU hardware threads; credible CPU margin measurements; and a fast GPU-assisted forecasting method. The historical conversation also allowed RunPod within budget, but the assignment explicitly disallows cloud work here and is not new authorization for a cloud action.

**Experiment-specific conditions, not user requirements:** 15% resident improvement, the selected row-7 stream, its 13-window qualification, the 5% cold regression ceiling, route set, memory cap, and exact ABBA procedure. Their failures must remain recorded, but none alone answers whether a modest gain is useful to the user.

**Evidence limits:** measurements are from different source checkpoints; ABBA candidate cannot be reconstructed from this packet; one trace's fine-cycle sample is nonrepresentative; callable/thread CPU intervals are not OS CPU-running traces; and no evidence here demonstrates a GPU forecast method or the complete manually specified suite.

## Concrete next action and prerequisites

Continue with the previously stated next action: refresh CPU forecasts on the final source, covering every manually specified test with complete receiver work. First obtain/identify the exact final checkout and source/native artifact hashes, the authoritative manual-test manifest and inputs, the supported forecast entry point and interpreter, and its resource/memory limits. These inputs and the entry point are **not established in this packet**; do not guess a command or infer that the frozen `c54` tools are the final runner. Use the existing authorized runner once its owner confirms those prerequisites, recording per-case coverage, full lifecycle and resident service, CPU busy-core equivalents over the matching interval, peak memory, and source/input identity. Then target a bounded same-input scheduling comparison only if those full-suite measurements still show a consequential gap; compare the supported 12-permit schedule against a concrete candidate while preserving complete work and memory limits. Keep the original gate result intact.

The GPU-assisted path should remain a separate unmet requirement. It needs a concrete, provenance-preserving estimator and validation against the full-precision CPU outcomes before it can support forecasts; no suitable entry point, accelerator implementation or comparison is supplied here. No receiver build, live source edit, installation, cloud operation or benchmark was executed.

## Executable check output

```text
ABBA status: performance_gate_rejected / verified_performance_gate_rejected
Coverage: 5 screen routes; 4 ABBA looks; audited 9 total looks and 87 jobs
Resident: 18.613436s -> 17.889080s; reduction=3.892% vs 15.0% predeclared gate
Paired resident ratios: 0.945455, 0.977182
Cold lifecycle: 41.162959s -> 38.409454s; reduction=6.689%
Busy-core equivalents: 4.116 -> 5.778 / 12
Earlier c54 trace: control/trace passed, exact numeric parity, inputs/source unchanged; selected cycle is explicitly nonrepresentative.
Archive boundary: ABBA revision 488c26aae4abc05b5d25f88844562d88cf1ab06c; earlier trace revision c54e24698c69c79805b5aad86205abdd36d2ca7c; no reconstruction attempted.
```
