# Delegation controller acceptance exercise

> **Current cost context (user-reported, 2026-10-28):** GPT-6.1 Sol in Desktop Codex was reported to consume included weekly allowance at about five times its previous Sol usage rate. The user-provided unitless planning index is Terra = 1, Sol ≈ 10, Astra ≈ 20, and Luna = 0.1. These estimates are not verified or calibrated to actual comparable workloads or weekly allowance use, and are not API/token or purchased-credit rates, USD amounts, or weekly usage percentages. The [official plan-pricing page](https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual) explains that credit prices alone do not determine included subscription usage. See the [weekly-usage cost guidance](../policy.md#weekly-usage-cost); this context does not revise historical measurements or conclusions, or change routing, role pins, tiers, or controller behavior.

Current Luna evidence-discovery guidance is summarized in the [policy](../policy.md#evidence-discovery-and-terra-screening); it does not change these historical results.

**Verified final state: stopped, 4/4 original tasks complete, independent review accepted, zero active work.** The delivery process corrected this heading and the successful-session count from the durable state; the original main-authored narrative remains at `unbundled-runtime/run-h477d4d60251ff030/report.md`. Original setup and format failures remain in the records.

## Run settings and runtime verification

Run ID `luna-medium-acceptance`; original requested settings remained gpt-6-luna / medium / default tier, engineering backend, workspace-write, approval never, network disabled, 4 reasoning / 4 processes / 4 CPU / 4096 MB, 240-second task timeouts, 900-second run deadline and 1500-second active budget. All six successful worker/reviewer sessions verified Luna medium/default, approval never, a `local` environment with the exact private workspace roots, and network-disabled workspace-write. The main chat's service tier is not exposed by available telemetry. Source hashes before and after are identical: `totals.py` `7eaedc46536ed878311cd976f85877e0b2f7792fc5b3c64601de1cbff555d300`; `test_totals.py` `745ec14ec8368fafd39f184f5db6905e963cc7a399b7b9b4f24841043988d339`.

## Setup failures and recovery

Initial first attempts for parser, reducer and repeatability failed before inference with read-only PATH alias creation and released with exit 1. Those failures remain in their original attempt history. The supplied explicit-local probe verified the runtime correction. The stopped run was migrated to the reviewed frozen runtime and each exact hold was resolved with its same operation ID, receipt/stderr, and current audited private-copy digest; no task identity or budget was reset.

A Python `subprocess.Popen` wrapper owned controller PID 294461. It was terminated with `Popen.terminate()` while parser, reducer and repeatability second attempts were active; no worker groups were signaled. Recovery controller PID 296696 reconciled those same attempts, ingested parser/reducer results, and retained the active slow attempt without duplicate dispatch. The slow result completed later.

## Diagnostic evidence and intervention

The parser experiment rejected the parser hypothesis: actual parsed values matched the matched expectations. The reducer wrapper compiled under its declared `scratch/` scope and ran against actual `totals.py`: `[2,3]` reduced to 3 vs 5, `[7]` to 0 vs 7, empty to 0, and `total("2,3")` to 3 vs 5. The worker labeled this `observed`; that original label is retained. After inspecting its immutable command evidence, the documented `assess` interface added separate `failure_reproduced` evidence bound to the same attempt, inputs and command log, without rewriting the scout outcome.

The original slow repeatability branch performed exactly one 60-second sleep and returned 3 for `total("2,3")` before and after; `total("-4,9,-2")` returned 7 vs expected 3. Earlier fast parser/reducer results were ingested while that slow task was still active. The correction waited for explicit operator interpretation because the reducer's original label was `observed`, not because the slow task blocked it.

A new, distinct `counterfactual-diagnostic` follow-up was submitted while paused. Its candidate copy changed only the reducer expression under `scratch/`, compiled there, and compared all five original unit-test inputs. Baseline mismatched four cases; candidate matched all five. It performed exactly one 45-second delay. After assessment and explicit resume, the controller automatically dispatched the original correction and this follow-up concurrently; the follow-up did not block the correction or reviewer path. The follow-up completed as `failure_reproduced`.

## Correction, tests, and review

The first correction worker attempt (`correct-total-1-2288894efa32`) changed only its private `totals.py` copy from `sum(values[1:])` to `sum(values)`. Its actual `python3 -B -m unittest -v` command exited 0 with all six unchanged tests passing. The controller initially rejected its returned packet because `commands` were objects rather than strings. That schema failure is preserved in the original result and history; no model rerun or patch reexecution occurred.

After the reviewed receipt-normalization runtime was migrated while paused, `continue --task correct-total` revalidated the retained original report using actual command receipts; it did not rerun the model or reexecute the patch. It created the independent review stage. Reviewer task `correct-total.review.1` inspected the retained patch and checks, independently ran the unchanged unittest command successfully, and completed with verdict `accept`; controller status records `validated`. Thus the original correction is passed after actual independent review. The initial `commands` object/string schema error remains in report validation history and is not erased. The reviewer wrote one scratch lock file inside its declared private scratch; no production file was changed.

The final CLI stop is persisted. Final report: run stopped, all tasks terminal, zero active work, 4/4 original tasks completed (with the additional counterfactual follow-up also complete). Source hashes were reported unchanged during the original run, before publication.

## Evidence files

- `events.json` and `event-timings.json`: full event timeline, attempt/operation/thread IDs, settings and controller identities.
- `requested-observed.json`: requested/observed policy, task states, budgets and source hashes.
- `correct-total-result.json`: retained worker report, initial schema failure and independent review history.
- `counterfactual-result.json`: follow-up diagnostic result.
- `final-status.json`: final controller report.
