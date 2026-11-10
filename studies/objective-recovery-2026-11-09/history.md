# CPU utilization retrospective evidence

Source: session JSONL `/home/user/.codex/sessions/2026/11/09/rollout-2026-11-09T01-27-53-01a1bf34-d662-7713-a2c4-da8c9e459da6.jsonl`. Physical JSONL lines and UTC timestamps are in `utilization-originals.json` alongside exact visible message text. Internal analysis was excluded.

## Visible chronology

- Line 17 (2026-11-09 07:28:42Z): User's original task called for productive high utilization of all 12 available CPU threads, complete receiver estimates, credible margins under parallel execution, and receiver optimization. It also reports a *prior* 5.5-hour effort. That is prior-work user report, not this session's measured active time.
- Line 2757 (09:35:54Z): User again requested full 12-thread utilization and asked for sustained CPU scaling research.
- Line 4711 (11:40:50Z): User stated that using fewer threads due to this computer's thermal limits would risk regression on other CPUs; default should use all available threads.
- Line 6855 (18:26:50Z): User asked to restructure for drastically better utilization.
- Line 14683 (23:45:05Z): Assistant reported the measured five-window service-time change (21.68 to 18.95 s) and mean busy cores 2.91 to 3.57, while full 12-thread saturation remained unproven.
- Line 16082 (2026-11-10 00:43:52Z): Assistant said the timing chart showed rolling overlap and substantial preparation/adaptive-prediction spans. Transcript evidence of the chart; artifact not independently inspected here.
- Line 17257 (01:33:24Z): Assistant said the proposed three-controller default would not be adopted: 3.9% settled-service improvement with busy cores 4.12 to 5.78; it would remove the wider-controller experiment. The user countermanded the throughput-only threshold at line 17394 (01:36:42Z), saying a minor improvement with higher utilization was worthwhile. Assistant accepted at line 17400.
- Line 18878 (02:54:39Z): Assistant reported average busy-core utilization 4.21 to 8.63, all 12 owners active for 36.4 s, and matched work/results.
- Line 19575 (03:35:47Z): Assistant reported 9.73/12 threads busy for 55 s with backlog, excluding preparation and monitor overhead; sustained 100% remained unproven.

## 15% gate and ABBA evidence

Before the decision message at line 17257, the tool transcript reads `local-evidence/receiver-oversubscription/predeclared.json` (tool call/output lines 16933/16936). Its qualification contract predeclares one independent ABBA comparison, baseline/winner/winner/baseline, 13 windows with selected tail jobs 7–12; it requires at least 15% median resident-service gain, both pair ratios below 1, at most 5% median cold whole-run regression, and numerical/work/resource/provenance gates. It states common fixed memory admission and says a memory-ineligible candidate or baseline failure stops the comparison. The experiment driver is `local-evidence/receiver-oversubscription/run.py`; transcript excerpts show its selected service-union measurement and the 12-thread budget checks (tool call/output lines 17016/17019). Screen logs were read at lines 17072/17075, 17106/17109, and 17118/17121. ABBA qualification log was read at lines 17171/17174 and 17195/17198. These exact log paths are `local-evidence/receiver-oversubscription/screen.log` and `local-evidence/receiver-oversubscription/qualify.log`.

The screen selected p3w18 after p2w12 measured 18.316 s / 3.846 busy cores, p3w18 16.475 s / 5.265, and p6w24 16.584 s / 7.045. Qualification ABBA observed baseline service 18.8879 and 18.33896 s, candidate 17.85766 and 17.92050 s; both paired ratios improved (0.9455, 0.9772), but median service reduction was 3.8916%, below the predeclared 15% threshold. Median cold lifecycle reduction was 6.6893%, below the allowed regression (there was no regression); busy-core median rose 4.116 to 5.778. Status was `performance_gate_rejected`, `failure: null`.

The visible transcript supports that the gate existed before the ABBA result and was the stated rejection reason. It does **not** show the user choosing or explicitly authorizing a 15% adoption threshold, nor identify who first proposed that exact percentage. It is in an assistant-maintained predeclared experiment artifact; do not infer more authorship from the file alone. The recorded qualification completed all four looks, with no runtime memory/admission failure. Therefore memory or correctness failure is not supported as the actual alternative reason for the line-17257 decision. A later docs patch at tool lines 17294/17297 links `screen.json`, `qualify.json`, and `predeclared.json`, but that documentation edit occurred after the decision and is not evidence those JSON artifacts were already present before it; the contemporaneous evidence is the `.log` outputs.

## Time-accounting limit

Visible conversation reports 5.5 hours for prior work. It does not contain a user claim that this session consumed 10+ active hours. Session wall-clock span is not active-work duration; measured benchmark intervals above are the only supported execution durations here.
