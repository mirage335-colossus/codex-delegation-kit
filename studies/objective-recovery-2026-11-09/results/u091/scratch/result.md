# Bounded continuation result

## Decision

The latest user steering changes the decision on the three-owner experiment: **do not retire/reject it solely because it missed the predeclared 15% resident-service gain threshold.** The user explicitly values higher busy-core use even for a small speedup. The archived result supports keeping the three-owner route as a candidate for a source-bound validation. It does **not** support silently promoting it to the default yet: exact candidate source is absent, the evidence covers one row-7 stream only, and measured busy use reached only 5.77/12 cores on average.

The original ABBA result remains `performance_gate_rejected` under its stated criterion. This is not a corrected/erased failure: median resident service gain was 3.89%, below 15%, while both matched resident ratios were <1 (0.9455, 0.9772); full-lifecycle cold time improved 6.69%, inside its -5% regression bound. Average busy cores increased from 4.116 to 5.778 (+40.4%, +1.662 cores). Work/message parity, input identity and source stability passed the independent audit. These are useful favorable measurements under the user's updated utility preference, but not a full-suite result or a current-source qualification.

## Case-specific requirements and adjustable decision

- Hard user outcome: prioritize CPU receiver bottleneck, preserve complete receiver work and accurate forecasts for the manually specified suite, use available threads effectively, and demonstrate stable measurement provenance. Latest steering makes higher utilization a positive criterion even when speed gain is minor.
- Experimental gate that was declared for this ABBA: at least 15% median resident gain, both pair ratios below 1, no more than 5% cold lifecycle regression, plus parity/resource/provenance. It failed the first criterion and passed the other recorded checks. Keep that historical status intact.
- Adjustable choice now: whether to continue evaluating a 3-owner/18-permit route despite missing that performance threshold. User's later message resolves this in favor of continuing the evaluation.
- Limits of inference: 3-owner/18-permit versus 2-owner/12-permit is a software-owner/permit setting on a 12-thread machine, not evidence of 12/12 productive utilization. This archived one-stream ABBA is not a complete manually specified suite forecast, a broad CPU saturation study, or GPU evidence.

## Evidence checked

`audit.py` is an executable, stdlib-only discriminator; its output is preserved below. It rechecks the receipt audit status, unchanged source/driver/input identities, same 12-thread denominator, ABBA gate arithmetic and source scheduling bound. The independent audit reports 9 looks, 87 jobs with five unique ordered spans, exact exposed-work/message parity within each phase, recomputed CPU usage including reaped decoder CPU, no retries/fallbacks, and modeled plus sampled memory checks at a common 5 GiB cap. The ABBA candidate is not reconstructible here: its dirty 66-file closure, exact native artifacts, private runner and native input are explicitly absent from this packet.

The earlier c54 checkpoint is separate evidence. Its source and input were unchanged across a 5-window trace; maximum numeric/message differences were zero and the timing check was qualified only as `singlematchedcontrol_within10percent_slowdown`. It captures five `fine_tracking` spans totaling 24.322 s but only two selected fine cycles totaling 0.067 s, so the selected cycle is too sparse to explain the dominant tracking cost. It does not validate the later ABBA candidate. In that immutable source snapshot, `_dispatch_ready` caps jobs at two and receipts report `maximum_processes: 2`; the architectural extension point is identified, but source changes in this environment are prohibited.

The trace's 13.026 s `parent_drain` interval has negligible recorded parent thread CPU, suggesting time spent waiting for children is a meaningful wall-clock dependency. Trace docs explicitly say callable intervals are not OS CPU-running intervals; do not read the drain interval as CPU consumption or infer scheduler/thermal causes from it.

### Executed check output

```text
PASS archived receipts: unchanged source/driver/input; 12 hardware threads; complete ABBA; exact exposed work by audit
ABBA p2w12 -> p3w18: busy cores 4.081 -> 5.773; gain 3.89% resident, 6.69% cold
resident paired ratios=[0.9454547822379967, 0.9771815301752439]; acceptance required >=15% resident so archived gate remains rejected
earlier c54 checkpoint: 5-window captured source/input, exact decision/numeric parity, timing qualification=singlematchedcontrol_within10percent_slowdown; 5 fine_tracking intervals totaling 24.322s while traced fine_cycles total 0.067s (sparse cycle not representative)
bounded source serializes capacity to two in _dispatch_ready; controller drain can wait with negligible parent CPU, but called intervals are not OS scheduled CPU time
```

## Next action and prerequisites

1. The project owner should recover the exact ABBA candidate closure, native artifacts, private driver and input identified by the archived receipt/audit, then check that they correspond to the current live revision before reuse. This packet cannot establish that mapping or restore the candidate; do not recreate it from the 6-file c54 extract and call it the measured implementation.
2. On current source, run one bounded paired validation of `p2w12` versus `p3w18` over the complete manually specified CPU suite, preserving the same per-case inputs, complete lifecycle, numerical/work/message gates, CPU-time denominator of 12, and memory admission. Keep the user-authorized utilization gain as a decision metric alongside resident and cold throughput; report both. Cover sufficient repeated matched looks to distinguish a stable small gain from noise and retain all negative gates/results. Only then decide whether 3 owners should be default.
3. If the candidate is unavailable, the bounded source checkpoint points to `_dispatch_ready` / backend admission and process caps as the implementation area to revisit. The predeclared ABBA budget used a common 5 GiB cap and at most 210 seconds total qualification with 10 seconds teardown; use coupled memory admission and include tracker, native owners, input/IPC and DSP workspace. The archive says 50 ms RSS is a sampled estimate, not a hard OS cap.

## Entry point and limitations

The archived driver SHA is `b51f875d…`, but it is not included. The packet exposes the Python API class `CompleteStreamReceiver` in `triad_stream_receiver.py`; it does not establish a supported current CLI or exact invocation. The trace records CPython 3.13.5 on Linux, but the required current environment, test-suite runner, suite fixture list and prerequisite native build/artifacts are unverified. Resolve those before executing the paired suite. I used no network, receiver build, production edit, installation or external service. No receiver tests were run in this continuation.
