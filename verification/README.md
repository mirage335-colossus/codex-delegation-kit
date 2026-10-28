# Validation and delivery record

> **Portable publication edition.** The records below are sanitized historical representations. Machine coordinates and service identifiers have been removed; reported results and failures remain historical claims. Original hashes, byte counts and validation totals do not validate the rewritten files. Use the [reproduction guide](REPRODUCING.md), [public source metadata](reproduction.json), and current `publication-manifest.json` for a fresh offline check. No private conversation, home directory, temporary build, or original session log is required. See the [portability validation record](portability-validation.json) for the migration audit and relocated-copy check scope.

> **Current cost context (user-reported, 2026-10-28):** GPT-6.1 Sol in Desktop Codex was reported to consume included weekly allowance at about five times its previous Sol usage rate. The user-provided unitless planning index is Terra = 1, Sol ≈ 10, Astra ≈ 20, and Luna = 0.1. These estimates are not verified or calibrated to actual comparable workloads or weekly allowance use, and are not API/token or purchased-credit rates, USD amounts, or weekly usage percentages. The [official plan-pricing page](https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual) explains that credit prices alone do not determine included subscription usage. See the [weekly-usage cost guidance](../policy.md#weekly-usage-cost); this context does not revise historical measurements or conclusions, or change routing, role pins, tiers, or controller behavior.

Current Luna evidence-discovery guidance is summarized in the [policy](../policy.md#evidence-discovery-and-terra-screening); it does not change these historical results.

The canonical current index is Luna = 0.1, Terra = 1, Sol ≈ 10, Astra ≈ 20 in [weekly-usage cost guidance](../policy.md#weekly-usage-cost). Frozen nested study inputs, reports, source-before records and locks retain the earlier unknown-Luna factor as historical evidence, not current guidance.

This is the historical first-controller delivery. See [the engineering extension record](engineering.md) for current engineering-backend, actual Luna-medium main-chat, recovery, and installation validation.

Validated on October 20, 2026 (America/Chicago). Maintained source:
`https://github.com/mirage335-colossus/codex-delegation-kit.git`, checkout-relative paths. Starting revision
`9014eab8b3ed8493f32c5e0c21c82c84c444c01c` was clean. This delivery is an uncommitted
working-tree change; no commit, push, publication or unrelated workload was
performed. Runtime hashes used by the live test are in `live-agent.json`.

## What was exercised

| Evidence class | Observed result | Scope |
| --- | --- | --- |
| Deterministic and controlled-process suite | 138 tests passed in 33.610 seconds on the delivered revision | Existing historical reducer and installer tests plus scheduling, process ownership, controller and synthetic protocol checks; see `tests.txt` |
| Real subprocess demo | Five original tasks complete: four passes and one intentionally demonstrated failure | Automatic dependencies and replenishment; no model calls |
| Native operator exercise, explicitly configured Luna medium | Correctly ran the demo, interpreted the failure, paused, recovered while still paused, explicitly resumed, retained completed attempts | The operator did not keep a manual scheduling ledger; this is one small exercise, not a general capability benchmark |
| Real model integration | All eleven acceptance checks passed | Actual app-server dispatch, observation, result ingestion, replenishment, controller crash/recovery, no duplicate attempts, protocol interruption, persistent stop, released execution and no cancellation-as-pass |

The model fixture completed three original diagnosis/result tasks in **17.583
seconds**, with two allocated reasoning slots. The dependent task's dispatch delay
after prerequisite acceptance was **0.00154 seconds**. These are a single small
run, not throughput guarantees. It killed only its owned controller while a model
turn was active, then recovered the original attempts. A separate fourth turn
was interrupted and not accepted. Both runs ended stopped with zero reservations.

For every live thread, app-server reported model `gpt-6-luna`, reasoning effort
`medium`, service tier `default`, read-only sandbox, disabled worker network,
`approvalPolicy=never`, and no environment access. These are resolved runtime
settings, not provider-side per-token identity. Three completed calls reported
21,004 input tokens and 33 output tokens in total, with zero cached input.
Interrupted-call usage was unavailable; no total cost claim is made.

The live calls used an explicitly approved runtime launcher because ordinary
the original restricted execution environment could not write runtime state. This launcher admitted
only the read-only agent fixture. It is **not** evidence that arbitrary subprocess
jobs inherit the operator's sandbox when launched outside it. No global model,
effort, role, tier, provider or account setting was changed. The first live setup
attempt exposed an MCP override-encoding defect before inference; its failure
remains in `live-setup-failure.json`, with the repair and subsequent evidence
separate. No denial was answered by model/account/backend substitution.

## Matched scheduling simulation

Targets were fixed in `examples/benchmark.py` before measuring: identical finite
inventory completed, fast-sweep early outcomes at least both baselines, adaptive
makespan at most 1.6 times FIFO, bounded interruptions. All five fixtures passed.
Full timelines, dispatch delay, idle slot time, setup, interruption waste, and
measured Python policy overhead are in `benchmark.json`.

| Fixture | Early useful outcomes: adaptive / FIFO / batch | Makespan seconds: adaptive / FIFO / batch |
| --- | --- | --- |
| Fast sweep | 6 / 0 / 0 | 27.08 / 26.08 / 28.08 |
| Newly arriving fast work | 5 / 0 / 0 | 56.12 / 50.12 / 50.12 |
| Nonpreemptible work with setup | 2 / 1 / 1 | 25.02 / 25.02 / 31.08 |
| Poor estimates and unknown work | 1 / 2 / 2 | 22.06 / 23.06 / 23.06 |

The early-result regression with poor estimates is preserved. Fast-arrival
preemption sacrifices four seconds of service plus two seconds of restart cost.
The policy improves early delivery in that case at a total-completion cost. Under
continuing auxiliary arrivals, the original expensive task receives service at
30.6 seconds. This is explainable heuristic scheduling, not global optimality.

## Review and deliberate bounds

Independent review found and prompted fixes for adapter field/log mismatches,
stale and transitive evidence, stop with no live controller, a stop/launch race,
budget propagation, optional-stage failure retention, held acceptance, and stale
embedded review material. Regression tests use actual processes where relevant;
model protocol tests are labelled synthetic. A final real-process test also exposed and verified the repair of a stale-snapshot preemption bug; the full suite and live exercise were rerun on the final runtime hashes. The live test separately establishes
the supported external-agent behavior.

The delivered first controller is deliberately bounded. The broader proposed
system is **not fully implemented** in these areas:

- Capacity is declared admission per run, not a host-wide CPU/memory pressure
  controller or automatic observation of unrelated sessions. No adaptive
  host-pressure ramp-up or cross-run quota authority is claimed.
- The supported automatic model profile is supplied-context read-only reasoning.
  It is not arbitrary write-enabled engineering, a literal tool-free guarantee,
  or integration into an existing chat's native subagent tree.
- Duration feedback uses censored lower bounds, progressive quanta and aging.
  There is no cross-run historical prediction service or automatic learning from
  matched completed workloads.
- There is no safe suspension/checkpoint backend. Supported preemption is
  explicitly safe cancellation and restart. If an owned runner becomes
  unidentifiable, execution stays held rather than risking duplicate side effects.
- Reports do not claim exhaustive global resource use, unavoidable-vs-avoidable
  idle attribution, full cost accounting, or general engineering correctness from
  the tiny model fixture. Helper acceptance preserves legacy reviewer assertions;
  actual checks should be explicit process evidence and independently assessed.

These limits keep bookkeeping in a small standard-library implementation. They
are incomplete broader-spec acceptance items, not simulated evidence of support.
No controller starts on installation, and existing native-only/advisory workflows
remain available. See the main README and ORCHESTRATION.md for operating steps.

## Reproduce

From the maintained checkout:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B examples/demo.py
python3 -B examples/controller_demo.py
python3 -B examples/benchmark.py --output benchmark-output.json
python3 -B examples/live_agent.py --help
```

The live example requires an explicitly authorized runtime, exact model/effort/
tier arguments and available account access. It never silently changes them.
Installation uses `install.py` preview/apply, then manifest parity and a no-change
repeat preview. Final installation evidence is recorded in `installation.json`.
