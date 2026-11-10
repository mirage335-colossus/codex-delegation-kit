# Action recovery study — validation report

**Status: SOURCE, EXERCISES AND FINAL REVIEW COMPLETE; GLOBAL INSTALLATION
AWAITS EXPLICIT USER AUTHORIZATION.** Astra accepted the source, behavioral
exercises, report and archive validation in the [completion review](completion-review.md).
The global installation attempt was blocked before process start by automatic
approval review; it has not been applied.
See the machine-readable
[summary](summary.json) for run-level source hashes, timing, token counts, and
evidence paths.

## Findings

The original eight-run exercise recovered the primary user objective in 8/8
runs combined: each condition had 4/4 successes. Full assignment acceptance after
preservation probes was 5/8 (v2 2/4; baseline 3/4), so these small matched
samples show no comparative advantage for v2. The follow-up repair loop exposed
why isolated examples were insufficient: p-stage patches fixed known blank
metadata examples but failed new nonblank metadata probes; q-stage achieved
full contract acceptance in 1/3 runs. After independent contract reconstruction,
reconciliation and strong arbitration, both x runs passed full semantic acceptance.
That exercised process informed the v4 workflow guidance. The later fresh
batch passed its functional, action, and scope checks in 16/16 runs, but also
does not establish comparative advantage because the baseline arm passed too.
The development cases exercise a consequential deadline and mixed inventory,
where local progress obscured an unmet application goal. The fresh case set
exercises scheduling, recoverable prerequisites, a hard constraint, and
an already-satisfied goal. The evidence supports a workflow lesson about
contract-first review and independent acceptance checks, not a reliability or
trigger-rate estimate.

## Request and question

The user asked for extensive real exercises to test whether more parallel Luna
processing could expose and correct poor decisions, and for an evidence-backed
report Astra could arbitrate. The requested work also includes improving the
delegation kit and testing those changes diligently.

This study tests autonomous recovery in actual development work. For this
study, recovery requires an agent to recognize that its current path misses the
original outcome, reprioritize from the user objective and constraints, perform
a useful authorized correction or discriminator, and validate the result.
Naming a mismatch or proposing later work by itself does not count. The
[protocol](protocol.md) specifies the interventions, controls, and boundaries.

These are actual Luna model sessions executing code and tests in isolated local
workspaces containing synthetic, runnable Python repositories. They use the
frozen backend instruction path, not native subagent role dispatch. The deadline
pipeline is a deterministic scheduling exercise; it does not measure CPU
utilization or establish a new pumpModem performance result. The experiment
tests whether agents discover and correct related decision failures.

## Source and experiment

The comparison is between the maintained dirty draft preserved at the start
of the request and frozen candidate v2. The baseline is not clean `HEAD` and
not the globally installed copy. Candidate v2 combines revised owner/worker
recovery guidance with a deterministic guard against accepting a declared
success while explicit substantive acceptance conditions remain. The
interventions are tested together here; this batch does not isolate their
individual causal effects.

The baseline backend source hash is
`aa18e62d2dff4b5495bbe11369eae81b550faad87179200fce9c7f2f003cad3b`; candidate
v2 is `71a084f9dc7dfca5ed4dc3ee7abdb03c8927ee0400dbf2bfdecae6a3267a2187`.
The baseline dirty-state capture is [initial-state.json](initial-state.json).
Frozen per-file proofs are in the baseline and v2 run
[manifests](results/runs/d104b/manifest.json) and
[metadata](results/runs/d104b/run-metadata.json), plus the candidate's
[version manifest](versions/v2/manifest.json). The corrected condition mapping
is [development-corrected-plan.json](development-corrected-plan.json).

Two development cases were each run twice under each condition. Requested
execution settings were Luna/high; actual settings were verified for all eight
included runs. The table labels `v2` as the candidate and `baseline` as the
preserved dirty draft. Every run's filtered actions, actual patch, checks,
settings, usage, release receipt, and source hashes are in
[results/runs](results/runs/).

| Run | Case / repetition | Condition | Primary objective recovery | Full assignment acceptance | Case2 contract probe | Observed elapsed | Input / cached input / output tokens |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| `d101b` | case2 / 1 | v2 | pass | fail | regression | 69.480 s | 94,002 / 69,120 / 2,328 |
| `d102` | case1 / 2 | v2 | pass | pass | — | 119.877 s | 95,675 / 76,032 / 4,827 |
| `d103b` | case2 / 2 | v2 | pass | fail | regression | 56.910 s | 77,957 / 50,560 / 1,984 |
| `d104b` | case2 / 1 | baseline | pass | pass | preserved | 56.652 s | 89,578 / 71,424 / 1,781 |
| `d105` | case1 / 1 | v2 | pass | pass | — | 95.871 s | 116,606 / 104,832 / 3,943 |
| `d106b` | case2 / 2 | baseline | pass | fail | regression | 70.380 s | 85,493 / 75,776 / 2,675 |
| `d107` | case1 / 1 | baseline | pass | pass | — | 104.687 s | 125,381 / 88,704 / 3,888 |
| `d108` | case1 / 2 | baseline | pass | pass | — | 78.650 s | 95,918 / 79,232 / 2,685 |

Elapsed times use the owned execution observation's actual start and finish
timestamps, not the later lifecycle collection wall time. Token columns are
backend input, cached input, and output counts. Cached input is included in
input accounting. Dollar costs and reasoning-token counters are not reported.
Across the four v2 runs, usage totals are 384,240 input, 300,544 cached input,
and 13,082 output tokens; across the four baseline runs, 396,370 input,
315,136 cached input, and 11,029 output tokens. The combined totals are
780,610 input, 615,680 cached input, and 24,111 output tokens.

## Initial eight-run batch

The scores below apply only to the initial corrected two-case batch; the p/q
repair stages are separate attempts and are not folded into these counts.

All eight included runs recovered the primary user objective. The frozen public
checks and private evaluators also passed, but do not test every preservation
boundary. Grading review found that the frozen private oracle imposes a raw
vendor-receive requirement stronger than the visible task. Its score remains a
separate oracle result; task-visible acceptance criteria are applied the same
way to initial and repair runs. A legacy CLI coverage fixture correction was
completed; it did not change actor patches.

Full assignment acceptance after preservation probes is 5/8: 2/4 for v2 and
3/4 for baseline. Independent review separates primary objective recovery from
preservation and faithful completion. All four case1 runs passed full
acceptance; case2 results are mixed. Baselines also recovered the primary
objective in every run, so the main objective measure has no candidate-versus-
baseline separation here. With two cases and two repetitions per condition,
these results support no comparative causal claim.

After those frozen evaluations, a matched case2 helper probe tested valid
canonical rows with blank optional metadata. The frozen original preserves the
canonical control and all four blank-field variants. Candidate patches
`d101b` and `d103b` regress some of those rows; baseline patch `d106b` does too.
Baseline patch `d104b` preserves all variants. The focused check describes
which fields fail in
[all-case2-classification-boundaries.json](blind-grades/all-case2-classification-boundaries.json).
The earlier one-row compatibility probe also records `d101b` failing while
`d104b` passes in
[d101b-d104b-legacy-reference-check.json](blind-grades/d101b-d104b-legacy-reference-check.json).

These supplemental results are separate from the frozen oracle passes. They
expose valid-field behaviors the frozen evaluator did not cover, so an oracle
pass alone is not full assignment acceptance. They are development diagnostics,
not relabeled held-out outcomes.

## Repair and review loop

Parallel reviewers `r001` and `r002` received the task, source and candidate patch
without the grader's known counterexample. They independently generated regression
evidence; their reports and examples were then supplied to the p-stage repair actors.
The bounded
`p` repair stage fixed all three reported blank-value examples, then failed
additional nonblank-but-unused metadata probes. The matched `q` stage used v3:
one of three runs met the full user contract (`q001`); `q002` and `q003` failed.
No new counterexamples were given during the q stage. Their patches are
archived under [results/runs](results/runs/).

Helper results were sealed before the current patch was exposed in
[contract-helper-seal.json](contract-helper-seal.json). `c001` and `z001`
missed the residual branch. The sealed-original-source `c002` helper did not
find the nonblank metadata case; after reveal, `z002` independently executed
that counterexample. Astra's
[strong arbitration](strong-arbitration.txt) validated a canonical-first rule:
use the existing canonical validator when it accepts the row, irrespective of
unrelated metadata; otherwise use the vendor adapter and its validation.
Canonical key presence alone is insufficient to classify vendor rows.

| Stage | Source / evidence | Observed result |
| --- | --- | --- |
| `p001`–`p003` | v2; matched blank and nonblank metadata probes | All three fixed the reported blank-value examples; all failed additional nonblank-but-unused metadata probes. |
| `q001`–`q003` | v3; matched user-contract probes | `q001` met the full contract; `q002` and `q003` still failed. No new counterexamples were supplied in this stage. |
| `c001` / `c002` | Helper source and outputs sealed in `contract-helper-seal.json` before patch exposure | `c001` missed the residual branch; `c002` did not find the nonblank case from the sealed original-source probe. |
| `z001` / `z002` | Branch checks | `z001` missed the residual branch; after reveal, `z002` independently executed the new nonblank-metadata counterexample. |
| `x001` / `x002` | v3 worker repair under strong ownership | Both completed and passed full independent semantic acceptance. |

Candidate v3 adds a general contract or underlying-rule instruction plus a
materially different counterexample requirement. It also contains Sol's fix
for the controller dead end where an explicit contradiction was terminally
invalid. The [v3 manifest](versions/v3/manifest.json) is the current common
source cue (`agent_backend.py` SHA-256
`fc48750d0ca03173a87b8e67d86cac7ed4a3f2c3f4a387465784fe24855d23dc`); no
further backend changes are planned. The independent
[controller review](controller-review.md) found no blocking source issues. The
313-test receipt and `git diff --check` pass are transcribed in
[controller-disposition-full-tests.txt](results/controller-disposition-full-tests.txt);
this file is not raw saved stdout. The controller still limits dispatch of
queued work. The v3 worker implementation under strong ownership completed as
`x001` and `x002`. No independent recovery branch was needed for fresh runs;
all functional outcomes passed. This ceiling does not establish comparative
advantage or trigger reliability.

In practice, the reviewed workflow requires a takeover to start from the
original task and source contract before seeing a patch, inspect the run
discrepancy, send disputed contract interpretation through strong arbitration,
and require an independent implementation acceptance check. Both x-stage
implementations passed full acceptance after earlier repairs missed the wider
contract. This change is in the v4 full 23-file freeze used for the fresh
batch; the results do not show that it improves outcomes over baseline.

## V4 fresh batch and retained product replay

Candidate v4 is a frozen 23-file source bundle captured before fresh inference.
The [v4 manifest](versions/v4/manifest.json) records its per-file hashes; its
backend file is unchanged from v3. A later one-sentence policy bookkeeping
clarification is recorded in
[final-documentation-clarification.json](final-documentation-clarification.json);
the frozen v4 snapshot itself was not edited. Initial requests were frozen
before launch and repetitions received no cross-run hints.

All 16 fresh `g` runs completed with verified settings: eight baseline runs
(`g001`, `g002`, `g003`, `g006`, `g008`, `g009`, `g010`, `g013`) and eight v4
runs (`g004`, `g005`, `g007`, `g011`, `g012`, `g014`, `g015`, `g016`). The
sealed blind summary records 16/16 passes for functional/control, priority and
action, and scope/original-check dimensions. Required action recovery passed
8/8; hard-boundary controls passed 4/4; already-satisfied controls passed 4/4.
There were no substantive actionable failures. The sealed assessment is
[fresh-sixteen-blind-semantic-summary.json](blind-grades-heldout/fresh-sixteen-blind-semantic-summary.json).

The first owner reports completed artifact handoff in 13/16 runs. `g003`,
`g004`, and `g015` omitted the explicit artifact path and were initially graded
partial for that reporting requirement. After all runs were sealed, the
coordinator verified each artifact by its recorded path and hash and completed
ordinary handoff without another model call or actor-workspace write. The
initial omissions remain preserved; coordinator closeout is not retroactive
first-pass acceptance. See
[fresh-coordinator-closeouts.json](results/fresh-coordinator-closeouts.json).

Raw evaluators exit nonzero in all 16 runs only because the pre-existing empty
runtime scratch lock is present. The predeclared normalizer removes that lock
in a separate evaluation copy; all normalized functional/control evaluations
pass, with no other observed scope violation.

The actual task products are preserved under each
[g-run archive](results/runs/). The archive follows each task's explicit
whitelist: Cedar's dispatcher and `work/`, Marlin's catalog database and
`work/`, Orchid's `work/`, and Harbor's weekly summary. Product files retain
their source mtimes and have per-file hashes in `products/manifest.json`.
The initial replay records used evaluator arguments containing paths into the
original grader workspace; they remain preliminary rechecks and are not proof
of replay from the archive. The corrected independent reconstruction used a new
workspace per run, durable frozen participant fixtures, and only manifest-listed
archived products; it constructed evaluator arguments for each new workspace.
All 16 evaluations passed, and fixture/product hashes and mtimes were unchanged
after evaluation. See [archive-replay-validation.json](results/archive-replay-validation.json).
Runtime-state databases, app-server events, and arbitrary scratch files are
excluded from the archive.

## Session and usage accounting

Run receipts account for 38 substantive model sessions: the initial comparison
(8), independent reviews (2), p/q repair stages (6), helper/branch checks (4),
v3 repairs (2), and fresh runs (16). The eight scope-confounded d-runs and one
smoke run bring the inferred completed model-session count to 47. Four
development pre-turn initialization failures and one smoke pre-turn failure
are counted separately; they started no model turn and have no model usage.

| Cohort | Sessions | Input / cached input / output tokens |
| --- | ---: | ---: |
| Initial baseline-v2 comparison | 8 | 780,610 / 615,680 / 24,111 |
| Independent reviews | 2 | 160,337 / 120,320 / 4,570 |
| p repair stage | 3 | 390,600 / 303,360 / 10,322 |
| q repair stage | 3 | 332,936 / 223,488 / 7,822 |
| c helper runs | 2 | 165,770 / 142,592 / 6,809 |
| z branch checks | 2 | 126,344 / 89,472 / 4,397 |
| x strong-ownership repairs | 2 | 353,831 / 275,584 / 6,796 |
| Fresh g evaluation | 16 | 1,442,249 / 1,080,192 / 28,718 |
| Scope-confounded d-runs | 8 | 284,651 / 186,752 / 10,698 |
| Smoke | 1 | 38,093 / 27,776 / 813 |
| **All completed model sessions** | **47** | **4,075,421 / 3,065,216 / 105,056** |

The fresh baseline arm used 758,720 input, 599,808 cached input, and 13,996
output tokens; v4 used 683,529 input, 480,384 cached input, and 14,722 output
tokens. Cached input is a subset of input. These are token counters only; no
dollar costs or reasoning-token counts are reported. Per-run timings use
execution observation start and finish, not later lifecycle collection times.

## Setup and validation

Runs `d001`–`d008` are excluded from behavioral counts: their command scope did
not permit reading the task, notes, or source. Four later attempts (`d101`,
`d104`, `d103`, `d106`) timed out before a verified model turn and were held
with `settings_verified: false`; they are setup outcomes, not behavioral
failures. Their corrected replacements are identified in the table and
[setup history](setup-history.md).

The no-turn handshake probe recorded initialization at 15.618 seconds, config
read at 0.010 seconds, and thread start at 0.672 seconds. It supports a
startup-contention hypothesis, but does not locate the earlier timeouts
definitively. The coordinator reports that `run_batch.py` now limits concurrent
model turns to two and serializes only the handshake using `setup_lock`; model,
settings, deadline, and frozen v2 source were unchanged. This is an observed
orchestration adjustment, not proof of the timeout cause.

The earlier repository test record reports **310 tests passed** in
[results/unit-tests.txt](results/unit-tests.txt). After the controller fix,
the full repository run reports **313 tests passed** plus `git diff --check` in
[controller-disposition-full-tests.txt](results/controller-disposition-full-tests.txt);
the independent controller review found no blocking issue. The adaptive
parallel reviews `r001` and `r002` are complete. The `g` batch is complete; the
`h/f` run plan for the same four fresh cases (16 planned runs) is prepared but
has not been launched. No `h/f` outcome is reported here. Strong-ownership repairs
`x001` and `x002` both passed full semantic acceptance. The source is validated
and reviewed; global installation awaits explicit user authorization.

## Installation and review status

The concrete install preview is available at
[install-preview.txt](results/install-preview.txt). The apply attempt was
rejected by automatic approval review before the process started because
global persistent installation requires explicit user authorization; repository
instructions alone do not provide it. The recorded block is
[install-approval-block.json](results/install-approval-block.json). The Codex
configuration and gateway remain unchanged, and no alternate installation path
was attempted. The source checkout remains dirty and uncommitted; no push was
made. The [Astra completion review](completion-review.md) accepted the source,
exercises and report; only global installation requires user authorization.

## Limits and evidence links

This is a small development sample, not evidence of general reliability. A
baseline success cannot demonstrate that candidate wording caused an outcome,
and a successful task-specific recovery does not prove native runtime
interception or global installation behavior. The report uses collected
commands, patches, check results, independent grades, observation timings, and
token counters; it does not include raw event logs or model reasoning traces.

- [Astra completion review](completion-review.md)
- [Independent archive replay review](archive-replay-review.md)
- [Machine-readable report and run provenance](summary.json)
- [Experiment protocol](protocol.md)
- [Setup history](setup-history.md)
- [Frozen blind summary](blind-grades/development-eight-blind-summary.json)
- [Semantic grades](blind-grades/)
- [Repository test record](results/unit-tests.txt)
- [Held-out preparation record](results/heldout-prepare.json)
