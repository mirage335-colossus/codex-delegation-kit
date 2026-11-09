# Parallel recovery exercises — 2026-11-09

This study tests the user's revised question: can parallel development agents
supply useful challenges and course corrections that would otherwise come from
user intervention? It evaluates executable work, not just whether reviewers
produce more suggestions. No global kit installation or production receiver
change is part of the study.

## First wave: no demonstrated advantage

Sixteen fresh Luna-high owners ran four executable synthetic development tasks
under a two-by-two comparison: the prior uninstalled performance proposal versus
a general recovery cue, with sequential versus parallel scheduling available for
requested helpers. All arms had the same owner and optional-helper allowance.
The exact [protocol](protocol.md), [baseline](freeze/baseline.txt),
[candidate](freeze/candidate.txt) and [arm map](freeze/plan.json) were frozen before
dispatch. The candidate replaced only the performance-specific portion of the
backend's shared instructions.

| Case | Actual required correction | Functional outcome | Ownership-compliant outcome |
| --- | --- | --- | --- |
| Team report | Connect the documented CLI to the existing complete report builder | 4/4 pass | 4/4 pass |
| Deployment dashboard | Stop cache collisions between services with the same capture time | 4/4 pass | 4/4 pass |
| Paginated export | Preserve accepted order and caller-owned project state while reading only the requested page | 4/4 pass | 4/4 pass |
| Routine pagination control | Distinguish omitted `None` from an explicit zero limit | 4/4 pass | 2/4 pass |

Every owner identified the relevant mechanism during the initial inspection.
**No owner requested a helper.** That was sensible on these small cases; it is
not evidence that they ignored a demonstrated need for help. Consequently no
sequential-versus-parallel helper contrast was realized, and the study does not
estimate a concurrency benefit. Each instruction version passed eight functional
checks and seven ownership-compliant checks. The candidate did not improve the
measured outcome. [Per-arm results](results/first-wave-summary.json).

The routine-control failures are two additions of regression tests to protected
`public_tests.py`, one under each instruction version. Neither removed assertions
or broke functionality, but both violated the exercise's explicit ownership rule.
They are not examples of an architectural dead end. All other patches preserved
the protected files. An [independent arm-blind review](results/first-wave-review.md)
checked the source changes and bounded acceptance evidence.

The two failed arms received the same prewritten user-style prompt and four extra
shell invocations after their autonomous results were sealed. Both rechecked the
already-correct zero-limit behavior and left the ownership violation intact.
These were **assisted continuations with extra budget**, not an equal-budget
estimate of the effect of user intervention. No favorable arm was selected after
seeing the results.

These fixtures contain prior mistaken approaches, but the new owners were never
observed getting stuck themselves. The mandatory request checkpoint also supplied
orchestration scaffolding to every arm. Successful recovery here is not evidence
of spontaneous intervention in a long-running, unrestricted development chat.

## Final replay: supplied parallel support

The separately frozen [amendment](transfer-protocol.md) authorizes one final
capability replay on actual pumpModem projection code. It preserves the first
wave and its failed default-adoption criterion. Four fresh owners receive the
unchanged instruction texts crossed with solo versus fixed parallel support.
Each supported owner gets two concurrent, read-only helpers: one asks what work
can disappear; the other examines correctness and caller constraints. The
coordinator delivers the reports verbatim after the owner's initial observations
are sealed, without adding a solution or repairing the reports.

The replay uses actual source from `28f08825670b76472628b50d98cd648a87aa62e4` and
explicitly constructed projection inputs. It is a historical, targeted replay,
not held-out validation, a physical receiver capture or a throughput benchmark.
Frozen acceptance compares numerical results, shapes, dtypes, errors and input
preservation with the original implementation; counts calls to the general FFT
independently; and runs an existing incremental-receiver equivalence check.
The baseline fails the work-elimination condition; the private witness passes it
and the correctness checks. [Fixture evidence](freeze/preflight/projection/evidence.md).

| Instructions | Support | Correctness and receiver check | Full work-elimination condition |
| --- | --- | --- | --- |
| Baseline | Solo | Pass | Fail: 3 low-precision cases still call FFT |
| Baseline | Two concurrent helpers | Pass | Pass: zero calls in all specified cases |
| Candidate | Solo | Pass | Pass: zero calls in all specified cases |
| Candidate | Two concurrent helpers | Pass | Pass: zero calls in all specified cases |

[Per-arm grades](results/transfer-summary.json) preserve that distinction. The
baseline solo patch is a useful, correct partial optimization with conservative
fallbacks, not a broken receiver or demonstrated dead end. The exact zero-FFT
counter condition was in the study protocol but was not spelled out in the
participant task; therefore its failure must not be equated with failure to make
a useful optimization. The replay criterion is narrower than general performance.

All four owners independently identified the single-coordinate opportunity before
receiving helper findings. Parallel help did **not** discover the algorithm for
them. The invariant helpers added executable dtype/shape/error counterevidence
against a naive replacement, which the supported owners reviewed during their
checks. However, the two work-elimination helpers failed during wrapper/import
setup and executed zero numerical assertions. One invariant helper initially
wrote an inaccurate all-pass summary, then corrected it; the owner received both
the original and correction. Small rounding differences alone were not an
acceptance failure. These records support useful scrutiny, not treating every
helper conclusion as correct.

Both helper pairs actually overlapped, as did part of their owners' inspections.
The supported baseline arm met the broader work condition that its solo comparison
did not, but the candidate solo arm also passed. Four targeted runs, additional
helper effort, variable owner checks and coordinator delay do not establish a
causal quality or elapsed-time advantage. Autonomous activation remains untested
by this fixed-support extension. No extra cases or participant repairs were used
to turn this into a favorable reliability result.

## Evidence quality and limits

Participant inputs were instruction-separated in a shared filesystem, not OS
isolated. Source copies, task contracts, protected checks and private evaluators
were frozen separately. The facilitators knew the case mechanisms. The participant
model/effort settings are observed in local runtime records; provider-side
execution and service-tier settings are not independently authenticated.

Preflight found and retained several fixture problems: an implementation-controlled
work counter, insufficient independent input coverage, an unsuitable routine-control
continuation, a malformed strided-array setup and a workload/check mismatch in the
projection replay. These were corrected before their participants ran. The replay
now labels its constructed inputs honestly. Original setup failures and corrected
checks remain under [preflight](freeze/preflight/).

Participants also made setup and reporting errors: unavailable `python` aliases,
Git commands in copies without Git metadata, a malformed stage-1 JSON artifact,
and inaccurate invocation self-reports. Preserve those failures rather than
counting only the final passing checks. The [session audit](results/session-audit.json)
retains numeric usage, timestamps and tool evidence. Its literal callsite counts
are source-derived and require inspection before being called executed invocation
counts. The first audit lost start timestamps when later context records replaced
them; the corrected script preserves the [earlier output](results/session-audit-before-timing-fix.json).

Helper inference, setup, owner integration and coordinator dispatch all cost work.
The first wave changes no realized helper scheduling; the replay adds both support
and effort. Neither provides a clean estimate of time saved by parallel scheduling.
The audit covers exercise owners/helpers, not all fixture construction, root or
Astra review overhead. Cached input is a subset of input, and token counts are not
subscription allowance or dollar costs. No historical hours saved are claimed.
The [usage summary](results/usage-summary.json) covers twenty owners and four
support helpers, including the two assisted continuations; it is not total study
cost. [Timing overlap](results/overlap-summary.json) distinguishes actual helper
concurrency from facilitator delays.

## Kit disposition

The first-wave adoption rule was not met. The earlier performance-specific
injected instructions are removed from the pending source patch. The existing
policy already covers reassessment, distinct hypotheses, bounded probes and
independent progress. Repeating those rules with a stronger default is not
supported by these results.

The reviewable change is an explicitly experimental, optional
[parallel-challenge recipe](../../README.md#parallel-challenges-when-work-stalls).
It gives helpers the original objective and distinct questions, asks for an
executable discriminator and requires the owner to act on supported findings.
It imposes no helper quota, automatic trigger, new gate or model change. The
candidate remains preserved as an experimental input, not promoted into the
backend or scout defaults.

Astra's [completion review](results/completion-review.md) accepted that disposition
and found no further required campaign or installation. Five existing targeted
prompt-delivery/distribution checks passed, as did `git diff --check`. The study's
[artifact checks](results/artifact-checks.json) report no unexpected issues while
preserving the known malformed participant artifact and initial scanner error.

## Reproduction and scope

Each `results/<id>/autonomous/` directory retains the patch, copied workspace,
independent evaluator output and original owner records. The evaluator was run
in a separate copy with protected-file hashes checked; it was unavailable to the
participant. The two assisted results have separate directories. Do not overwrite
an autonomous result with a later correction.

For a fresh check, copy a retained `evaluation/` directory to private scratch and
run its `evaluator.py` and public tests. Synthetic cases use Python 3 and the
standard library; the projection replay uses the recorded NumPy/PyTorch CPU
environment and its focused existing receiver test. The scripts [exercise.py](exercise.py)
and [transfer.py](transfer.py) document preparation and grading and intentionally
refuse to overwrite frozen cases or sealed outcomes. [audit_sessions.py](audit_sessions.py)
reconstructs local numeric/tool evidence when the original Codex logs are available.
Those private session logs are not required to inspect retained patches and grades.

The replay's six modules and existing receiver test match their original Git
blobs. Their [source provenance](freeze/cases/P1/source-provenance.json) and
[original license](freeze/cases/P1/original-LICENSE) are retained; the kit's license
does not relabel the copied project's source. The selective source copy supports
this local exercise and does not reproduce a complete pumpModem environment.

The maintained kit baseline is `cab99adc30cf20b5740a6f92f7611da2caf224aa`; its
five-file uninstalled performance proposal is retained under
[source-before](freeze/source-before/). The previous pumpModem retrospective was
already untracked and is not rewritten by this study. Source changes, installed
state, Git preservation and experimental effectiveness remain separate claims.
