# Illustrative strategic routing and token estimates

> **Current cost context (user-reported, 2026-10-28):** GPT-6.1 Sol in Desktop Codex was reported to consume included weekly allowance at about five times its previous Sol usage rate. The user-provided unitless planning index is Terra = 1, Sol ≈ 10, Astra ≈ 20, and Luna = 0.1. These estimates are not verified or calibrated to actual comparable workloads or weekly allowance use, and are not API/token or purchased-credit rates, USD amounts, or weekly usage percentages. The [official plan-pricing page](https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual) explains that credit prices alone do not determine included subscription usage. See the [weekly-usage cost guidance](../policy.md#weekly-usage-cost); this context does not revise historical measurements or conclusions, or change routing, role pins, tiers, or controller behavior.

This document was written by an explicitly requested Terra subagent. Terra is
the configured role identity reported for this task, not independently verified
with the model provider. These are proposed, hypothetical runs, not observed
model usage or claims that a project defect exists. They assume the task authorizes the model mix and all
work, the selected primary is Terra, and the existing pinned roles, project
contracts, permissions, service tier, and concurrency ceiling remain in force.
If the runtime cannot supply an authorized role, report the limit and do not
silently change a pin, tier, account, or permission. Terra coordinates and keeps
the overall outcome; Sol or stronger reviews every high-level architecture
decision, and independent review is required for worker patches. Astra gives
frequent bounded reviews of the alternatives and consequential written code;
it is not a substitute for acceptance or for verification.

Ask the user early for a decision that controls the architecture or acceptance
criteria. A late question that does not gate acceptance should be reported while
independent authorized work continues. If the evidence shows that the current
approach is fundamentally unsuitable, stop optimizing its local details and
present a redesign for review; a model's assertion alone is not evidence.
Escalate a stalled or diminishing-return investigation to a bounded Sol/Astra
review with the original evidence, alternatives, and decision needed. Retain
original failures, scoped ownership, deadlines, and any repair already used.

## What is observed and what remains proposed

The allocations and token budgets below are hypothetical; neither scenario was
executed as described. Their Astra shares of estimated API cost are 69.55% and
57.35%, respectively. Those figures are arithmetic on assumed API budgets, not
observed usage or weekly subscription allowance shares. They do not establish a
cost advantage for any routing approach.

Separate, small live Luna exercises tested parts of the controller workflow.
One engineering fixture used six successful Luna-medium sessions: four scouts,
one worker, and one independent reviewer. It preserved initial setup and schema
failures, demonstrated a correction and review, and is not a mixed-model cost
benchmark. See the [engineering evidence](engineering.md) and
[operator report](engineering-main-report.md). The earlier
[Astra installation record](astra-installation.json) explicitly says live Astra
execution was not tested. The current kit-improvement work has used native Luna
scouts, Terra screening and bounded Sol review through native subagent tools,
rather than a controller run. That observed workflow is not a controlled workload
or cost comparison; model-attributed weekly-allowance telemetry is unavailable.

| Evidence | What actually ran | What it does not establish |
| --- | --- | --- |
| [Initial live integration](live-agent.json) | Three completed Luna-medium controller/app-server sessions; 21,004 input and 33 output tokens, zero cached input; interrupted usage missing | A realistic project campaign or mixed-model savings |
| [Engineering fixture](engineering.md) | Four scouts, one worker and one reviewer; actual bounded fixture correction and review | Broad software quality or quota savings |
| [Swarm result](swarm-main-final-status.json) | Two completed diagnostic probes, one inconclusive cutoff | Completed patch acceptance or full coverage |
| [Scheduling benchmark](benchmark.json) | Deterministic simulation with matched simulated resources | Live model performance or allowance use |

These records show the kit's actual controller, dispatch and acceptance paths
were exercised within their recorded configured/resolved permissions. Separate
app-server sessions are not native children of the main desktop chat. Some
historical setup required an explicitly authorized launcher after a setup failure;
that does not authorize broader execution in a future session. Neither receipts
nor prompts prove universal service-policy compliance, exhaustive tool isolation
or provider-authenticated model identity. Native subagents have the parent turn's
permission boundary; role instructions do not create a separate sandbox.

For future authorized work, proactively look for distinct useful Luna evidence
and experiments, with an aspirational target of at least ten times the previous
allocation of *useful eligible investigation*. First define the prior baseline
and the unit counted; an agent, call, token, or page of output is not itself a
useful finding. Terra can screen relevant Luna results for source support,
contradictions, omissions and decision relevance, then supply focused evidence
and direct references to experts. Review the original requirements and decisive
sources directly. A consequential strategic trigger can go immediately to
Astra, and required architectural review precedes substantial dependent work;
neither waits for a mandatory screening step or a long scout sequence. See the
[evidence discovery and Terra screening guidance](../policy.md#evidence-discovery-and-terra-screening).

Compare a few representative, matched tasks against a specified previous
allocation, including consequential architecture and sequential tasks. Retain
the same acceptance criteria and assess useful accepted findings, missed or
contrary evidence, strategic alternatives, corrections and rework, completion
time, and total usage across all involved models and review stages. Record
input, cached-input subset and output where available without summing repeated
cumulative samples; report missing observations. A meaningful comparison of
weekly allowance also needs sufficiently isolated or otherwise attributable
per-model observations. The current Luna planning factor is 0.1, but it is not
calibrated to those observations, so the aspiration for Luna to account for at
least half of weekly usage cost is not established.
Do not spend allowance simply to achieve that share, and do not convert API
prices or token counts into weekly allowance.

Research provides reasons to test, not proof that this allocation works here.
[FrugalGPT](https://arxiv.org/abs/2305.05176) studies learned model cascades on
particular tasks, while [Lost in the Middle](https://arxiv.org/abs/2307.03172)
finds position-sensitive retrieval on two long-context tasks. Neither evaluates
this kit or establishes that additional scouting will save cost or improve
current models' results.

## Cost method

The following are planning scenarios using the [OpenAI API pricing page](https://developers.openai.com/api/docs/pricing)
and [model catalog](https://developers.openai.com/api/docs/models), accessed
2026-10-28. Standard, short-context prices in USD per million tokens are:

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| gpt-6-luna | $0.10 | $0.01 | $0.50 |
| gpt-6.1-terra | $1.00 | $0.05 | $5.00 |
| gpt-6.1-sol | $2.00 | $0.10 | $10.00 |
| gpt-6-astra | $10.00 | $1.00 | $50.00 |

Standard is a comparison assumption, not the account's actual billing or
permission to change inference tier; the actual service tier stays unchanged.
The cached-token budgets are assumptions about eligible cache hits, not automatic
cross-model reuse of scout context. Cached tokens are a subset of input:
`cost = ((input - cached) * input_rate + cached * cached_rate + output * output_rate) / 1,000,000`.
Counts below include prompts, tool-result context, response and hidden reasoning
output, coordination, bounded review, and a modest repair reserve. They are
illustrative budgets, not measurements or guarantees; actual output includes
hidden reasoning billed as output, and cache hits are uncertain. Extended cache
writes may cost extra. Long-context pricing, other tiers, regional uplifts,
model/tool fees, compute, storage, human time, retries beyond the reserve, and
subscription or account-specific billing are excluded. Treat each request's
context length separately; aggregate input across jobs does not establish that a
request qualifies for short-context pricing. Reprice using actual per-model usage
and actual cache/read/write and rate conditions before making a cost claim.

## User-reported weekly allowance context

On 2026-10-28, the user reported that GPT-6.1 Sol Desktop Codex included weekly
allowance usage had recently increased by about five times versus its prior
usage. The following are rough, unverified, unitless relative estimates—not
token prices, USD, purchased-credit rates, or weekly usage percentages:

| Model | Relative weekly-usage estimate |
| --- | ---: |
| GPT-6.1 Terra | 1 |
| GPT-6.1 Sol | ≈10 |
| GPT-6 Astra | ≈20 |
| GPT-6 Luna | 0.1 |

The index supplies a Luna planning factor, but it does not calibrate a campaign's
weekly allowance use. The token budgets and API USD calculations below cannot be
converted into weekly usage totals: actual comparable workload measurements
and attributable weekly allowance observations are unavailable.
The API pricing table above remains a separate API-price scenario. The [official
plan-pricing page](https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual)
explains that credit prices alone do not determine included subscription usage;
workload, context, reasoning, tools, and caching affect usage. See the
[weekly-usage cost guidance](../policy.md#weekly-usage-cost).

## pumpModem: helper-carrier acquisition and precision

The read-only reference was `unbundled-home/___quick/p/_cur/dataPump/pumpModem`
at `dae58eaccfd68cbf2366b85fd746b56fde089cd3`, with pre-existing dirty files;
no new tests were run for this example. The dirty paths at inspection were
`docs/helper-carrier.md`, `docs/validation.md`, `src/live_helper_presence.hpp`,
`src/signal_view.cpp`, `src/signal_view.hpp`,
`tests/test_live_helper_presence.cpp`, and `tests/test_signal_view.cpp`.
The local cold-pull-in evidence reports
a synthetic FFT seed 1.258 Hz off the 2092.5 Hz tone, outside the fine
innovation gate, delaying admission 7.525 s. Widening the local gate also
qualified a 5.55 Hz error against a 4.49 Hz interval. The recorded redesign
allows four consistent adjacent unqualified fine observations to recenter the
NCO without granting sync, discards the old/new bridge, and preserves later
qualification (`local-evidence/helper-v13/cold-pullin-r2/README.md`). Synthetic
results do not establish cable or OS capture behavior.

Precision evidence reports an ideal forecast of 0.06046 Hz versus measured
metadata uncertainty 0.5662 Hz at nominal 30.02 dB-Hz, with 0.1546 Hz CW;
the admitted phase-window and metadata residuals matter. A GLS experiment
improved some strong cases but failed its weak-EME guard and was not integrated
(`local-evidence/helper-v14/tone-precision/README.md` and
`local-evidence/helper-v14/gls-precision/README.md`). The live contract in
`docs/helper-carrier.md` requires real capture geometry and phase reacquisition
after retune; frequency support must not invent phase or advance the payload
frontier. Do not remove guards or substitute expected SNR for measured data.

A hypothetical routing packet:

1. Terra asks early for any required acquisition/precision acceptance criteria
   and representative hardware constraints. Luna scouts can independently
   investigate the tracker/gates, recorded precision experiments, current test
   and capture evidence, and relevant primary sources. Terra screens their
   concise packets for contradictions and gaps; the packets cite paths and
   distinguish measured, synthetic, unrun, and unknown results. A strategic
   trigger can reach Astra immediately, without waiting for these investigations.
2. Sol reviews the acquisition and measurement architecture and tradeoffs;
   Astra reviews the alternative designs and the consequences of changing the
   qualification gate. If evidence rejects the existing architecture, request
   a redesign rather than continuing a local gate adjustment. A nonblocking
   late question about presentation can be reported without stopping unrelated
   checks.
3. Three bounded Luna workers can prepare independent regression assignments
   for tone estimation, cold pull-in, and retune/loss/phase behavior, each with
   a distinct owned path and original acceptance checks. Shared tracker changes
   and integration stay with the strong owner. `CMakeLists.txt` registers
   `test_helper_tone_tracker`, `test_helper_cold_input_stage`,
   `test_helper_pilot_phase`, and `test_helper_phase_continuity`; exact commands
   and runnable environment need verification in the actual run. Astra reviews
   consequential code at integration, and a separate authorized reviewer
   reviews worker patches. Escalate an evidence-backed stall rather than
   repeatedly changing tolerances. Reserve one bounded repair where warranted.
4. Preserve the failing baseline and the precision guards; report synthetic
   tests, real-RF transfer and manual radio/display qualification separately.
   No model review turns an unrun capture or hardware qualification into a pass.

The illustrative allocation is one Terra coordinator, six Luna agents (three
scouts and three test workers), two distinct Sol agents (a reused architecture
owner and an independent patch reviewer), and one Astra agent consulted at two
bounded checkpoints. The Sol owner may have multiple turns; the reviewer is
independent of patch authors. The estimates cover their aggregate turns and a
repair reserve, not a promise of fixed usage.

One illustrative aggregate budget, in thousands of tokens, includes these
packets, two bounded Astra checkpoints, integration/review and repair reserve:

| Model | Input | Cached subset | Output | Estimated USD |
| --- | ---: | ---: | ---: | ---: |
| Luna | 360 | 120 | 80 | $0.0652 |
| Terra | 120 | 30 | 25 | $0.2165 |
| Sol | 100 | 20 | 20 | $0.3620 |
| Astra | 90 | 20 | 15 | $1.4700 |
| Total | 670 | 190 | 140 | **$2.1137** |

## software-foundation: receipt trust boundary and a wide regression campaign

The read-only reference was
`unbundled-home/___quick/p/_cur/dataPump/_lessonsLearned/software-foundation`
at `4c471cb93702cdc03b5230bfa33372355424b665`, clean when inspected. Its
current project instructions park the appended implementation. This is a
hypothetical *future authorized* campaign, not a request to resume that work;
no project edit, build, CI run, or test was performed here.

The passive converter in `tools/appended_foundation_receipt.py` checks and
joins original stream, native-runtime acceptance, construction/readback,
bootstrap, exact artifacts/assets, and producer receipts. It snapshots and
rechecks inputs and uses exclusive output creation. Conversion cannot establish
that runtime execution occurred merely by issuing a receipt. The project
documents the converter as partial, untested, and unregistered; the registered
contract suite is not a converter test. No converter-specific test file was
found. A prior release-feedback run is historical, and its exact failure output
was not retrieved; it is not evidence of a current failure.

With authorization and a settled test contract, Terra could route a large
campaign as follows:

1. Luna scouts can investigate the converter and its contract, consumer, packaging,
   existing validation, and relevant primary sources in distinct slices. Terra
   screens compact evidence and supplies references and unresolved questions.
   Sol owns the trust-boundary
   decision and reviews what constitutes an admissible receipt; Astra
   independently challenges the brainstorming, including what passive evidence
   cannot prove. Ask the human early if runtime proof or scope is genuinely
   ambiguous; keep the parked work parked until authorized.
2. Prepare up to 24 bounded, independent Luna regression jobs in four batches
   of six: strict JSON/schema/types; stream/seal and physical identity joins
   including mutation and alias cases; bootstrap call/result/order and worker
   joins; and artifacts/assets/producer receipt bindings plus CLI side effects.
   Each job receives a unique case or fixture and reports the exact baseline,
   command, result, and patch if authorized. These are proposed partitions,
   not claims that 24 valid distinct cases already exist: the strong owner
   determines actual cases and coverage before dispatch. Group overlapping
   fixtures under clear ownership, and do not dispatch contradictory writers.
3. Sol reviews every high-level architecture decision and a separate
   authorized reviewer examines worker patches. Astra checks consequential
   written code and the integrated trust-boundary argument at a second bounded
   checkpoint. On diminishing returns, present an evidence-backed decision to
   Sol/Astra; redesign a demonstrably unsound trust model rather than patching
   around its symptoms. Ask late nonblocking questions while independent work
   continues. Preserve unrun, setup-failed, and failed tests separately.

The shared build, CPU, memory, writable fixtures, actual concurrency ceiling,
review capacity, and dependent tests can constrain simultaneous execution.
Twenty-four jobs do not imply twenty-four concurrent processes or linear
wall-time speedup. A usable report states accepted coverage and remaining gaps.

The illustrative allocation is one Terra coordinator, four Luna scout agents,
up to 24 Luna worker agents for distinct test jobs, two distinct Sol agents
(the reused architecture owner and an independent patch reviewer), and one
Astra agent consulted at two bounded checkpoints. The owner may have multiple
turns, and worker jobs may be staged or reduced when the cases or available
resources do not justify all 24. The reviewer is independent of patch authors.

One illustrative aggregate budget, in thousands of tokens, covers the four
scouts, up to 24 small test jobs, Terra coordination, Sol architecture and
independent review, two Astra checkpoints, and modest wrapper/repair reserve:

| Model | Input | Cached subset | Output | Estimated USD |
| --- | ---: | ---: | ---: | ---: |
| Luna | 2,000 | 600 | 350 | $0.3210 |
| Terra | 220 | 70 | 40 | $0.3535 |
| Sol | 150 | 30 | 25 | $0.4930 |
| Astra | 100 | 20 | 15 | $1.5700 |
| Total | 2,470 | 720 | 430 | **$2.7375** |

With the same total input and output but no cached input, the illustrative
standard short-context totals become $2.3710 for pumpModem and $3.0950 for
software-foundation. This sensitivity changes only the assumed cache hits; it
does not change the actual service tier.

These examples are point scenarios, not a predicted range or measured
savings. For a simple sensitivity range, if every input, cached input, and
output count in either scenario is halved or doubled at the same rates, the
pump example is about $1.06–$4.23 and the foundation example about
$1.37–$5.48. Real changes in context, repair, cache and reasoning need not
scale proportionally. Compare actual total usage and accepted outcomes against
a separately measured baseline; no baseline or observed usage is available
here.
