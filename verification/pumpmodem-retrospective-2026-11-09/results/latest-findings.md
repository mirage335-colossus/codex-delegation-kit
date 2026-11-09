# Latest chat retrospective evidence (bounded cutoff)

Scope: root transcript through physical line 7135 (zero-based ordinal 7134), 2026-11-09 18:38:48Z, with supplemental dependency-child evidence through 18:40:10Z. Main transcript: `/home/user/.codex/sessions/2026/11/09/rollout-2026-11-09T01-27-53-01a1bf34-d662-7713-a2c4-da8c9e459da6.jsonl` (22,083,826 bytes at last stat; 7,159 lines at cutoff inventory). Do not treat subsequent active implementation as validated.

## Chronology and direct claim evidence

- Root user line 6855 / ordinal 6854, 18:26:50Z: requested substantially higher receiver core utilization and possibly tensor-core use; RunPod GPU availability mentioned. This is a change from prior throughput framing and sets the latest objective.
- Root assistant line 6997 / ordinal 6996, 18:32:33Z: summarizes GPU scout finding that fine processing is ~2.4% of cloud trace.
- Root assistant line 7079 / ordinal 7078, 18:36:17Z: summarizes CPU scout: manual cases prepare same native waveform lane six times across clock/channel hypotheses; these banks use about one core and account for roughly half nominal CPU service in two cases.
- Root assistant line 7135 / ordinal 7134, 18:38:48Z: picks two implementation candidates: share prepared waveform work across clock/channel projections, and fuse rendering, projection, and statistics for fine-search candidate tiles into one worker task. Immutable worker inputs and single native-cache ownership were called out. This is a proposed next direction, not a demonstrated fix.

## Verification / denominators

### GPU fine-path share

Artifact: `local-evidence/current-tensor/fp16/disposition.json`. In its FP16 paired row, whole `driver_seconds` = 61.764197929 s; `process_seconds` = 64.5 s; fine = 1.482477504 s. Fine / driver = 2.40022%, matching the 2.4% claim. The fine work is 5.248% of the 28.24786109 s common-measured-component sum. That denominator sums simulation 15.5411, initial bank 2.76315, acquisition 4.10346, fine 1.48248, recurring banks 4.35768. The 61.7642 s whole driver denominator includes 32.32984 s validation-only CPU reference/check; therefore “2.4% of paired driver elapsed time” is accurate, while “2.4% of GPU work” is not established. ZoomFFT comparison: whole driver 59.9813 s, fine 1.80087 s (~3.0%), common sum 28.3144 s (~6.36% fine). The paired-driver elapsed ratio is a prioritization clue, not proof that the remaining CPU/GPU service can be accelerated by a given design.

### CPU bank service share

Artifact: `local-evidence/current-parallel/calibration-current-all8.json`, source revision `15b17f7d3886f1baadf3c22b8990083eda6f85cd`; provenance says unchanged at completion and hashes match. The receipt records 15b17f7d plus dirty paths. All 61 declared shared-source hashes were independently matched to immutable 247b7202 in receipt-source-check.json; this is source-content equivalence, not a new measurement at that commit. The figures are from saved calibration samples:

- Row 5, HF Encrypted / GPS DO: recurring-bank preparation .1209458452 s/s; nominal service .2319399688 s/s; ratio 52.145%. Two bank samples took 7.25675 and 7.13216 s; `busy_cores` .98986 and 1.00165.
- Row 7, HF No Encryption / GPS DO: recurring-bank preparation .1170752987 s/s; total .2211626434 s/s; ratio 52.936%. Two samples took 7.02283 and 7.02452 s; `busy_cores` .98907 and 1.00403.

The denominator is per-second nominal service for these cases; measured samples are roughly seven seconds, normalized against about 60 seconds of slot time. Thus “roughly half” is supported for these two cases; it is not a workload-wide fraction. Geometry reported: 71,205 raw rows, 78 template lanes, estimated work 11,107,980.

## Native lane reuse claim: code facts vs instrumentation

Immutable source comparison at revisions 28f08825, 3fb65026, 15b17f7d, and 247b7202: the original 28f loop is epoch → clock → bit → ray; later revisions batch lanes while still nesting clock and ray work. The batching layout is later, while the repeated clock×ray work is already present at 28f. The six-way clock×ray multiplicity is inherited, not a newly introduced 247 regression. At 247, `tools/triad_case_replay.py` public-screen geometry uses three clocks when clock bound is nonzero and two ray alternatives when delay/Doppler spread applies. `tools/triad_realtime_fft.py` has 13 epochs × 2 bits = 26 base epoch/bit lanes, and loops three clocks × two ray choices; resulting 78 lane hypotheses and 11,107,980 estimated sample-work are consistent with the artifact (71,205 rows × 78 × 2). `tools/triad_case_replay.py` passes a mapped provider into `FFTScreen`; `tools/triad_continuous.py` routes `NativeStream.basis[_mapped]` calls to the native stream.

Important qualification: “same native waveform lane six times” is a useful description of repeated clock/ray waveform sampling/projection work, but overstates repeated source construction if read literally. `tools/triad-helper-export.cpp` caches `PatternSource` by `(epoch_offset, source_bit)` within a stream and its `PatternSource::Impl` has two tile-cache slots; `src/triad_basis.cpp`/`PatternSource::sample_at` still perform the sampled waveform and carrier/ray projection for each mapped query. The bank is not simply rebuilding six independent PatternSource objects.

No direct provider request counter exists in the inspected baseline `NativeStream`/C++ service. Static call-count estimate only: at 71,205 rows and 16,384-row chunks, mapped path could issue five chunks × six clock/ray alternatives = ~30 lane-batched requests; integer route could issue five chunks × six alternatives × 26 lanes = ~780 one-lane requests. These depend on chosen provider route and are not observed call counts. Artifact’s 78-lane / sample-work totals are observed report fields, not a direct request counter. Later CPU child transcript shows an in-progress private instrumentation attempt (`requests`, `sample_values`, `lease_groups`) but it was not validated by cutoff and was not read from current mutable source.

## Other latest architectural evidence

Read-only child `/home/user/.codex/sessions/2026/11/09/rollout-2026-11-09T12-30-35-01a1c193-9040-7b03-a57b-71ec7ec5e051.jsonl` (`receiver_dependencies`): child line 485 / ordinal 484, 18:35:25Z, reports candidate trajectories independent through fixed-state segments; adaptive pruning/global merge remains a segment-boundary barrier. Existing joins follow rendering, projection, then coherence update per fine block, so candidate-tile fusion is plausible. It warns `NativeStream` request pipe and `CachedMappedBasis` LRU mutation need a single owner; do not concurrently push nominal/adaptive calls through the same provider or nest shared executor work. These are source-derived dependencies, not perf measurements. Child line 555 / ordinal 554, 18:40:10Z, notes tests do not directly cover `bulk_statistics` or fused DATA render→projection→r/G and lack some failure/lifetime edge checks.

GPU child `/home/user/.codex/sessions/2026/11/09/rollout-2026-11-09T06-13-31-01a1c03a-5983-76f0-a520-685d7cebbb1b.jsonl`: isolated FP16 transforms reportedly 1.33–1.88×, but no integrated end-to-end gain. Tensor-core use is not established as a high-leverage answer for latest objective from this evidence.

CPU child `/home/user/.codex/sessions/2026/11/09/rollout-2026-11-09T06-13-11-01a1c03a-09a3-7180-babc-8ac36d2c96e0.jsonl`: child line 718 / ordinal 717 reports fine path: `mapped_dispatch` 96 calls, .11006s; `mapped_basis` 96 calls, .26513s; `basis_affine` 16 calls, .1339s; worker FFT 384 calls/.5486s; basis projection 32 calls/.10881s wall, controller CPU .01371s; Gaussian update 96 calls/.28089s; 16 segments. These are fine-path profile timings, not recurring coarse waveform-bank cost. Child line 713 / ordinal 712 reports row7 targeted timings, which should not be mixed with the calibration artifact’s bank samples.

## Status, evidence boundary, and gaps

By latest root line 7135 these were reported scout findings, existing artifacts and source inspection. The fine-tile fusion and bank-reuse changes were selected candidates only. CPU child later began private source edits/instrumentation around child lines 836 and 1550, but there is no validated integrated run or accepted performance result in this cutoff. Root earlier authorized no credentials/cloud work; this bounded update uses only local transcripts, immutable git blobs and existing artifact files. No native compiler failure for these latest proposals is evidenced here.

Relevant search boundary: immutable source revisions 28f/3fb/15b/247, named fine-path profiles, one calibration artifact, one tensor disposition artifact, receiver dependency child, and root timeline through line 7135. This does not establish exhaustive absence of other call-count telemetry across every project branch or prove a causal speedup from reuse/fusion. A small actual-helper call-count wrapper and matched before/after case run would resolve the remaining multiplicity uncertainty, as a separately authorized engineering check in the active implementation chat; this retrospective has not run that performance comparison.
