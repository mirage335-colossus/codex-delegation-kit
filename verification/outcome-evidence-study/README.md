# Outcome and evidence prompt exercises

This record supports an exploratory test of generic instructions asking an agent
to connect the user's intended outcome with the evidence and implementation it
actually needs. The motivating pumpModem request asked for brief simulation of
CPU and workspace margins and allowed receiver development. The initial result
reported coarse acquisition and separate tracking probes and said it did not
qualify whole-message or integrated receiver operation. A later user follow-up
explicitly distinguished manual capacity tests from performance regression tests
and asked for a complete receiver and fine-search CPU work. The later clarification
is not included in the historical exercise task.

## Cases and inputs

* `inputs/receiver` is an illustrative two-tone laboratory with a deliberately
  simplified waveform and a condensed task derived from the request. It is not
  pumpModem or a physical-channel qualification.
* `inputs/transfer` asks for a feed importer capacity estimate; its starting
  benchmark exercises only part of the normal entry point.
* `inputs/narrow` asks for a small grammar change, to observe whether agents
  unnecessarily expand a task where a narrow fix is sufficient.
* `historical/EXERCISE.md` contains the task for a selective copy of actual
  pumpModem commit `c578659143f400b7a56f444d4d9773b5a813394b`, the latest
  committed revision found before the original request. The exact dirty and
  untracked state at that time is not known. The selective 42 MB copy contains
  receiver tools, source, tests, list, Markdown guidance and third-party source;
  it excludes data, non-Markdown documentation assets and web content. It has
  no Git metadata. The historical tree itself is not stored here; the frozen
  per-file inventory is `freeze/historical-sha256.txt`. It can be reconstructed
  from the locally available source Git object with `recreate-historical.py`,
  subject to access to that commit and the manifest check.

Before agent dispatch, the derived cases, task instructions and rubric were
frozen; the copy and task for the historical case were frozen later, before its
own dispatch. The fixture checksums were captured with their original `/tmp`
paths in `freeze/fixture-sha256.txt` and the run-copy checksums in
`freeze/input-sha256.txt`. The latter covers the first six actor copies before
dispatch and is not a complete log of later v2/historical actors. `freeze/rubric.md`
records the pre-dispatch criteria, not a claim that the cases are fully blind.

## Comparison

Fresh native default-role agents received the same task wrapper and each got
an isolated *copy* of the relevant files. The baseline received no extra
instruction; the first candidate additionally received `freeze/candidate.txt`.
A review found that wording could permit a useful bound to be mistaken for
completion of an unmet objective. The revision `freeze/candidate-v2.txt` makes
that distinction explicit, and later candidate exercises use the revision.
After those runs, an exploratory v3 emphasized starting work on consequential
gaps. It was frozen before the v3 actors were dispatched, but developed after
the earlier results and is not an independently held-out prompt. `freeze/`
preserves all versions. The exact wrapper wording is in
`actor-prompts.md`.

The candidate text was appended to the exercise dispatch prompt. This tests an
excerpt in that setting, not delivery or compliance through an installed kit.
Native role/model defaults and effective runtime settings were not independently
verified. Agents had a shared filesystem and instructions to stay within their
own copies, not OS-level isolation. The evaluator selected and assessed cases;
there was no verified randomization or blinding. Runs overlap and can contend
for CPU and I/O, so their timings cannot be compared as clean hardware capacity
measurements. Each pair is a small exploratory sample, not a reliability,
causal, or cost estimate.

## Reproducing retained artifacts

Each derived-case patch under `actors/` applies with `patch -p1` to a fresh copy
of the matching directory under `inputs/`; the historical patches apply to a
freshly reconstructed historical snapshot. The companion `*.RESULT.md` is the actor's own report,
including its reported commands and limitations. The actor copies retain their
local task and documentation, but these files are not complete tool-call
transcripts or raw measurement logs. Apply patches in disposable copies, not
over the frozen inputs. Applying all nine derived-case patches to fresh copies
and running `python3 -m unittest -v` passed for each copy during study-record
verification; the later n4 and r4 patches also applied and passed their two and
three tests respectively. This
establishes that the retained patches and tests run in the
current environment; it does not validate each actor's original timing claim.

For the historical source, run `python3 recreate-historical.py SOURCE_REPO
DESTINATION` with a destination that does not exist. The script uses the local
Git object and verifies the manifest; the retained exercise references a
temporary Python environment that may need to be recreated for another run.
The reconstruction was checked locally against all 2,998 recorded files.

## Results

The following observations distinguish an agent's executed work from whether
its evidence supports the whole request. The actor reports are their own
descriptions and can be compared with their retained patches. An additional
feasibility witness received more direct, case-specific instruction and is not
a comparison actor.

| Case | Baseline | Candidate v1 | Candidate v2 | Candidate v3 |
| --- | --- | --- | --- | --- |
| Derived receiver | r1 implemented and tested bounded unknown-start and offset acquisition with bit decisions. | r2 independently implemented and tested a similar bounded receive path. | r3 independently implemented and tested a bounded acquisition and decoding path. | r4 implemented and tested a bounded receiver; a 20-seed probe recovered 19 weak-case messages. |
| Feed transfer | t1 benchmarked parsing, validation, SQLite inserts and commits. | t2 independently benchmarked the full import path. | t3 independently benchmarked the full import path. | — |
| Narrow control | n1 made the singular grammar correction and checked it. | n2 made the correction and checked it. | n3 made the correction and checked it; `git status --short` failed because the copy has no Git repository. | n4 made the correction, passed two tests and reported an additional -1000 to 1000 integer check. |
| Historical pumpModem | h1 created a fresh-list parser and explicit unsupported case records, but did not simulate the requested case-level receiver. | — | h2 built the native exporter, ran a plan-only geometry check and reported nominal link-budget arithmetic, but did not simulate the requested case-level receiver. | h3 independently tested the existing Helper-off receiver branch and reported its unresolved early exit; it also ran native planning. |

The derived-receiver implementations are short, deterministic simulations and
none demonstrated saturated whole-machine throughput. r4's machine-wide scaling
estimates are unverified assumptions. Their real-time estimates
and workspace figures are limited to their stated assumptions and are affected
by concurrent runs. In particular, r1's statement that no work remained is too
broad for the requested saturated capacity and recovery claims; r2 labels a
wall-clock reciprocal as a CPU ceiling. The fresh-agent controls also initiated
the relevant implementation in these cases, so these pairs do not demonstrate
an improvement attributable to either candidate wording. All three feed runs
similarly exercised the omitted import stages; their tmpfs measurements are not
evidence of durable-disk production capacity. None of the narrow runs showed
gratuitous expansion.

h1's measurements covered isolated abbreviated kernels; all nine listed cases
were recorded as unsupported and the requested case-specific metrics remained
null. Its reported five new parser tests and eight abbreviated-harness tests
passed; the native CMake build and CTest registration were unrun. Its guide
proposes aggregate CPU seconds per input second, which does not match the
original request's wall-time-at-high-thread-utilization metric for a multicore
workload. h2 initially failed its native build because the compiler cache was
read-only, then built the exporter with caching disabled; it reports both
focused CTest suites passed. Its native plan does not generate samples or
templates and is not a receiver-capacity measurement. An independent check
found the nominal C/N0 arithmetic consistent with the exporter's assumptions.
In the initial phase, all three actors identified an integrated receiver gap,
but none implemented a case adapter or higher-fidelity case simulation. h2's more grounded native
planning is an observed difference in one exploratory pair, not causal proof
of a prompt improvement. h3's additional small diagnostic fed zeros into an
existing synthetic fixture and independently reproduced an unresolved
`helper_acquisition_unresolved` / `helper_disabled` result before DATA scoring.
This demonstrates the existing early-exit behavior, not signal detection or
the impossibility of Helper-free reception. It explicitly did not report the
early-exit timing as receiver throughput. h3's first native build similarly
failed on a read-only compiler cache and succeeded after disabling that cache.

The `h1.patch`, `h2.patch` and `h3.patch` files were applied to separately
reconstructed historical inputs; their focused Python tests passed (5 and 8
for h1, 4 and 8 for h2, and 2, 8 and 12 for h3). Generated builds, caches and
local-evidence outputs were not retained in the patches, including h2's locally
reported raw timing evidence. The
historical case uses a selective snapshot and a bounded time
window, so it cannot establish what would happen on the live project or after a
full task campaign.

The separately directed [feasibility witness](witness/README.md) ran actual
native source/channel samples and native templates through the existing
FFTScreen for two bits in flat and HF-worst diagnostic conditions. This was a
small, truth-narrowed acquisition slice with no complete receiver, statistical
qualification or saturated throughput measurement. Its retained report
records an initial failed CMake configuration, the subsequent successful build,
and the mismatch between the HF-worst margined descriptor and the raw list
values. An independent reviewer reproduced all four diagnostic runs. This
establishes a feasible bounded action under the witness's more direct
instruction; it does not turn the generic-prompt actors into successes or
establish prompt causality.

## Historical continuations

After the initial bounded runs, h1 and h3 each received the same neutral
instruction and approximately eight more minutes, without the witness method or
results. The original reports and patches remain unchanged. The
[continuation protocol](freeze/continuation-protocol.md) records the exact
instruction and evaluation limits. These are continuations of agents with
different prior work and context, not a fresh randomized comparison.

h1 added conditional nominal link budgets and checked them against the native
planner; the nine configurations remained unsupported for simulation. It
reported an initial CMake configuration failure with both GUI and CLI disabled,
then a read-only compiler-cache build failure; enabling CLI and disabling the
cache allowed the targeted build and two CTest entries to pass. Those budget
calculations are not sampled receiver performance. Its continuation repeats
the process-CPU metric wording that does not by itself establish the original
whole-machine wall-time-at-high-utilization metric.

h3 added an explicitly Helper-free acquisition branch and reported correct
selection of both bits in a small noiseless synthetic one-ray test. Its first
diagnostic placed the waveform at the wrong calendar offset and misclassified
bit 1; after correction to include the capture lead, both bits were selected.
It also ran a bounded acquisition-screen timing slice using native DATA basis
and a synthetic proxy channel. The retained 0.1428 CPU-second estimate covers a
single screen on a repeated three-second capture, not complete-receiver or
saturated whole-machine throughput; the screen's workspace forecast is not a
measured system workspace margin. The exact probe is part of
`actors/h3.continuation.patch`; the reproduced `local-evidence/probe-hf.py`
has SHA-256 `a71ea17fee17f07265824722eaa3d02f0445ae6bee3d488ad93f177822ee51c1`.
These results demonstrate direct incremental work, with substantial case
mapping, full reception, statistical qualification and capacity work still
unresolved. They do not establish a causal effect of the prompt wording.

To reproduce the continuation source states, first reconstruct separate copies
of the historical input, apply `actors/h1.patch` or `actors/h3.patch`, then
apply that actor's corresponding `*.continuation.patch` with `patch -p1`.
Both sequences were applied to separate reconstructed copies. Focused Python
tests passed on the resulting h1 copy (6 and 8) and h3 copy (14, 8, 2 and 17).
The original actor reports describe their own CTest and timing runs; those
runs were not repeated during patch verification. Native build products and
temporary outputs are excluded, while the h3 probe source is retained.
