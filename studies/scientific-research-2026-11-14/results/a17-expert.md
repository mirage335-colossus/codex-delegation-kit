# A17 independent review

At revision `13db435fc85114be2e2a0298580d5c3e2bcba996`, both receiver schedules pass Helper frequency intervals to coarse search. The existing fallback supplies the full public frequency prior. Fine scoring gets coarse-derived coordinates and DATA IQ. The first ablation can therefore diagnose Helper frequency restriction. There is no Helper channel-gain handoff in this path to ablate.

## Matched replay

1. For each captured or simulated slot, replay identical IQ and validity inputs through the current DATA receiver with the actual Helper intervals and with the existing full-prior fallback. Keep the public grid, proposal limits, receiver priors, and admission rules fixed. The full-prior arm can search more tiles by design. Record the Helper result, intervals, search work, and coarse and fine proposal survival in both arms. For simulation only, check interval coverage and proposal proximity offline against the planted public-coordinate reference and declared grid tolerances. In drifting cases, also inspect whether DATA support traverses the intervals over the slot. Use the labels to interpret recovery after the replay.
2. Replay the exact same completed public DATA proposal bank with the current basis and the cheapest plausible improvement. Start with the existing selective-delay anchors if disabled. If anchor coverage is already active, try a small public delay bank with shared delays and blockwise complex gains, freezing the arrival, frequency, clock, bits, windows, and proposal records. Use the fallback bank first on cases that survive coarse and fine search. Repeat this paired scorer comparison on the Helper bank if both proposal banks are viable and the first comparisons suggest an interaction. Replay score diagnostics only when a candidate bank cannot be consumed by the normal evidence path. An offline fit at planted coordinates can bound losses from proposal selection, with a separate diagnostic label.

Full-prior recovery with the same DATA basis identifies a loss from Helper-restricted search when the baseline excludes viable DATA support. If both arms contain comparable support but the retained candidates differ, inspect ranking and pruning before attributing the loss to an incorrect frequency interval. Repeated recovery with a basis change at fixed proposals identifies a DATA-model contribution. Missing usable proposals in both arms leaves the basis comparison inconclusive and points the next check at coarse and fine proposal generation. A gain only when fallback and an improved basis are combined calls for both interventions. A wide search that loses to proposal crowding leaves Helper transfer unresolved for that slot.

## Model and decision controls

At 75 Hz spacing, the idealized equal-power, independent two-tap channel at delays 0 and 7 ms gives normalized correlation magnitude `abs(cos(pi * delta_f * 0.007))`, about 0.078 for neighbors and 0.988 for the outer pair. This is a direct falsifier of a diagonal carrier-gain prior for that constructed case. Independent per-carrier parameters can still fit a single well-observed block. A short shared-delay bank can express the joint structure and use the existing shaped delayed-wave templates where envelope delay matters. The simulator also applies common phase evolution after ray combination. Include a common-phase-only control and a flat or static selective control ahead of tracker work, with off-anchor cases to test generalization.

Any candidate model used for ordinary decisions must use fixed, normalized model and delay weights for both bit hypotheses, preserve the public coordinate priors and evidence support rules, and reserve its assigned mass when skipped. Keep thresholds and the baseline false-accept budget in the comparison. Measure paired correct and wrong accepts, erasures, and bit evidence on signal slots, plus false accepts and high-confidence tails on noise, representative interference and wrong-hypothesis cases. Compare at matched false-accept risk and record compute and memory. Improved residual fit alone supports a diagnostic hypothesis. A shared-path tracker merits a follow-up when viable proposals survive, the cheap selective-delay model still loses on independently varying rays or delays, and a predeclared small shared-path model yields repeatable calibrated acceptance gains at tolerable compute. If the cheap model matches those gains, the ablation gives no basis for adding tracker state.

## Evidence scope

Two read-only commands ran in `/home/user/___quick/p/_cur/dataPump/pumpModem`. Both exited zero.

```sh
git show 13db435fc85114be2e2a0298580d5c3e2bcba996:src/triad_receiver.cpp | sed -n '150,192p;365,468p'
git show 13db435fc85114be2e2a0298580d5c3e2bcba996:src/triad_simulation_stream.cpp | sed -n '795,968p'
```

The shaped-basis and anchor descriptions come from the owner’s source findings. The two-ray calculation is analytic. No working-tree baseline or runtime behavior was checked, and the replay remains unexecuted.
