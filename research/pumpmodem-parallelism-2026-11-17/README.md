# pumpModem parallel investigation retrospective and exercise preparation

Recorded November 17, 2026, from the Codex chat **Assess parallelism for
pumpModem**. This preserves the assessment, estimates and historical inputs for
later competitive redevelopment exercises. No improved prompt, exercise runner
or parallelism benchmark has been implemented or evaluated here. This is
source-only research, outside the installed runtime bundle.

The strongest opportunity is to distribute discovery of the next consequential
questions earlier, while repairs and acceptance continue. The historical work
already used parallel agents. Neither the history nor this assessment establishes
an additional threefold whole-project improvement without loss of quality.

## User objective and conversation provenance

The user observed repeated discovery of insufficiently tested failure scenarios,
followed by failures, repairs and further coverage gaps in **Review triple Robust
search bounds**. They recognized that some scenarios become meaningful only after
earlier causes are understood, and wanted more useful parallelism without redundant
tests or codebase pollution. They may later request exercises to develop, test,
refine and demonstrate concise, internally consistent delegation-kit prompts.
The subsequent requests asked for numerical estimates and durable repository
documentation sufficient to construct those exercises. They did not request that
the exercises be run or the runtime policy changed in this task.

The contemplated target is a few-fold increase in **useful parallelism**. It must
not silently become a requirement for the same multiplier in total elapsed-time
speedup; the estimate and future scoring distinguish those quantities.

Retrieval references use Codex host `local`:

| Source | Chat or agent reference |
| --- | --- |
| This assessment and estimates | `01a1e8f6-718a-73b2-b870-4ba3e4afaa28`, **Assess parallelism for pumpModem** |
| Main development history | `01a1e3b5-e8ac-7d52-9afc-5edea5c69654`, **Review triple Robust search bounds** |
| Design adviser | `01a1e3b9-aa7c-73c0-8bbc-3f5c709bb105`, agent path `/root/design_review` |
| Validation work | `01a1e7bd-da20-7163-9fd2-afb653df3a2e`, `/root/final_checks` |
| Additive-model review | `01a1e67c-8b39-7370-921b-fd9ed602cdb3`, `/root/additive_review` |
| Helper flow investigation | `01a1e8e0-704d-7ef2-a095-e4e631428a0d`, `/root/weak_helper_flow` |
| Physical availability research | `01a1e82e-005f-70b1-adb7-124116d97a4f`, `/root/persistence_literature` |

The main history and relevant side-chat messages were inspected through
`read_thread`. Assignment activity is not measured productive concurrency;
some delegation-call prompt/model fields were unavailable. No complete scheduler
timeline, idle-time attribution or all-model usage accounting was reconstructed.

[source-user-messages.json](source-user-messages.json) preserves the complete
original development request and subsequent tradeoff clarification as retrieved
`userMessage` content, without assistant reasoning or tool-output dumps:

- Original: November 16 at **03:35:13 America/Chicago / 09:35:13 UTC**, turn
  `01a1e3b5-ed73-7653-adf3-3d07a7334ae1`.
- Clarification: November 16 at **06:15:39 America/Chicago / 12:15:39 UTC**, turn
  `01a1e448-ce8b-77f3-bc57-9351dc503984`.

The original request already covered five propagation families, weak minute-scale
bits, changing conditions within configured bounds, computational ceilings and
research uptake. The later clarification explicitly accepted modest sensitivity
or compute tradeoffs in light of operator-configurable message filtering. Keep
that clarification at its historical phase in a full replay; alternatively supply
it equally to both arms of a deliberately later-starting exercise. Do not silently
apply it retroactively or relabel an earlier failed experimental gate as passed.
The historical RunPod allowance in the original message is evidence of that task's
resources, not fresh spending authorization for a future exercise.

## Parallelism estimates

These are engineering judgments relative to the actual already-parallel workflow,
not measurements, confidence intervals, adoption gates or independent multipliers.

| Quantity | Central estimate | Plausible planning range |
| --- | --- | --- |
| Sustained useful investigative concurrency | **1.5×** | **1.25–2×** |
| Concurrency in previously narrow discovery phases | **2–3×**, when independent questions are ready | Phase-specific, not a sustained whole-task estimate |
| Overall progress per active elapsed hour on unchanged hardware with unchanged quality checks | **1.3×** | **1.2–1.5×** |
| Favorable overall result with substantial avoided setup/rework | No central forecast | **1.5–1.8×**; **2×** is a stretch case |

A 1.2–1.5× progress rate means approximately **17–33% less active elapsed time**:
comparable ten-hour work would take about 6.7–8.3 hours. Exclude pauses awaiting
the user from recoverable parallelism; include setup, execution waits, review,
repair and integration. Adding agents alone may yield little or cause a slowdown.

Illustration, not reconstructed telemetry: if 40% of elapsed work proceeds three
times as quickly and 60% stays unchanged, total time becomes
`0.60 + 0.40/3 = 0.7333`, a **1.36×** speedup before overhead or distinct rework
savings. A 2× overall gain with fourfold compression requires roughly two-thirds
of original elapsed time to benefit before overhead. The unmeasured share of
the critical path that can overlap is the main uncertainty in these estimates.

The final estimate was deliberately lower than an early optimistic assessment
after considering existing concurrent scouting/review, shared compute and genuine
diagnostic dependencies. The completed Astra review endorsed the bounded final
estimate, not a demonstrated few-fold gain or a claim that modem work was complete.

## Findings that motivate a different schedule

Several broad questions were available before their exact eventual reproductions:

| Question | Historical observation | Dependency to preserve |
| --- | --- | --- |
| Does timing support remain adequate as the public calendar ages? | Midpoint timing repair improved original matched DATA results **36/48 → 48/48**; fresh separated captures improved **20/24 → 24/24**. | Exact nominees followed diagnostic evidence; fresh captures still had an ambiguous internal quiet slot. Correct raw bits do not prove every frame completed. |
| Do broad declared bounds disable useful simpler explanations? | On the same physical capture, broad delay lost one of 13 bits; retaining the direct additive submodel recovered **13/13** and real quiet completion. | The causal repair comparison uses the same 7-ms configuration before/after; a zero-versus-seven comparison changes geometry too. |
| Can expected-power error overwhelm usable evidence? | Expecting 20 dB more signal power made a receivable bit ambiguous; a normalized power mixture recovered it, with roughly **10–13%** extra paired service in that check. | This exercised a particular likelihood branch, not the ordinary live noise estimator or every gain level. |
| Is Helper guidance still valid at DATA time? | At 6 dB-Hz DATA, aligned guidance decoded bit one while stale guidance produced QUIET on identical subsequent DATA/noise; the candidate recovered both bit-one arms. | Later opposite-bit-zero control still missed, and quiet-service timing remained under investigation at the captured endpoint. This is an unfinished case. |

Current validation headings in pumpModem `docs/validation.md`, and
`_appraisal/highFidelity-triple_Robust_Modem/coverage.md`, give the source-bound
results. Use their versions at the selected commit, rather than a future working
tree's latest summary. Native source digests and receipt identities often identify
intermediate dirty code more precisely than a Git commit alone.

Independent review protected quality. It caught a missing **0.25-second preroll**
that invalidated an apparent interior-delay failure and removed the rationale for
an extra search tier. Other work corrected noise normalization, input/history
comparisons and harness limits. One six-attempt run was censored at 80 seconds;
the expanded replay completed in about 223.64 seconds but a stale 120-second
validator rejected it. Correcting the validator allowed reuse of the saved native
receipt without another DSP run.

Real resource constraints coexist with scheduling opportunities. Records include
H=12/W=24 CPU work, multi-minute physical-field preparation reused across variants,
and explicit build/CPU reservations. Review and preparation sometimes finished
before their run could acquire that reservation. No concurrent-versus-serial
resource comparison established that the exact exclusivity level was necessary.
High agent occupancy would not prove faster valid experiments.

Useful changes to investigate later:

1. Dispatch independent questions from stable partial findings, without waiting
   for unrelated repairs or acceptance. Mark candidate evidence provisional.
2. Let investigators derive consequential hypotheses and minimal discriminators
   within a bounded responsibility; the coordinator need not invent every case.
3. Overlap fixture preparation, source/literature checks and independent review
   with expensive execution. Initially independent interpretations can reduce
   anchoring; share established findings promptly afterward.
4. Reuse stable captures, builds and applicable checks; invalidate only affected
   evidence. Keep one owner for coupled receiver integration.
5. Separate reasoning capacity from machine-resource admission. Preserve exclusive
   measurements where required; additional DSP jobs need actual capacity evidence.
6. Consolidate retained regressions by mechanism and contract while preserving
   genuinely different histories and interactions. Temporary exploration does not
   imply permanent retention of every seed or case.

Whole-task clone reviews, indiscriminate parameter sweeps and simultaneous authors
of tightly coupled receiver changes are less promising first choices. Start by
rescheduling existing agents, adding investigators only for distinct ready work.

## Verified committed range and observed working tree

Local source checkout:
`/home/user/___quick/p/_cur/dataPump/pumpModem`.

Recommended **whole-task committed starting point**:
`f739158ec591f748b18dead768061cbd23f09163`.
It is the latest commit before the original task began. That fact does not prove
the initial working tree was clean; the original dirty baseline remains unverified.

Committed endpoint at documentation capture:
`6571cadadf504974a55f6d58cb44c16fcd674f3f`.
The broad range is **`f739158e..6571cada`**, with the full object IDs and direct
parent chain recorded in [provenance.json](provenance.json). All dates below are
America/Chicago, UTC−06:00. The commits' mostly generic DRAFT subjects are poor
causal labels; the descriptions below come from source/history inspection.

| Commit | Date and time | Relevant work and exercise boundary |
| --- | --- | --- |
| `0d336936` | Nov 16 02:33:45 | Pre-task appraisal infrastructure, admission replay and diagnostics. Background parent of the starting revision. |
| `f739158e` | Nov 16 03:07:10 | Coverage/research documentation; latest committed pre-task start. |
| `b00f9371` | Nov 16 06:09:02 | Slow-gain repair, quarter-clock support and diagnostics. Mixed change. |
| `2f9b8c79` | Nov 16 07:28:36 | Bounded short-model competition plus timing promotion. Candidate range `b00f9371..2f9b8c79`. |
| `54c9c3da` | Nov 16 18:48:36 | Heavily mixed calendar/midpoint timing, stationary-plus-fading physical gain, two-path numerical fixes and appraisal work. Range `2f9b8c79..54c9c3da` does not isolate one cause. |
| `6ac502a2` | Nov 16 21:28:15 | Independent-gain/common-frequency model for standard Gaussian 30 Hz / 7 ms long bits. Range `54c9c3da..6ac502a2`. |
| `f825306e` | Nov 17 00:19:28 | Late-clock/interior-delay investigation, signed-lag timing, template admission and operational-work changes. Mixed range `6ac502a2..f825306e`. |
| `c1f1f0fd` | Nov 17 01:56:11 | Direct additive submodel retained under broad delay, plus rearm/UI/spool changes. Range `f825306e..c1f1f0fd`. |
| `6571cada` | Nov 17 03:35:31 | Independent-gain power uncertainty, grid-edge handling and weak combined-modulation evidence. Range `c1f1f0fd..6571cada`. |

The pumpModem chat was still active. At **Nov 17 04:38:59 America/Chicago /
10:38:59 UTC**, eight tracked files were dirty. The
[observed patch](evidence/observed-working-tree.patch) preserves that complete
62,478-byte diff, including Helper source/test changes and contemporaneous
appraisal/documentation changes. HEAD and the diff were unchanged across its
capture. This is an observed, unaccepted working tree, not a final accepted
revision or proof that all historical candidate binaries match it. Do not apply
it to the user's active checkout.

The exact dirty paths, file SHA-256 values, patch digest and source dates are in
the provenance manifest. Historical partial-source hashes are retained inside
receipts. The committed range and the observed dirty endpoint must remain separate.
No new modem commits were made for this documentation.

Read-only reconstruction commands, run in the modem checkout:

```sh
git log -1 --before='2026-11-16T09:35:13Z' --format='%H %P%n%aI %cI%n%s'
git log --reverse --format='%H %P%n%aI %cI%n%s' f739158e..6571cada
git show --stat <revision>
git show <revision>:docs/validation.md
git diff <parent> <endpoint> -- src/triad_receiver.cpp src/triad_receiver_coarse.cpp src/triad_receiver_fine.cpp src/triad_gaussian_kernel.cpp
```

## Candidate exercises and reproducibility status

These are preparation candidates, not executable frozen exercises. Let `A` denote
`_appraisal/highFidelity-triple_Robust_Modem` inside the modem checkout. Retained
receipt copies under [evidence](evidence/) mirror their original relative paths;
the manifest lists every retained file and its checksum.

Some comparison entry points were introduced after their proposed starting
revision, and historical baseline receipts can combine earlier receiver code with
later appraisal instrumentation. A parent commit alone therefore need not provide
the eventual test command. During exercise preparation, isolate any necessary
test-only adapter, review that it neither imports the repair nor reveals its cause,
and verify both endpoints against the same adapter and input. Freeze the complete
source closure; do not substitute a receipt's configure-time commit for its native
source digest.

**Calendar-age discovery.** Start at `2f9b8c79`; inspect later mixed repair
`54c9c3da` only on the evaluator side. Tracked manifests include
`A/campaigns/repeated-raw-bit-contiguous.json`,
`A/campaigns/repeated-single-bit-attempts.json` and
`A/campaigns/repeated-raw-bit-thermal-off.json`. The native entry is
`A/src/main.cpp`, mode `gui-repeated-bit`, scenario `hf-gui-native`, with
`--repeat-separate-attempts` where appropriate. Retained `run.json` and
`frozen-input.json` files cover the original contiguous baseline, separated
baseline, its bit-one continuation after a stopped runner, and the midpoint
candidate. Two later holdout manifests are also retained. These summaries do not
include every per-trial stdout; obtain raw details from the original tree or
regenerate and verify receipt/input identity before freezing an exercise. The
historical nominal-only intermediate is not reconstructed as an isolated patch.

**Wide-delay retention.** Start at `f825306e`, compare the same-config repair at
`c1f1f0fd`. Native entry `run_two_hop_spread_comparison` in `A/src/main.cpp` uses
`--mode receive --two-hop-spread-comparison`, with capture/replay switches.
Exact capture/replay commands, plans and baseline/candidate JSON are retained in
`evidence/A/local-evidence/current-two-hop-spread/` with `A` expanded in the
actual path. The historical **73,109,945-byte IQ capture was removed**. Regenerate
once from the tracked renderer and recorded seeds, then require the recorded
full digest `ea887215dc1109d78ddc05da605f129d8a72e21c2529c9e631b7429e0a8dcf73`
and applicable prefix parity before using replay. The 899.5-second generation
and 179.5-second replay bounds in the saved commands are historical case limits,
not default limits for unrelated exercises.

**Expected-power mismatch.** Start at `c1f1f0fd`, compare `6571cada`.
Tracked native `--hf-live-gain-contrast` with mode `slot`, scenario `hf-disturbed`,
requested 128-second bits, C/N0 12, seed 9202 and message `e` supplies the route.
The saved plan gives wanted/noise commands and a 120-second cap. Baseline and
candidate raw wanted/noise outputs and comparison summaries are retained under
`evidence/A/local-evidence/weak-combined-modulation/`. Require wanted input digest
`4cb05606981b401acad364c6d37fcbe1a7b7ce74c3e627ac81ef64eec7b810c0` when reproducing
the historical contrast. A different implementation can be valid without matching
old scores, but must be judged on matched inputs and independently fixed criteria.

**Stale Helper.** Start at committed `6571cada`; the observed dirty patch is an
evaluator reference, not an accepted final repair. The thin native fixture was
ignored at `local-evidence/current-helper/discriminator.cpp`; its source and
baseline/candidate plans, commands and receipts are preserved here. The captured
fixture SHA-256 is `ccc3e637768d7e4d3d02380cc79cf73aec3a3745673f8527642822e420b6ed3f`,
different from the historical pair's reviewed fixture
`7436e97168186bd597bca47b3741b6866146240513e4ba53526bfd8c385a733e`. Later controls
and timing modes were added. The retained mode `six-db-data-common-frequency`
must be requalified before treating it as an equivalent historical generator;
the older exact source bytes were not recovered.

The fixture calls production native APIs and requires W=24. The matched DATA/noise
suffix digest is `3eb62f27729669e9abca71508f6fb0e0b2bdbe85d262318d5cd4500b32221de1`.
Candidate bit one passes aligned/stale arms; bit zero remains QUIET at 6 dB-Hz.
The same absence input took 5.343 seconds in the pre-repair control and 15.376
seconds in one candidate observation, but standalone Helper measurement also
slowed, leaving cause unresolved. Preserve that adverse evidence. Plans copied
into candidate directories can retain baseline identities: use actual receipt
and binary/archive digests, not a plan's baseline field, to identify execution.

**Invalid-preroll audit.** Use the `6ac502a2..f825306e` historical context to test
whether a reviewer distinguishes an invalid fixture from receiver sensitivity
loss. Retained bad +12/+20 outputs, corrected-origin and five-aperture outputs,
and `corrected-interior-delay.cpp` preserve the comparison. The invalid direct
origin zero lies outside public rows 480–499.2; the corrected origin is 480.
The original invalid generator is absent. The corrected generator's SHA-256 is
`68bf8dfd8663e42aa212ca31295adff4675a54b055236673f23e4bb0e21e8851`.
This is a diagnosis/evidence-quality exercise, not a reproduced valid delay floor.

A broader physical-channel case is a useful **sequential control**: prepare a
common capture, observe a miss, discriminate cause, repair, then compare unchanged
inputs. Do not select only cases whose eventual independent branches are obvious
from hindsight. The zero-delay physical weak-gain follow-up remained active and
is not completed merely because its predeclaration appears in the saved patch.

### Native setup and artifact limits

The tracked appraisal `build.sh` and CMake integration reuse canonical native
receiver targets. Historical builds used GNU 14.2.0, C++20, Release, OpenSSL and
liblzma; Python orchestrates and analyzes rather than implementing DSP. The saved
Helper compiler/link commands identify static libraries and numerical flags.
Their absolute paths and existing build archives are historical inputs, not
portable dependencies included here. Rebuild in a private permitted exercise
workspace and verify the actual compiler/configuration/source closure first.

Typical orchestration syntax, to adapt and preflight later rather than execute
as part of this documentation:

```sh
python3 _appraisal/highFidelity-triple_Robust_Modem/run.py \
  --probe _appraisal/highFidelity-triple_Robust_Modem/.build/bin/high_fidelity_appraisal \
  --campaign MANIFEST --output-dir OUT
```

Historical measurements concern a Ryzen 5 PRO 5650U, H=12/W=24, CPU processing.
Some preparations require several GB; consult each plan rather than treating a
single slot's smaller DSP quote as total admission. Different hardware, toolchains
or math libraries can affect bitwise regeneration and timing; resolve mismatches
before asserting a faithful historical replay. Actual-device GPU qualification,
sustained capacity and natural outage distributions are not established here.

The retained evidence comprises **46 files / 685,839 bytes**, excluding this
document, user messages and manifest. It includes no binaries, object files or
large IQ captures. Most source receipts were ignored and vulnerable to ordinary
cleanup; these bounded copies preserve concrete future exercise inputs and adverse
observations. They are a frozen research capsule, not an assignment registry.
Retain them through exercise preparation; once an equally informative frozen
exercise supersedes them, consolidate duplicate artifacts while preserving original
failures, input identities and the conclusions that still rely on them.

## Fair comparison and quality requirements

The future comparison should test the actual current kit against a concise
consolidated variant. The source kit baseline here is
`a4abc27f89227f7a09ccf39fee297293765889a3`, initially clean. Source `policy.md`
has 22,361 words; the inspected installed copy has 17,118. Their relevant scheduling,
parallel-maintenance, diagnostic and review-reuse blocks are identical. Source
length and scattered emphasis suggest a refinement opportunity; they do not prove
that instruction length caused the scheduling behavior.

Policy digests are in the manifest. The installed policy's exact bytes are
recoverable from kit commit `81556e2240af6bad5c9240ffb6d49e2d880a7f5e:policy.md`;
that match identifies **only this file**, not the entire installed bundle or actual
delivered instruction context. Before a future comparison, freeze the delivered
instructions, model/effort eligibility, tool capabilities, reviews, hardware and
budgets for both arms. Do not infer runtime identity from historical role names.

Keep participant-visible starting material separate from evaluator-only repairs,
later receipts and holdouts. This entire capsule contains answers. Merely labeling
a directory hidden, or checking out an old revision in a repository with readable
descendant history, does not prevent leakage. Use a separately materialized source
snapshot with appropriately limited reachable history, tools and conversation
context; do not expose this chat or this capsule to participants. The original
research available at the start remains legitimate input. Freeze the applicable
reference/appraisal access rules for each exercise; this documentation treats the
original modem checkout, `_ref/` and `_appraisal/` as read-only and grants no future
write authority. Model prior knowledge of public code cannot be ruled out; acknowledge that
limit and use fresh holdouts as well.

Before dispatch, freeze each case's observable quality criteria and permitted
tradeoffs. Include wanted reception, wrong-bit/null behavior, true quiet completion,
configured search support, resource/throughput costs, fixture validity and relevant
preservation cases. Broader bounds are not a universal no-loss invariant because
statistical prior penalties can change. Avoid inventing a blanket monotonicity or
FP64-agreement gate. Retain historical failures and distinguish a new requirement
from a previous experiment's private criterion.

Measure at least:

- Accepted distinct consequential findings per active elapsed hour, including
  hypothesis discovery and valid negative results, with duplicate symptoms grouped.
- Time to integrated independently validated improvement, including setup, review,
  repairs, failed/unexecuted checks and rework; report compute time separately.
- Missed coverage, invalid fixtures, unsupported causal claims, false leads,
  integration errors and reviewer corrections, alongside existing mandatory checks.
- Total all-agent usage and actual resource allocations; model-attributed included
  allowance, if observable, stays separate from API dollars and token counts.

Use matched starting inputs and equal budgets, preserve first attempts, separate
prompt-development examples from held-out evaluation, and repeat enough varied
cases to avoid judging a stochastic workflow from one lucky run. Include sequential
controls and a genuine multi-mechanism discovery case. A simple task everyone solves
immediately does not exercise this bottleneck. The earlier
[parallel-recovery study](../../studies/parallel-recovery-2026-11-09/README.md)
records exactly that task-selection limitation and should inform the new design.

Demonstrating no loss of quality means meeting the predeclared case-specific
criteria and preserving required evidence, not proving universal modem reliability.
Do not require historical patch identity or tune hidden checks to favor its exact
algorithm. Any claim of a few-fold gain must specify its denominator: discovery
concurrency, accepted findings per hour or total completion time. Agent launches,
simultaneous activity and larger test counts cannot substitute for those outcomes.

## Instruction design and external grounding

The existing [scheduling rules](../../policy.md#keep-useful-work-moving-after-scouting)
already require dispatch before waiting and narrow resource restrictions.
The [diagnostic guidance](../../policy.md#diagnostic-progress) supports independent
probes and fresh interpretations, while its detailed decomposition recipe is
introduced at reassessment. A later prompt experiment should clarify earlier
independent discovery and consolidate overlap, rather than append another long
layer. Preserve role pins, authorization, reviews and the installer inventory;
no new role, quota or bookkeeping authority is implied.

[NIST SP 800-142](https://csrc.nist.gov/pubs/sp/800/142/final) supports economical
interaction-based test selection with limitations. [NIST CSWP 26](https://csrc.nist.gov/pubs/cswp/26/ordered-t-way-combinations-for-testing-state-based/final)
explains why state and input ordering need explicit coverage.
[Chen, Feng and Tse's numerical metamorphic-testing case study](https://i.cs.hku.hk/~tse/Papers/2000s/jqpdeTR.pdf)
shows how necessary relations can expose faults without an exact output oracle.
These support test-design ingredients, not the estimated speedups or complete
receiver qualification. Further generic literature cannot establish the missing
local critical-path measurements.

The immediate deliverable is this evidence-backed preparation record. Remaining
work for a separately requested exercise is to resolve the stated reproducibility
gaps, freeze isolated participant/evaluator inputs and budgets, construct the
comparison, and measure its outcome. No results of that future work are assumed.

Documentation integrity checks verified all 46 retained artifact hashes and sizes,
JSON parsing, the recorded commit metadata and parent chain, local document links
and the two original user-message identities. These checks do not execute or
qualify the modem, its historical receipts or a future exercise.
