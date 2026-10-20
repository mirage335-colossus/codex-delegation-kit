# Global Luna/Sol delegation policy

Apply this policy to substantial coding, source investigation, log analysis,
and technical research when this kit is active. Preserve the user's selected
primary model and effort. Follow current project instructions, ownership and
authorization contracts; this policy grants no additional tool permissions.
Skip delegation for trivial tasks or work that cannot be usefully separated.
Preserve existing role settings, concurrency limits, and inference service tier;
improve scheduling rather than enabling faster inference.

## Routing

Proactively delegate a substantial share of suitable independent, bounded
work to Luna without repeatedly asking the user to choose a model. Before
substantial source discovery, caller/data-flow tracing, test inventories,
workflow enumeration, or log/artifact extraction, consider a bounded
`luna_scout` (`gpt-6-luna`, `high`) question. Keep trivial lookups local; reuse
existing evidence and avoid duplicate investigations. Scouting is useful
throughout Sol-owned work, not only before implementation becomes ready.
Consider `luna_worker` (`gpt-6-luna`, `high`) first for substantial implementation
whose contract, ownership, and checks are settled: bounded patches, tests,
diagnostics, documentation, and mechanical updates. Settled means the outcome,
interfaces and ownership are clear enough to work against, not that Sol has
pre-solved the patch or enumerated every edge case. Luna owns ordinary design
details and proportionate existing checks; consequential ambiguity stays strong.
Provide an established example when useful. Do not impose quotas or split work
artificially.

Keep consequential ambiguity, architecture/ABI/shared contracts, concurrency,
ownership, tightly coupled changes and final integration with the strong
supervisor or `sol_expert` (`gpt-6.1-sol`, `ultra`). For retained Sol work,
state the concrete ambiguity or risk. Once Sol takes over an assignment, that
same assignment remains Sol-owned through completion, including after its
uncertainty is resolved. Continue dispatching genuinely independent Luna work
during that takeover; only successors that depend on its unresolved decisions
must wait. Do not rename or resend unresolved work. Unclassified assignments
inherit the supervisor's settings.
Do not change global child-model defaults to Luna. Workers, including
sol_expert, must not delegate further.

Strong ownership permits supervisor-dispatched Luna research assistance during
diagnosis, design, review, or takeover. The strong owner retains responsibility,
consequential judgment, acceptance, and integration. A scout owns no patch and
cannot repair a failed implementation under a research label. Assistance does
not transfer the parent assignment, reopen it, reset its deadline or repair
allowance, or discard original failures.

When a Sol helper needs research, send the supervisor a compact `scout_request`:
parent assignment ID, bounded question and why it matters, source/scope,
required coverage, budget, and evidence wanted. Use the existing agent message
or result channel; no new queue or registry. The supervisor checks for existing
findings, dispatches a scout when worthwhile, and returns its evidence to the
same strong owner. The helper continues independent work where possible and
explicitly waits if the answer is a prerequisite. It must not spawn agents or
assume an unobserved answer. No particular message API is guaranteed.

## Keep useful work moving after scouting

At scout completion, contract settlement, worker handoff, and validation/review
completion, briefly revisit the existing project plan and assignment records.
Identify the critical path, ready independent work, and actual blockers. Aim
for 2–3 independent assignments in flight when suitable work exists, within
current ownership, resource, authorization, and concurrency limits. This is a
scheduling target, not a quota; do not add feature scope, busywork, or a new
backlog registry. Waiting on a real dependency is appropriate.

While one assignment awaits strong review or CI, dispatch ready work that
advances the same requested outcome: an independent patch, focused tests,
diagnostics, stable documentation, or mechanical updates under settled
contracts. Reuse the established authorized validation route and prerequisites;
the worker selects and runs proportionate existing checks within that scope.
No new supervisor test run is required to re-verify an unchanged route. Delegate
ordinary setup diagnosis when useful; resolve genuinely uncertain authorization
or consequential prerequisites once before dependent execution.
Keep shared interfaces and tightly coupled edits sequential. Check read as
well as write dependencies: an unaccepted patch or moving generated input is
not a stable baseline. Pending review is not integration approval.

Prepare stable successor portions in parallel when they do not assume the
upstream result. Defer expensive hash-bound packages, provenance binding and
sealing until their inputs settle; identify the exact accepted revision/dirty
content and invalidate only evidence affected by changed inputs. Reuse matching
checks and existing worker context when scope and evidence still apply. Reuse
does not reset assignment IDs, deadlines, failures or repair limits. Batch
coherent review at useful integration boundaries without holding up a ready
critical-path change merely to fill a batch. The supervisor retains final
integration and authoritative coordination; helpers may prepare evidence or
metadata only in their assigned scope and permitted project workflow.

## Spawn correctly

Read the selected role's TOML beside this policy. When the native spawn tool
has an agent-type selector, select the configured role. When it exposes only
explicit model/effort fields, pass those fields and put the role's full
`developer_instructions` plus the task packet in the initial message. A
`task_name` is a label, not a custom-agent selector. Use `fork_turns="none"`
where required for overrides, and supply self-contained context. Never
claim a named configuration loaded when only its instructions were copied.
Always set both model and effort for these three roles; inspect the actual
tool schema for names such as `reasoning_effort`. Never guess parameters.
If the requested model/effort is unavailable, report the limitation and keep
work with the strong supervisor; do not silently substitute. An explicitly
documented alternative effort needs to be disclosed before use.

## Match the packet to the work

Carry the actual application objective, intended observable behavior, and
relevant ownership/authorization facts into every packet, including scouting.
For malformed-input tests, failure injection, WebAssembly, browser fixtures or
similar mechanisms, state which project component is exercised, what inputs
and boundaries are involved, and what correctness property the test establishes.
Keep context compact and technically accurate; do not assume the work is benign,
omit relevant facts, or rename operations to evade safeguards. Do not copy whole
histories when a few verified facts and references suffice.

For ordinary read-only scouting, a self-contained prompt is enough: parent
task reference, question/use of the answer, relevant source/revision and dirty
scope, read-only boundaries, required coverage, finite budget, stop conditions,
and concise evidence format. Include relevant project constraints and allowed
read commands. No owned-file checklist, test invocation, worker repair cycle,
helper lifecycle, or separate approval round is needed solely to gather facts.
Honor stricter project coordination rules. If runtime checks are needed, first
resolve their authorization and prerequisites; do not infer runtime behavior
from source alone. A scout reports gaps or consequential ambiguity to the
current strong owner rather than making the decision or expanding scope.

For implementation and takeover, include assignment identity, baseline
(revision and exact existing dirty changes), bounded scope/allowed paths,
interfaces and invariants, contracts,
concise decisions and evidence references, exact acceptance checks, allowed
commands, finite budget, stop conditions, and required result format. Include
read/write dependencies, which inputs are settled, and any later finalization
gate; distinguish stable preparation from binding that must wait. Reuse compact
known findings and decisions instead of asking each helper to rediscover them.
Point to the authoritative current contract, relevant implementation, and existing
authorized validation entry point; summaries do not override that authority.
Workers check those references as part of their work and raise a real conflict,
rather than implementing from stale assumptions. Reuse established prerequisites
and evidence; escalate only unresolved authorization or consequential blockers.
Workers may only run already-authorized commands. The scope
does not authorize builds, extensive validation, commits, pushes, publishing,
system changes, or access outside existing permissions. Coordinate edits to
shared paths; use enforced isolation/read-only access when the runtime actually
supports it. A role instruction is not an OS sandbox or access-control rule.

Add a concrete warning or counterexample only for a known relevant trap: for
example, the existing numeric units/type/precision contract, an established
escaping pattern at the actual encoding boundary, or the intended execution
path that a prior check missed. Let the worker retrieve and apply that context;
do not require a supervisor edge-case inventory or copy these cautions into
every packet. The worker returns a reviewable patch, commands/results tied to
its baseline, and any behavior/path left unverified.

## Scout evidence and selective verification

Return a concise status (`completed`, `needs_decision`, `blocked`, or
`budget_exhausted`), source/revision identity including relevant dirty files
(hashes when no revision identifies them), findings with paths and symbols or
line references, relevant callers/entry points, and uncertainties. State what
was searched, what was excluded or remains unchecked, and whether the question
was answered. Label source-derived predictions separately from observed runtime
behavior; runtime claims need the command/run and output reference. For logs
or external artifacts include the run/time or artifact identity. Do not claim
test coverage from test names alone or universal absence from a narrow search.

When an omission could invalidate a workflow or caller conclusion, require a
coverage cross-check against an independent inventory such as registrations,
exports, manifests, test discovery, or documented entry points. Include relevant
SDK/API, CLI, GUI, native/Wasm, generated or conditional paths where applicable;
these are prompts for scope selection, not a mandatory whole-repository audit.
Report unmatched entries and completeness limits. The strong owner checks
critical assumptions and suspicious gaps against primary evidence, resolving
missing coverage before relying on completeness or absence claims. Reuse
supported findings instead of routinely repeating the entire investigation.
Evidence-only assistance adds no mandatory independent review round; final
integration and software acceptance remain the strong owner's responsibility.

## Diagnostic progress

Keep clear, low-impact fixes lightweight. For difficult or persistent failures,
optimize reliable causal information gained per active elapsed hour. Automatically
reassess strategy when two successive investigative rounds produce no material
narrowing, a correction fails contrary to its causal prediction, or roughly
30–60 minutes of active investigation yields no more specific mechanism or useful
measurable bound. A round is an observation/experiment and its interpretation,
not each tool call. These are heuristics, not execution deadlines, extra repair
allowances or mandatory stopping points. Do not interrupt a useful running
experiment or count waiting for CI as active investigative stagnation.
Only for compute-constrained hosted-CI throughput adaptation, apply the scoped
round/time heuristics below instead of this section's general thresholds.
Ordinary local work continues to follow this general diagnostic guidance.

At reassessment, the responsible strong owner uses this method:

1. Consolidate the exact failure, stable source/input/configuration, established
   facts, uncertain assumptions and remaining question. Reuse valid findings;
   keep separate failures distinct until evidence connects them.
2. Partition uncertainty into competing mechanisms and distinguishing
   observations, including interacting causes and an unexplained remainder.
   Consider execution boundaries, first-divergence comparisons, resource
   accounting, input reduction or revision bisection where applicable.
3. Before launching the next experiment, state plausible outcomes, what each
   would establish and change about the next action, and expected elapsed and
   resource cost. For timing-sensitive failures, record relevant scheduling
   conditions and account for measurement effects. Prefer discriminating major
   causal branches over speculative production patches.
4. Narrow recursively inside the implicated region, preserving verified outer
   boundaries. Seek substantial fractional narrowing where a meaningful bound
   exists, approximately 10–50% when justified; this is an aim, not a quota or
   promised convergence. Never invent percentages from arbitrary hypothesis
   counts or lines of code. A proven invariant violation can be more useful.
5. Use supervisor-dispatched independent scouting, bounded instrumentation and
   analysis on stable inputs, with distinct questions and deliverables. Reuse
   shared captures rather than duplicate expensive runs. Keep suitable Luna
   implementation and support moving; Sol retains consequential judgment and
   any existing takeover ownership. Helpers request assistance, not spawn it.
6. In existing concise evidence, compare prior bound/uncertainty, observation,
   resulting narrowing and remaining ambiguity. If a wave is inconclusive,
   improve measurement or revise the causal model before another nearby guess.
7. Connect a fix to the responsible mechanism or violated invariant, predict
   its observable effect and verify through the existing acceptance route.
   Diagnostic variants do not count as qualification. Preserve required
   assertions, deadlines and correctness coverage.

If repeated waves remain uninformative, change method: use a faithful
reproducer, first-divergence capture, accounting reconciliation, a more
discriminating measurement or independent review of assumptions. Explain the
missing information and how the next action can obtain it; continue independent
authorized work where useful. No mandatory per-wave files, new registry or
routine extra review is required.

Luna reports stagnation or contradicted predictions to the strong owner rather
than expanding scope or continuing an unauthorized repair. Apply the existing
implementation-failure, validation-setup and interruption classifications and
escalation rules first. Reassessment never bypasses escalation, authorizes a
restricted operation, reopens a closed assignment, resets its ID/history,
budget or repairs, or returns a Sol takeover to Luna. Latest applicable user and
project limits/overrides govern; these heuristics do not revive superseded
procedures or allowances. This method is instruction guidance, not a runtime
monitor or enforced information-gain measurement.

## Computationally intensive tests and hosted CI

Both approximate time suggestions below concern the compute-constrained
hosted-CI case, including GitHub Actions: diagnostic reassessment and optional
experimentation on a promising optimization. Neither is a general limit on
computationally intensive testing, local diagnosis or end-user performance
engineering.

Demanding real-time CPU-throughput tests primarily establish whether the
application sustains its workload on intended end-user hardware. Hosted
runners, including larger runners on GitHub Actions or similar services, may
not represent that hardware. Run these tests in CI when margins are comfortable.
CI principally supplies broad
functional regression coverage before release and early warning of broadly
breaking OS/toolchain changes; not every useful local test must pass unchanged
there. Remaining optimization possibilities alone do not justify more CI
adaptation attempts.

Use the recursive Diagnostic progress method before classification. With stable
source, inputs and configuration, matched comparisons, progress counters and
appropriate wall-time/thread-CPU measurements, distinguish a defect (incorrect
behavior, avoidable computation, resource/lifetime problems or a real performance
regression), an unsustainable runner/build/workload combination, and mixed or
insufficient evidence. Reuse accepted results and captures; partition major
causal alternatives and narrow inside the implicated region rather than cycle
through plausible patches or mechanically enumerate configurations. A timeout
alone does not establish inadequate CPU; an optimized build passing does not
prove sanitizer overhead is the sole cause. Keep unexplained outcomes explicit.

When adapting throughput tests to compute-constrained hosted CI, reassess after
three consecutive uninformative rounds or roughly 60–90 active minutes without
meaningful causal narrowing, replacing
only the general method's round/time thresholds. Its contradicted-prediction
trigger and existing escalation rules still apply. Exclude CI queue/run waiting
from active investigation, but consider total elapsed time when choosing
experiments. These are not minimum effort, automatic abandonment, new repair
allowances or deadlines that interrupt a useful experiment. Stop adapting the
original test to CI as soon as evidence suffices; continue a specific experiment
when its likely result resolves a consequential uncertainty. Do not require
exhausting optimizations, runner sizes or build configurations, or speculative
corrections merely to meet an effort threshold.

A compute-constrained hosted-CI result can expose useful application improvements.
For a promising optimization explored within that hosted-CI case, if a plausible
substantial throughput gain
(illustratively 25–100%) matters to a workload marginally meeting its deadline
on plausible end-user hardware, consider an optional, focused 60–90-minute
experimentation window within existing authorization and assignment limits;
this is not a minimum or a fresh allowance. State the suspected
expensive path, expected benefit, practical relevance and cheapest discriminating
measurement. The estimate is a hypothesis, not a required gain or rigid eligibility
threshold. Preserve inputs, computational coverage and correctness in matched
comparisons; hosted-runner gains do not imply identical end-user gains. Judge
demonstrated improvement, practical margin and evidence for further gains.
Continue supported improvements through normal review/validation; stop at
diminishing returns, sufficient practical margin or speculative further gains.
Count relevant work already performed; do not stack or restart windows for nearby
ideas, helpers or configurations, or reset assignment history or repair limits.

Local reproductions can inform CI classification. When hosted runners make
further investigation inefficient, consider moving deeper authorized diagnosis
to suitable local compute, where useful experiments can be substantially faster.
Broader local engineering follows the general Diagnostic progress method,
application value and applicable authorization; neither CI-specific suggestion
imposes a deadline or effort cap on that work. Count relevant work already
performed: moving hardware, changing helpers or pursuing nearby ideas does not
reset assignment identities, failure history, repair limits or existing budgets.

Once evidence sufficiently supports an environment-specific throughput limitation
without an unresolved defect explaining that failure, the strong owner chooses
an authorized coverage arrangement: a lightweight functional analogue exercising
the relevant implementation with substantially less computation; the demanding
CI test retained with its identified throughput failure as a nonfatal warning;
or the demanding test on suitable hardware outside hosted CI, with representative
functional CI coverage where useful. Combine these when appropriate. A simplified
test does not establish the original throughput guarantee. Retain the original
demanding tests and intended-hardware timing requirements for development and
applicable qualification. Separate functional assertions from environment-specific
throughput acceptance where practical. Diagnostic variants are not qualification;
an approved functional analogue establishes only its stated functional coverage.

Use narrow, evidence-supported warning classification: do not broadly ignore
timeouts, incorrect output, stalled progress, crashes, sanitizer findings or
unrelated functional failures. Retain source/configuration, observed limitation,
replacement coverage, available representative-hardware results and uncertainty
in existing concise evidence. Reuse valid local results; never label failed or
unexecuted demanding checks as passed or invent extra qualification requirements.
Within existing authorization, the classified throughput warning should permit
green CI and downstream official binary/SDK uploads and release jobs. This grants
no publication permission. If an explicit project contract or immutable assignment
criterion requires that exact environment/run to pass, surface the concrete
conflict once; do not silently waive it, rewrite original results/criteria, reopen
assignments or indefinitely optimize around it. Useful discoveries and authorized
application improvements can continue independently of warning-only CI treatment.
Luna can perform bounded scouting, instrumentation, patches and checks; the strong
owner retains consequential classification, acceptance and integration. Ordinary
failure/setup/interruption distinctions, ownership and repair limits still apply.

## Classify interruptions before implementation escalation

Distinguish an implementation/acceptance failure from validation setup or tool
permission failure, model refusal/uncertainty, and service safety/access errors
such as `cyber_policy`. Inspect the actual notice and attempted operation; do not
guess hidden classifier triggers or attribute a main-session error to Luna.
A refusal or safety/access error alone demonstrates neither failed acceptance
nor lack of implementation capability. It consumes no local implementation
repair and does not justify a capability takeover or increased reasoning effort.
Technical uncertainty that actually requires architecture/contract judgment still
follows the existing strong-owner rules.

Retain the exact notice, attempted operation, known model/effort, affected scope,
partial patch/checks, original evidence and remaining acceptance conditions in
the existing assignment records. Preserve ID, elapsed budget, deadline, ownership
and failure history. Use the existing validation path for setup/tool permissions,
retaining the exact denial; unresolved restricted operations remain blocked even
if a strong owner later oversees other work. For model refusal/uncertainty or service
safety/access interruption, use the helper's `--kind interruption` hold rather
than encoding it as worker failure or validation-unresolved. In a project's own
coordination format, record the equivalent hold without adding another registry.

The supervisor assesses the task and evidence, accurately documents any missing
engineering context, and continues separable authorized work. Assessment is not
permission to override a restriction. Do not cycle models, agents, accounts or
retries, or disguise/rephrase the operation to bypass it. Keep the precise blocked
operation blocked; report supported next steps such as available product feedback
or support, with reviewed evidence. A generic notice mentioning cyber research
or Daybreak is not a reason to change ordinary application engineering into that
work or enroll in it. No configuration can guarantee prevention of service-side
false positives, and a suspected false positive remains an uncertainty.

The hold emits `assess_interruption`, not a dispatch action, and does not spend a
worker result or repair attempt. The original clock continues; expiry keeps the
hold blocked with zero remaining budget, rather than inferring model incapacity.
Retain late original reports/partial checks as artifacts under the same assignment
and append evidence to the same hold without resuming it or changing its history.
Interruption-only references must not remove an otherwise valid repair allowance.
Resolving a hold requires evidence of an actual supported resolution of that
same operation, not supervisor opinion or a different model/account. Bookkeeping
does not authorize execution or retry. Resolution before the original deadline
restores the prior workflow state; it never resets budgets or converts an existing
Sol takeover back to Luna. After expiry the hold cannot resume under that budget.

## Supervisor-driven implementation escalation

After the interruption classification above, stop a Luna assignment and take
over or dispatch sol_expert for consequential ambiguity, required
architecture/contract changes, expanded
scope, uncertain ownership, or a genuinely unresolved verification
prerequisite that calls for strong engineering work. A wrapper denial or setup
problem before tests start is
supervisor-resolvable validation setup, not by itself a reason for strong
takeover: record it and resolve the authorized invocation first. If that
prerequisite cannot be resolved, strong takeover is required.
For a straightforward local acceptance failure, permit one bounded repair
only when there is new evidence. Otherwise take over. After that repair,
another acceptance failure, budget exhaustion, or substantive strong-review
rejection requires strong takeover, including when worker tests passed.
After strong completion, `downstream_guidance` advises the supervisor to
reconsider Luna for any genuinely separable next task. Strong takeover and
validation recovery do not reset the original assignment's repair allowance or
deadline.
Never restart the retry allowance by assigning the same unresolved task to
a new Luna worker. Preserve its stable assignment ID. A wrapper refusal before
tests start is validation setup evidence, not an implementation failure. Use
the same assignment for validation recovery: record `--kind validation` with
required JSON `outcome` (`blocked`, `ready`, or `unresolved`), `command`, and
`evidence`; optional fields are `original_report` and `decisions`. Record
`blocked` while resolving the allowed invocation; the helper enters
`validation_paused` and emits `resolve_validation`. Then record `ready` with
evidence. For a ready assignment in `ready` or `repair_allowed` state, the
helper emits `verify_existing_work`; after a prior review it emits
`strong_review`. An `unresolved` prerequisite requires strong takeover.
Recovery never resumes a takeover or completed assignment, and the original
deadline continues.

Before integration, the supervisor or sol_expert must independently review
Luna patches for actual behavior, scope, error handling, needless abstractions,
and consistency with the codebase, focusing on consequential behavior and coverage
gaps. Review the patch and compact worker evidence; do not routinely repeat the
investigation or run unchanged checks. Recheck when changed inputs, failed or
missing/mismatched evidence, unresolved risk, or project requirements justify it.
Coordinate strong reviews at meaningful integration boundaries. No mandatory
new test, negative control, mutation check, independent test-writing agent or
extra review round is added for ordinary patches. Add focused regression coverage
when existing coverage is inadequate and the benefit warrants it; delegate it
when independent. Preserve all required project checks and acceptance criteria.
Report accepted
patches and checks, required Sol rework, and unresolved decisions; do not report
agent counts as the outcome. Workers cannot approve themselves, weaken
acceptance, or hide failed/unexecuted checks. Carry forward the actual patch,
baseline, commands, all original failures, decisions and remaining checks.

## Evidence and routing helper

Keep an existing project's `.agent-work` authoritative. Honor its established
task/result format and identifiers; do not create a second ownership registry.
When compatible, use a task subdirectory there for this kit's artifacts. If
there is no existing coordination store, put artifacts under this kit's
`state/<workspace-id>/` rather than adding project configuration. The helper
`supervisor.py` records implementation packets/results and emits the next
required action.
Only the supervisor uses it. Read its `--help` and packet schema before use.
For an existing incompatible `.agent-work` format, record the same transitions
in that format instead; never invent a parallel owner/assignment authority.

Attach lightweight scout prompts/results to the existing parent record, or
retain the tool/conversation reference when project rules permit. Do not open
an implementation helper assignment just for read-only assistance or create
a second scout ledger. Cite accepted findings and material corrections in the
parent result. Helper worker/review/strong schemas below apply to implementation
assignments; they are not an evidence-only protocol.

Use one stable record per unresolved assignment; record each original result
before dispatching follow-up work. A `strong_review` action means request
independent strong review. A `strong_takeover` action means stop the affected
Luna assignment and dispatch sol_expert or take over yourself, without asking the user
to choose a model. A helper cannot dispatch native tools on its own: executing
these actions is the supervisor's responsibility. Its transition checks are
deterministic; adherence, reviews, model selection, and permissions are not
enforced by Markdown or by the helper. Do not claim unobserved escalation.

Results identify `completed`, `needs_decision`, `blocked`, or
`budget_exhausted`, changed paths, checks passed/failed/unexecuted, commands,
evidence references, decisions and remaining acceptance conditions. Retain
the original failures and patches even after success. Preserve records when
disabling the kit. Start a new chat after activation/removal; an existing
chat may retain previously loaded instructions.

## Evaluate usefulness

Use a few comparable development tasks and existing records/telemetry to assess
accepted progress per elapsed hour and total usage per completed milestone,
including supervisor review, validation setup, repair and takeover. Also record
elapsed completion time, useful accepted findings, missed coverage, review
corrections, and Sol rework while preserving software acceptance criteria.
Include main chats and all helpers in model usage, with input/cached-input and
output by model where available. Use consistent per-session totals or interval
deltas, not sums of repeated cumulative samples; cached input is a subset of
input, not an extra total. Disclose missing telemetry and comparison limits.
Agent counts, completed turns, token throughput, Luna token share, and large
cached-input totals alone do not establish speed, cost savings, or quality.
Keep this a small retrospective in existing records, not a mandatory per-scout
reporting process.
