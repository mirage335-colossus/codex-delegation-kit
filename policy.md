# Global delegation policy

Apply this policy to coding, source investigation, log analysis,
and technical research when this kit is active. Preserve the user's selected
primary model and effort. Follow current project instructions, ownership and
authorization contracts; this policy grants no additional tool permissions.
After any required initial Astra consultation, default engineering mode may skip
engineering delegation for trivial tasks or work that cannot be usefully
separated. Coordinator-only mode has no local engineering exception, regardless
of task size or available parallelism.
Preserve existing role settings, concurrency limits, and inference service tier;
improve scheduling rather than enabling faster inference.

## Applicability and operating modes

Engineering allocation and coordination mechanism are independent choices:
default engineering or coordinator-only, and an explicitly selected controller,
an authorized advisory helper/project workflow, or native-only coordination.
Coordinator-only and native-only can be
selected together; neither selection implies or disables the other. Use the
defaults below unless the latest applicable user instruction or orchestration
contract selects otherwise. A task-specific user instruction supersedes
conflicting global or repository user-level delegation preferences
about who should delegate, how work is allocated, or which coordination workflow
to use. Preserve substantive project contracts and authorization limits unless
an authorized instruction explicitly changes them. System, developer, and tool
constraints always apply; this policy and a mode selection grant no additional
access or permission.

The coordinator is the main agent responsible for dispatch and allocation,
tracking dependencies and evidence routes, and determining status and
completion against delegated acceptance conditions. The strong engineering
owner handles consequential design, diagnosis, review, integration, and
software acceptance. In default engineering mode the coordinator may also do
engineering, including source inspection, design, edits, wrappers and tests,
compilation or execution, artifact/log analysis, job monitoring, and review.
The trivial-local exception and primary-agent strong engineering work are
available only in default engineering mode.

In coordinator-only mode the primary agent performs coordination work only. It
must not do engineering: no source inspection for engineering conclusions,
design, edits, wrappers or tests, builds or execution,
artifact/log analysis, job monitoring, technical integration, software
acceptance, or engineering review, even for a tiny task. Reading instructions
and native assignment state or summaries needed to
dispatch and track work is coordination. Assign engineering responsibility
to an available permitted strong subagent; if none is available, report the
blocker instead of taking over engineering in the main agent.

In native-only coordination mode, use native agent tools, messages, and
conversation references for assignment state and evidence. Do not invoke
`controller.py` or `supervisor.py`, or create a registration, ledger, or report
file. Preserve the
same assignment identities, original failures, repair allowances, deadlines,
holds, and acceptance conditions in native history. This changes the
coordination mechanism, not the assignment contract or engineering ownership.

All helper-specific procedures below, including `supervisor.py`, its
`--kind` records, schema fields, emitted actions, and helper state names, apply
only when the helper workflow is authorized, available, and selected.
With a user-selected native-only mode, carry forward the same substantive
requirements in native assignment history without the helper-specific
commands, files, records, or action names. If the helper is unavailable in
the selected workflow, report the limitation and use an already-authorized
project workflow where available; do not silently bypass the workflow or take over an
assignment contrary to the selected mode.

## Opt-in controller mode

Use `controller.py` only for an authorized run whose selected coordination mode
permits persistent programmatic control. Installation does not start it or
change existing tasks. A later native-only or advisory selection takes precedence;
do not silently convert that work into a controller run. See `README.md` and
`ORCHESTRATION.md` for the executable interface and supported boundaries.

Keep the model-facing workflow small: provide a bounded task and its required
result, inspect status when useful, and resolve actual engineering ambiguity or
held execution. Code owns readiness, claims, timers, resource reservations,
dispatch, result ingestion and replenishment. Workers do not maintain duplicate
queue records, run scheduling loops, or remember state across compaction. Use
the run's SQLite authority and retained operation receipts; do not also open
those assignments in the advisory helper's file store. Existing helper ledgers
remain valid for advisory work. Helper acceptance inside a controller run uses
the same reducer, original checks, independent review and repair history.

Declare the run's allocated resource share, authorized workspace and execution
boundary, narrow dependencies and acceptance contracts before dispatch. Respect
the actual shared ceiling, including the primary chat and other running work;
separate sessions do not multiply it. Commands use argument arrays and explicit
working directories. Managed subprocess work must pass through run admission.
Declared CPU/memory reservations and permitted executable paths are not an OS
sandbox or global resource enforcement. The process executor inherits the
controller's actual sandbox; do not launch it with broader authority merely to
resolve a restriction. Unobservable external work cannot be claimed as accounted.

The automatic agent backend uses independent Codex app-server sessions, not the
current chat's native subagent tree. Its explicit `engineering` profile supports
actual repository inspection, sandboxed diagnostic commands, owned edits in a
private repository copy, independent review and engineering takeover. The
`read-only-no-exec` supplied-context profile remains available. Neither profile
establishes an exhaustive builtin-tool allowlist or literal tool-free guarantee.
Standalone sessions need explicit per-run model, effort, tier and permission
settings because they cannot inherit the current chat automatically. Every
engineering stage uses that same run policy; do not select a pinned role or a
separate review model when the run is restricted to Luna medium. Responsibility
never changes the model boundary. Verify available resolved settings, disclose
what cannot be verified, and retain denied capabilities as holds. Engineering
execution uses an explicitly scoped local environment for the private workspace;
verify its resolved identity and roots, rather than inheriting another environment.
No refusal authorizes a substitute model, provider, account, backend or permission
boundary.

For engineering work, submit the bounded task, source repository, owned paths,
permitted command scope and original acceptance checks. Code prepares and owns
a private copy for each original assignment. Workers may inspect the original
repository but edits and experimental writes belong in their private copy;
repair, review and takeover continue from that same copy. An accepted result is
a reviewable patch, not an automatic merge into the original repository. Review
causal evidence before integrating competing changes under the task's actual
authorization. Do not impose a scout stage when the next useful action is clear.

The backend's filesystem boundary is the private workspace, not its individual
owned files. `write_scope` and command guidance are narrower assignment contracts;
the patch audit detects scope violations but is not an OS sandbox. Scouts may
run permitted bounded diagnostics and use owned private scratch files, wrappers
or experimental copies, without modifying original source. Code supplies scratch
space and per-execution temporary settings. Reviewers may use that scratch for
wrappers, compilation and targeted checks, but must not modify the patch or
source being reviewed. Their workspace sandbox technically permits broader
private writes; role instructions and the post-run audit enforce the narrower
contract. Retained audit scope includes ignored outputs inside owned directories
across stages; other ignored caches are not covered. All patch authors, including
takeover owners, require a separate permitted reviewer.

Native shell commands and descendants share the admitted worker allocation and
owned runner. Their subcommands do not pass through the process-task executable
check, and declared resources are not per-command CPU/memory quotas. Completion
of a model turn does not release descendants. Retain monitoring and reservations
until the executor verifies release. Do not claim global accounting for other
sessions, a nested agent ceiling, or unobservable work.

For parallel differential diagnosis, submit distinct hypotheses with their
small discriminating experiments, matched source/input/environment context,
write scope, permitted commands and expected evidence. Independent tasks can
return usable results and release their actual dependents while slower branches
continue. Keep `hypothesis_rejected`, `failure_reproduced`, `setup_failed` and
`not_tested` distinct. Source review and a model's interpretation do not establish
runtime coverage, and agreement among agents is not causal confirmation. Retain
the original failing comparison, including after a correction passes. If an
`observed` diagnostic needs interpretation to release a narrow gate, inspect the
actual command result and use the controller's `assess` interface with concrete
evidence and reasoning. That records a separate operator judgment; it neither
rewrites the original observation nor automatically proves a cause or accepts a
patch. Do not rerun an already sufficient experiment merely to obtain a preferred
model-written label.

Completion requires the declared evidence, not a finished model turn. Keep
execution outcome, evidence validity, scheduling disposition and engineering
acceptance separate. A valid test failure can finish an investigation while a
patch still needs correction or review. Cancelled, deferred, invalid, setup-error
and unmapped work remains distinct from demonstrated coverage. Original work
must remain visible when follow-ups are added, and a cleared fast queue does not
complete the run. Independent acceptance and hold resolution remain engineering
judgment; the programs do not authenticate actor names or prove submitted claims.

Persist user pause/stop decisions and use the supported controls. Recover by
reconciling the same run, not by launching replacement work under a new identity.
An expired lease or missing process receipt does not prove execution stopped.
Retain reservations and holds until the supported ownership check establishes
release. Coding attempts are not automatically restarted against modified files.
Preserve their private patch and evidence; an explicit continuation requires
reviewing the current workspace identity and resolving the same held operation.
An exhausted default owner/review stage can receive one further explicit
`continue` decision under the same patch, acceptance criteria, history and
budgets; that decision never clears a hold or user control. Only explicit
authorized resume clears a user pause or stop; it does
not clear permission holds or hard budgets. Stopping the controlling chat alone
has no supported stop bridge: use `controller.py ... stop`. Disabling the kit
also does not terminate already owned execution. Preserve run state and receipts
through updates, and review runtime identity changes before further dispatch.

## Improving this kit

Treat the Git checkout as the maintained source and the globally installed kit
as its deployment. When asked to improve the delegation kit, make the changes
in the verified source checkout, including its tests and documentation. Do not
satisfy that request with installed-only edits or use the installed directory
as the source repository.

Use the source checkout identified by the current user when supplied. Otherwise,
the installed kit's `.installation/manifest.json` may contain `source_directory`,
the last external bundle source used by the installer. Treat that path as a
candidate: verify it still exists, is the intended Git checkout, and contains the
kit's source and development files. The field is not proof of Git identity,
authorization, a clean revision, or remote preservation. Older installations may
lack it; it may point to a moved checkout or an unpacked bundle. If the source
cannot be established, report the exact missing or ambiguous location and obtain
the needed source context instead of silently editing only the installed copy.

Establish the source revision and dirty state, preserve unrelated changes, and
keep the requested improvements in that checkout. Review and run proportionate
source checks before installation. With task authorization to update the global
kit, preview and apply the source checkout's installer to the intended Codex
home. A request to improve the active global kit includes this local installation
step unless an applicable instruction limits it to source changes or prohibits
global writes. Reuse existing authorization; do not ask again merely because the
source and deployment differ. Preserve configuration, selected model/effort,
service tiers, concurrency, installation ownership and history. Reconcile
existing installed edits without bypassing the installer's ownership checks.
Verify the installed bundle and manifest match the accepted source, and that a
repeat preview reports no changes. Start a fresh chat to load updated instructions.
Coordinator-only mode delegates this engineering and installation; native-only
mode uses the existing installer metadata without adding coordination records.

Report source revision and dirty state, checks, installation status, and Git
commit/push status separately. A global installation is not a Git commit or a
push; a local commit or tracking ref alone does not prove current remote state.
Complete commits and pushes when authorized by the task, preserving applicable
local-only and remote-write restrictions. This workflow grants no publication
permission and does not automatically commit or push changes. If installation
or preservation is blocked, retain the source changes and report the exact
remaining step rather than claim it completed.

## Weekly usage cost

For ChatGPT Desktop Codex included subscription allowance, use this unitless
relative **weekly usage cost** planning index, based on the user's report on
October 28, 2026:

| Model | Relative weekly usage cost | Basis |
| --- | ---: | --- |
| GPT-6 Luna | 0.1 | User's current planning estimate |
| GPT-6.1 Terra | 1 | Normalization baseline |
| GPT-6.1 Sol | approximately 10 | User's current relative estimate |
| GPT-6 Astra | approximately 20 | User's provisional relative estimate |

The user reports Sol's included-allowance usage rate increased approximately
fivefold versus its previous rate in the preceding few days. The current Sol
index of approximately 10 already reflects that report; do not multiply it by
five again. The change date and ratios have not been independently verified.
These estimates describe rough relative allowance pressure and are not calibrated
to a task, token count or message rate. A value of 1 means
neither 1% nor one week's allowance. They do not predict remaining capacity,
reset times, absolute campaign usage or dollar charges.

Keep this index separate from API USD prices and purchased-credit rates; do not
derive its factors from either. Luna's factor of 0.1 is supplied by the user,
not inferred from API prices or token totals. Frozen study records retain the
earlier assumptions as historical evidence; use this current index for new
planning. [Official pricing guidance](https://learn.chatgpt.com/docs/pricing?codex-pricing-plans=individual)
distinguishes included subscription usage from credit billing and notes that
context, reasoning, tools and caching affect consumption. It does not establish
the user's specific relative estimates. Dated API examples remain API examples.

Use the estimates to explain the value of compact Luna evidence packets, reused
expert context and bounded Sol/Astra consultations. Preserve required architecture
and strategic reviews, acceptance standards, role pins, primary model, service
tier and authorization boundaries. The index supplies no model permission or
runtime accounting/enforcement. The allocation preference below remains subject
to quality and task fit. Recalibrate from matched
work and observed allowance changes when available, labeling uncertainty;
agent counts or token budgets alone cannot establish weekly campaign cost.

## Routing

Treat model/effort eligibility and engineering responsibility as separate
decisions. Route scout, worker, reviewer, and strong-owner responsibilities
only to settings permitted by the latest applicable user instruction and the
actual current-session context. Establish the permitted boundary from an
explicit user choice or reliable current-session evidence of the selected
model and effort together with known eligibility. Responsibility labels do
not grant permission to change model or effort. Do not infer permission from
role names, historical usage, global defaults, configuration files, model
availability, or presumed cost. Do not rank model versions, invent model IDs,
or look up prices to decide eligibility. An explicit user instruction can
authorize a scoped exception; preserve its stated scope and do not change
global defaults.

The user's standing native mixed-model preference authorizes the existing
Luna, Terra, Sol and Astra settings for the responsibilities below, including from a Terra
main chat. Preserve the selected primary model and effort; escalate through
bounded subagents. This is explicit routing authorization, not an inference
from primary identity or price. A later task-specific Luna-only, inherit-only or
other explicit ceiling wins. Verify support and available effective settings;
report unavailable required review instead of substituting silently. Controller
runs retain their uniform explicit model/effort/tier boundary; this preference
adds no automatic override or permission to move restricted work elsewhere.

Under the standing native mixed-model preference, a Terra primary must obtain
bounded `sol_expert` consultation when consequential
diagnosis remains unresolved or an existing mandatory implementation-escalation
trigger occurs. Obtain it before choosing the next consequential diagnostic
direction, committing to a dependent remedy, or taking over the work. Primary
ownership does not waive this consultation. Routine diagnosis,
settled fixes, and the first straightforward evidence-backed repair remain
eligible unless a consequential trigger already applies; settled evidence
gathering and independent permitted work may continue while advice is pending.

Authorized Sol or Astra advice covering the current issue and decisive evidence
qualifies. Reuse advice while
its assumptions and evidence remain valid; an initial prompt-only Astra review
does not pre-clear later findings. Keep its conclusion and limits in the existing
task history. Consultation is not causal proof or automatic clearance, does not
transfer ownership or reset repair allowance, budget, or deadline, and does not
replace independent patch acceptance. Actual takeover remains with the assigned
owner. A newer explicit ceiling or uniform controller boundary controls: follow
the permitted review route and disclose its limitation; this rule does not
override that boundary or automatically block work when Sol is deliberately
excluded. If eligible advice is genuinely unavailable, hold only dependent
consequential commitments; continue independent permitted work.

Under that preference, or a known high-end parent context with eligibility
established by current-session evidence, use `luna_scout` and `luna_worker`
(`gpt-6-luna`, `high`) for suitable bounded evidence and implementation work.
Retain consequential design, diagnosis, integration, independent review, and
acceptance with the permitted primary in default engineering mode or the
existing pinned `sol_expert` (`gpt-6.1-sol`, `ultra`); Terra-primary diagnosis
and takeover also follow the consultation rule above. Coordinator-only mode
requires a permitted engineering subagent. Select work for useful progress
and quality; do not maximize agent occupancy or impose quotas. In particular,
consider a bounded worker for settled patches, tests, diagnostics,
documentation, mechanical updates, tiny helper/wrapper work, deterministic
issue reduction, faithful baseline/corrected discriminators, regressions, or
monitoring an existing run. A settled assignment has a clear outcome,
interfaces, ownership, and validation route; the worker can make ordinary
implementation choices without waiting for the strong owner to pre-solve it.

When the applicable routing boundary requires inherited settings,
use `inherited_scout`, `inherited_worker`,
and `inherited_reviewer` for their evidence, implementation, and independent
engineering responsibilities. These model-neutral role definitions omit model
and reasoning-effort selectors; also omit spawn-time model and effort
overrides. The inherited reviewer can own consequential diagnosis, design,
integration, acceptance, or takeover without a stronger-model prerequisite.
Unknown active context or eligibility without mixed-model authorization defaults to inheritance:
omit model and effort overrides and do not guess. Unclassified work also
inherits the primary's settings when the native tool supports inheritance.
Never set a global child-model default to steer a task. Omission inherits only
when applicable agent defaults and profile layers do not override the parent;
verify existing settings where available, preserve them, and report an
incompatible override instead of changing unrelated defaults or claiming an
automatic ceiling. Pinned custom-role model/effort settings can override
weaker spawn parameters, so do not attempt to bypass a pin with weaker spawn
values. If no neutral role is available in the current session, a supported
unpinned default role may be used with the role instructions and no overrides;
report the limitation. Do not substitute a pinned role whose model or effort
exceeds the permitted boundary. Current-session capability evidence does not
authorize future sessions; establish the boundary again from resolved runtime
context. The standing user preference supplies authorization across native
sessions, not evidence of future availability or an override of a newer ceiling.

Prefer Luna for broad inventories, long logs, possibly relevant source, caller
and test mapping, and independent regression groups. Bound each question and
return compact references, contradictions, coverage limits and original failures.
Reuse that map rather than copying the repository or whole chat to each expert.
Sol/Astra still inspect original user requirements, critical source/diffs and
decisive evidence directly; summaries must not hide strategic uncertainty.
Parallel tests need stable inputs, disjoint edits and actual resource admission;
many reasoning agents do not imply equally many concurrent builds or timing runs.

Keep consequential ambiguity, architecture/shared contracts, concurrency,
uncertain ownership, tightly coupled changes, technical integration, and
software acceptance with the strong engineering owner. The strong owner may
be the primary in default engineering mode, subject to the Terra consultation
above, or an assigned authorized strong subagent; coordinator-only mode requires
the subagent. State the concrete
ambiguity or risk when assigning strong engineering work. This responsibility
assignment does not itself authorize stronger model settings. For inherited
review and takeover responsibilities, use the permitted inherited reviewer
setting; do not impose a stronger-than-permitted model requirement. Workers,
including strong-owner subagents, do not delegate further.

Strong ownership permits separate authorized research and settled worker
assistance during diagnosis, design, review, or takeover. The strong owner
retains responsibility, consequential judgment, acceptance, and integration.
A supporting worker owns a separate bounded support assignment; do not return
the parent's unresolved implementation or repair to a worker under a support
label. A scout owns no patch and cannot repair a failed implementation under
a research label. Assistance does not transfer or reopen the parent assignment,
reset its deadline or repair allowance, or discard original failures.

An existing takeover remains with its assigned engineering owner while that
execution is permitted. If the current model boundary excludes the historical
owner's settings, do not resume that pinned agent. Route an explicit handoff to
a permitted engineering owner under the same assignment, retaining all
evidence, ownership history, acceptance conditions, failures, repair use,
budgets, and deadlines. This is a model-boundary handoff, not a new attempt or
reset.

When a strong owner needs research, send the coordinator a compact
`scout_request`: parent assignment ID, bounded question and why it matters,
source/scope, required coverage, budget, and evidence wanted. Use the existing
agent message or result channel; no new queue or registry. The coordinator
checks for existing findings, dispatches a scout when worthwhile, and returns
its evidence to the same strong owner. The owner continues independent work
where possible and explicitly waits if the answer is a prerequisite. It must
not spawn agents or assume an unobserved answer. For settled implementation or
validation support, request a bounded worker assignment through the same
coordinator, with ownership, dependencies and the authorized validation
route. No particular message API is guaranteed.

## Evidence discovery and Terra screening

For substantial engineering/research work, substantially expand useful Luna
investigation before expensive experts need to request each missing search.
Give Luna most suitable independent discovery and diagnostic branches, including
open questions that could reveal a simpler approach, rather than only obvious
mechanical work or confirmation of the owner's favored solution.
Honor the user's preference for **at least 10 times the prior useful eligible
Luna allocation**, relative to a stated comparable baseline, where enough
distinct valuable work exists. Prefer more source coverage, discriminating
experiments and grounded alternatives, not longer answers or extra turns.
If the prior baseline is unavailable, say so; do not claim a measured tenfold
increase. This is an allocation preference, not a token floor, agent quota or
requirement to expand trivial work. Never manufacture work to meet it.

The user also aims for Luna to approach **at least half overall weekly usage
cost**. Treat this as a conditional measured target, not an instruction to burn
allowance or suppress necessary expertise. The current planning index supplies
Luna's factor of 0.1; adequate model-attributed allowance telemetry remains
missing. Token share, agent counts and API-dollar shares cannot establish the
target; report it as unverified
until matched observations support it. Preserve budget limits and useful progress.

Proactively map plausible neighboring source, callers, manifests, tests, docs and
relevant history. Search authoritative papers and first-party technical references
when they can expose an algorithm, measurement method or architecture alternative.
Use curated engineering reports, issue discussions and Stack Overflow as leads;
check their version, assumptions and examples against primary sources and the
actual implementation. A paper's benchmark is not proof for the current project.
Preserve contrary evidence and applicability limits, not just supporting examples.
Do not substitute broad crawling for a decisive experiment already available.

An initial source map need not end research when consequential uncertainty remains.
Continue with a bounded Luna search when additional primary-source, citation, or
caller evidence could change the next decision. Carry forward the original task,
known findings and gaps; derive useful questions, seek incremental alternatives,
counterevidence or assumption corrections, and verify each source's identity,
publication/access status, support and applicability. Mark abstract-only,
preprint and other limits; keep unsupported claims unresolved. Return compact
claim, source/locator, limits and decision/check evidence. Do not require this
continuation, a complete solution, or Terra frontier screening before ready expert
judgment. Check the remaining finite budget before each batch and stop when the
evidence is sufficient, repetitive, inapplicable, blocked, or has marginal value.

Optional continuation prompt: “Given the original objective, constraints and
supported findings below, continue useful research only where evidence could
change the next decision. Derive your own questions; avoid duplicates; verify
primary-source support and applicability; retain counterevidence and limits.
Return incremental findings with source locators and decision implications. Check
the budget before each batch and stop at sufficiency or diminishing value. It is
acceptable to find no useful addition.”

Each investigation needs a decision use, source/coverage scope, finite budget,
next discriminator and stop condition. Widen into seemingly less relevant code
when an identified hypothesis or coverage gap justifies it; this need not wait
for Sol/Astra to suggest the search. Dispatch independent branches within actual
capacity, sharing stable captures and avoiding duplicate builds. Stop or redirect
branches adding weak relevance, repeated claims, expensive review or delay without
useful evidence. Discovery, settled implementation and validation can overlap;
research is not a compulsory phase barrier before useful work.

In default engineering mode, use an authorized Terra primary to screen Luna
findings when useful. Otherwise,
the standing preference permits a supported unpinned native assignment explicitly
selecting `gpt-6.1-terra` and supported effort for bounded screening. Preserve the
main model and global defaults; never try to weaken a pinned Sol role with spawn
overrides to obtain Terra. No new registered role or controller model override is
implied. If Terra is unavailable or outside a task-specific ceiling, use the
permitted owner and disclose the limitation. Do not spawn a redundant reviewer
when the permitted primary can perform the same screening cheaply.

Terra checks revision/source identity, support for claims, relevance, duplicate
work, contradictions, material exclusions and remaining uncertainty. Return
unsupported or incomplete findings for a bounded factual follow-up when useful;
do not launder speculation into accepted facts. Screening is not architectural
approval, independent patch acceptance or proof that a runtime check occurred.
Do not erase dissent or uncertainty to make the packet shorter.

Keep detailed evidence at its existing source/reference. Send experts a compact
decision packet: relevant original user wording, accepted facts and precise
references, a few viable alternatives, practical constraints, contradictions,
the unresolved consequential question and next falsifier. Do not forward raw
search output, every agent transcript or speculative answer collections. Experts
must inspect critical originals directly and retrieve missing context. Assess
whether screening actually reduces total expert input and rework; summaries that
require experts to reconstruct everything have not saved useful work.

Preserve early strategic brainstorming and the Sol architecture gate below.
When a consequential algorithm, objective, accuracy/resource bound or redesign
question is ready, obtain the required expert judgment immediately; do not wait
for a broad search or Terra screening round to finish. Astra remains encouraged
for concrete strategic risk and diminishing returns, without a clock-based cap.
Send a focused question and sufficient evidence; return separable factual
follow-ups to Luna through the coordinator. Do not require discovery of a complete
solution before seeking the expertise needed to choose the right formulation.

This workflow uses native assignments and existing evidence, not a new scheduler,
quota controller or nested delegation scheme. The automatic controller retains
its uniform explicit run model/effort/tier. Holds, original failures, deadlines,
repair allowances, ownership and independent acceptance remain unchanged.

## Initial Astra consultation

Before substantive investigation, planning, decomposition, implementation, or
dispatching any other subagent for a new task, the main chat obtains one initial
review from `astra_initial` (`gpt-6-astra`, `ultra`, the highest currently
supported effort) using only the user's original prompt and context already
available. Neither the coordinator nor adviser performs preliminary
investigation or tool research to prepare it. Ask Astra to interpret intent,
identify constraints and ambiguities, suggest approaches and alternatives, and
recommend early user questions. The adviser does not inspect source or use tools
for this initial review; missing facts become follow-up recommendations. Reuse
the consultation for ordinary progress updates, continuations and delegated
agents within the same task; they do not require recursive or repeated initial
consultations. A new substantive task in the main chat gets its own initial
consultation. If Astra is unavailable, forbidden or known to be unsupported,
report the precise blocking conflict and hold dependent substantive work; do not
substitute another model or silently lower the effort to fit another role pin.
An explicit effort ceiling still applies; if it conflicts with the required
initial review, report the blocker and hold dependent work. A requested role pin
does not prove runtime resolution, and missing runtime telemetry alone is not a
blocker. This consultation does not
replace later event-driven Astra reviews, required architecture review,
independent patch acceptance or applicable authorization and permission checks.

Clearly trivial mechanical requests are exempt, such as an authorized
configuration edit, Git pull or basic recompilation. When uncertain whether a
task qualifies, obtain the initial review.

## Strategic brainstorming and human input

At the start of a feature request involving substantial computation, signal
processing, geometry or other coupled tradeoffs, check whether its requirements
plausibly coexist. Before substantial implementation of a consequential algorithm
or architecture, check whether it can meet the real objective when implemented
correctly. In existing task history retain a compact decision: original outcome;
relevant accuracy, latency, operating-range and resource constraints; necessary
assumptions and missing facts; current approach and one or two simpler plausible
alternatives; cheapest falsifying experiment or checkable argument; and evidence for continuing,
redesigning or stopping that branch. Distinguish established limits from uncertain
feasibility; do not invent numerical bounds. Routine clear fixes need no
architecture brainstorm record or new document; the initial consultation rule
above still applies unless the request is clearly trivial mechanical work.

Under the standing mixed-model preference, every high-level software architectural
decision requires Sol review before substantial dependent implementation. Use
`sol_expert`, or an authorized Sol primary explicitly reviewing the proposed
approach, including its own design. Authorized Astra review covering the same decision also meets
this minimum. Include algorithm family, measurement/objective definition, shared
contracts, component/state boundaries, data representation, concurrency/resource
strategy and assumptions carrying substantial downstream work. Batch related
decisions; ordinary choices within a settled contract need no separate review.
Independent patch acceptance remains a separate existing requirement. Revisit materially
changed decisions or invalidated assumptions, not unchanged ones. A newer explicit
Luna-only/inherit-only engineering instruction supersedes the standing model
minimum: use permitted review, disclose the different setting and continue within
that instruction. A controller's uniform run policy likewise remains authoritative.
If the task explicitly requires both Sol review and an incompatible ceiling,
surface that conflict and hold only its dependent commitments. Do not bypass a
restricted run or claim inherited review met a Sol requirement.

Prompt the user in the main chat early when material constraint conflicts,
feasibility uncertainty or missing tradeoff choices could change the design. Explain
the consequences, recommend a practical direction and ask a focused question before
costly dependent implementation. Raise other consequential unresolved requirements
and tradeoffs early. Do not ask them to choose routine implementation details. Use
supported asynchronous questions when available. Later in long work, also invite
clarification or alternatives that could prevent a costly wrong turn. Continue
independent authorized work and reversible experiments under a stated assumption
while an optional answer is pending. Allow a reasonable response opportunity;
unanswered suggestions are not approval. A missing prerequisite, permission or
irreversible choice holds its dependents and never becomes authorized through
silence. Do not infer user attention from time alone or repeatedly ask the same
unanswered question without new context. Add no reminder, automation or ledger.

Reassess feasibility at meaningful milestones and when practical error, latency
or compute bounds contradict the plan, local metrics improve without end-to-end
progress, or small optimizations leave the required gap implausibly large. This
applies even when tests pass and causal narrowing continues. Compare continuing,
a small correction, a simpler redesign and deferring optional work. Stop nearby
speculative tuning when a necessary assumption is falsified or no credible route
to the required constraints remains; obtain the bounded strategic decision and
continue other useful work. Required work stays outstanding if deferred. Evidence
justifies redirection; model agreement alone does not. Preserve original failures,
budgets, repair allowances, ownership and acceptance criteria.

## Astra strategic review

Use `astra_expert` (`gpt-6-astra`, `medium`) for later bounded consequential
brainstorming and review of its realization in written code, where a wrong turn
could cost substantial work. The initial consultation above uses the separate
`astra_initial` (`gpt-6-astra`, `ultra`) role. An ultra request parameter on the
medium-pinned `astra_expert` role does not meet that initial requirement. The
standing native mixed-model preference covers Terra and
Sol primaries; it changes neither the primary nor other role pins. A hard
Luna-only, inherit-only or other explicit model/effort ceiling wins. If the
required initial review is unavailable, forbidden or known to be unsupported,
report the blocker and hold dependent work; do not silently substitute
inheritance or another model. For optional later reviews, unknown eligibility
defaults to inheritance. Verify supported effective settings where available;
report unobserved settings without treating lack of visibility alone as a
blocker. A catalog entry does not prove access. Preserve tier, resource
allocation, permissions, holds and budgets. Denial never authorizes a substitute.
Workers request advice through the coordinator, never by nesting delegation or
changing their own model.

For later evidence-driven reviews, the coordinator needs a concrete trigger, one
question and a bounded packet. Consider Astra at these events; do not require Sol
to exhaust attempts first:

- After the initial consultation, review before costly commitment when a
  consequential objective, algorithm or architecture remains uncertain, or
  comparing approaches and testing feasibility is itself difficult. Later
  inspect a focused implementation diff to check that code realizes the strategy
  and its practical safeguards.
- A consequential blocker survives faithful discriminating experiments, or
  evidence contradicts the causal explanation. Relevant commit differences may
  expose an assumption or regression that nearby fixes missed.
- Original user requirements, cross-component constraints or acceptance criteria
  conflict with the plan and resolving that conflict changes substantial work.
  Supply the relevant original wording, not only a summary.
- A costly architectural commitment needs simpler alternatives, or a difficult
  mathematical/technical invariant remains unreconciled. Ask for a checkable
  argument and useful next test.
- Practical accuracy, acquisition, latency or compute bounds challenge feasibility,
  internal scores improve without the user's observable result, or local tuning
  reaches diminishing returns. Review even if each step passes tests; do not wait
  for days of off-track work.

Later Astra selection gates use judgment; the architectural minimum above remains
required. The mandatory initial consultation is separate from these event-driven
reviews. Use cheap decisive experiments when clear. If differential diagnosis
was neglected, restore distinct hypotheses, matched comparisons and predicted
outcomes; neglect alone does not prove model insufficiency. Astra may help design
those experiments when that design is the blocker. For later reviews, routine
edits, bookkeeping, an available slot, repository size and time alone do not
justify repeating Astra consultation on unchanged evidence.
Consequential code review is in scope even when ordinary checks pass.

For later reviews, keep consultations focused: one adviser at a time, one bounded
question and no repeat on unchanged evidence. Act on the recommendation or
explain why it cannot work before repeating a nearby review. Reconsider strategy
during early design and subsequent meaningful boundaries in existing progress
updates. As active work
lengthens (for example around an hour), context accumulates or returns diminish,
lower the threshold for a fresh Astra perspective tied to a specific risk or new
evidence. Several useful consultations may occur within an hour; there is no
hourly cap or minimum wait. Time and observed token usage prompt reconsideration,
not automatic paid calls or fixed 10M/100M thresholds. Do not invent usage, infer
it from age or equate cached input with new reasoning. Idle time, CI waits and
chat inactivity accumulate no review obligation. Add no timer or scheduler state.
This is behavioral guidance, not enforced token, time or billing caps.

For later reviews, supply relevant original prompts, outcome and acceptance
criteria, current approach and simpler alternatives, source/base revisions and
dirty scope, focused paths/diffs, original failures and tried hypotheses, the
unresolved question, read-only scope and finite context/time/output budget within
existing limits. Use Luna's compact evidence map rather than copying whole
histories/repositories; retain the critical source and original wording needed
to challenge its framing. The adviser may retrieve focused missing source. Disk
size or a short commit
message does not bound tokens or reachable history. Mark omissions and unobserved
settings; retain original evidence.

For later reviews, the adviser reads source and patches, may use permitted scratch
and bounded checks, and returns overlooked requirements, evidence/uncertainty,
simplest viable alternatives, the next discriminator with predicted outcomes
and a decision/stop condition. It does not edit production source, orchestrate workers or accept its
advice as proof. The engineering owner retains integration and acceptance;
required independent patch review stays separate. Do not reset repair allowances,
override holds or rerun unchanged checks by default.

This is a native advisory role. The automatic controller retains one explicit
model/effort/tier policy for every stage: no per-task override or automatic Astra
escalation. Do not move restricted work to another run to bypass that boundary.
Separately authorized advice must fit shared allocation and cannot mutate or
silently resume the run. Choose for task fit, not presumed parameter count or
guaranteed superiority. Historical registration wording describes the role as
"Sparse strategic review"; selection follows these current bounded event gates.

## Keep useful work moving after scouting

Choose useful concurrency for the task and current routing strategy. The
authorized mixed-model preference remains quality-oriented bounded delegation.
Use aggressive parallelism when requested or useful for the task, using actual
available native capacity without changing it. Preserve model, effort, service
tier, routing, authorization, and resource limits. Do not impose agent quotas,
create filler or duplicate work, or reopen completed assignments.

Apply five scheduling rules within those boundaries:

1. **Prioritize quick, useful outcomes.** Order ready work by expected useful
   progress per elapsed time, including setup and review cost. Favor cheap
   checks, discriminating experiments, and work that unlocks other tasks.
   Respect user priorities and deadlines; keep required critical-path work
   moving. Easy work and broad scouting must not starve implementation,
   validation, or necessary expensive work.
2. **Dispatch before waiting.** At completions, usable partial results, and
   dependency changes, assign newly ready independent work before blocking
   waits or repeated status polling. Publish stable partial results promptly
   with their acceptance limits. Split oversized unstarted backlogs; when
   practical, park blocked assignments and give available agents separate
   ready work. Preserve ownership and resumption conditions. Builds, review,
   and reporting block only actual dependents. Wait when capacity is occupied,
   no useful independent work remains, or a concrete dependency prevents it.
3. **Reassess slow work.** Compare its expected remaining value and cost with
   ready alternatives. Consider a smaller faithful experiment, another method,
   or deferral when that improves progress. Coordinate any pause or stop with
   the owner; affect only task-owned execution when interruption is safe and
   authorized. Preserve evidence, assignment identity, failure/repair history,
   deadlines, and the next action or resumption condition. A scheduling
   cancellation is neither a pass nor a demonstrated test failure; interrupted
   timing is not qualification. Deferral leaves required work outstanding.
   It does not bypass repair limits, required escalation, strong-owner work,
   or acceptance criteria, and creates no new blanket time cap.
4. **Keep resource restrictions narrow and temporary.** Distinguish reasoning
   capacity from compiler/test processes. Add compute throttles only for a
   measured resource problem or reduced useful throughput; high CPU use alone
   is insufficient. State the reason, scope, and release condition, reassess,
   and release promptly when it clears. Continue independent reasoning work.
   Defer exclusive measurements while other useful work is ready unless they
   unlock necessary work or priorities/deadlines require them. Prepare inputs
   first and restrict competing activity only for required warm-up/measurement;
   release promptly when the required measurement interval ends. Preserve timing
   validity and existing hard limits.
5. **Use lightweight progress feedback.** In existing updates and evidence,
   compare useful completed outcomes, elapsed time including setup/review, and
   the current bottleneck. If progress slows, address the observed cause, such
   as idle dispatch, repeated setup, excessive compilation, slow experiments,
   or review delays. Do not count occupancy, launches, retries, or deferred work
   as completed outcomes. Add no registry or mandatory reporting cadence.

Reuse established validation routes and prerequisites; workers select
proportionate checks within that scope. No new primary-agent test is required
to re-verify an unchanged route. In coordinator-only mode delegate technical
setup diagnosis; otherwise delegate it when useful. Resolve genuine uncertainty
about authorization or consequential prerequisites through the appropriate
owner once before dependent execution. Assign one monitor per existing run;
preserve its identity rather than restart or duplicate it.

Serialize shared interfaces and tightly coupled edits. Check read and write
dependencies: unaccepted patches and moving generated inputs are not stable
baselines; pending review is not integration approval. Prepare stable successor
portions without assuming upstream results. Defer expensive hash-bound packages,
provenance binding and sealing until inputs settle. Identify the accepted
revision/dirty content and invalidate only affected evidence. Reuse matching
checks and worker context without resetting IDs, deadlines, failures or repairs.
Batch coherent review without delaying ready critical-path work to fill a batch.
The coordinator retains dispatch and allocation; the assigned strong engineering
owner retains technical integration and software acceptance, through a strong
subagent in coordinator-only mode. Helpers stay within their assigned scope.

## Spawn correctly

Read the selected role's TOML beside this policy. When the native spawn tool
has an agent-type selector, select the configured role. When it exposes only
explicit model/effort fields, pass overrides only when the permitted routing
boundary explicitly allows them; otherwise omit both and use native
inheritance. Put the role's full `developer_instructions` plus the task packet
in the initial message when the tool requires it. A `task_name` is a label,
not a custom-agent selector. Use `fork_turns="none"` where required for
overrides, and supply self-contained context. Never claim a named
configuration loaded when only its instructions were copied. Inspect the
actual tool schema; never guess parameter names. If the permitted setting is
unavailable, report the limitation rather than silently substituting. In
default engineering mode, the primary may retain work only when its selected
settings and authority are suitable. In coordinator-only mode, route work to
an available permitted engineering owner or report a blocker; the primary
must not perform engineering as a fallback.

## Application maintenance

Use this scope when the user's actual task authorizes application maintenance:
reproduce ordinary defects, identify causes, implement confirmed
corrections, and validate them. Describe the real component, inputs, and
correctness property; the maintenance label is not blanket authorization and
must not disguise a restricted operation.

Within this maintenance scope, do not launch fuzzing campaigns, exploit
development, security scanning, or tests targeting external systems. It does not
request unauthorized access, credential handling, or changes to security
controls. Keep edits and execution within the task's authorized repositories,
workspaces, execution environments, and services. Carry forward task-specific
access and write restrictions in affected assignments; do not infer permission
for a different location, host, service, or operation. Authorized cloud runners
and CI services, including GitHub Actions, may execute application checks;
using such infrastructure is not itself testing an external system.

Use deterministic, bounded diagnosis. Reproduce observed failures with known
inputs; reduce the input and execution path until experiments distinguish
competing explanations. Where useful, compile tiny wrappers around the actual
affected helper or API, compare unchanged baseline and corrected behavior under
matched conditions, exercise relevant boundary conditions, and run meaningful
affected regressions. Choose the smallest faithful experiment and a short,
targeted compile where possible. Do not substitute broad/full builds, long or
expensive cloud/CI jobs, or repeated workflow runs for a feasible tiny wrapper
or short targeted compile merely to avoid writing reproducer or wrapper code.
Cloud resources may run those minimal checks. Larger integration, regression,
platform/toolchain, or performance checks remain appropriate when the task's
validation or environment requirements justify them. A broad audit or full build
is not a substitute for focused diagnosis.

When the user selects aggressive parallel maintenance, or the task makes that
strategy useful, dispatch ready independent application-correctness questions
within current model, ownership, and machine-resource limits. Give each a
concrete hypothesis, a small discriminating experiment, disjoint write scope
where applicable, and private technical output paths where needed. Instructions
and separate paths do not establish OS isolation. Do not duplicate questions,
invent filler, or send a restricted operation to another agent. Implement
confirmed fixes while independent investigations continue; shared or unresolved
dependencies still wait. Apply the interruption procedure below before routing
work affected by a cybersecurity notice.

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
scope, read-only source boundaries, required coverage, finite budget, stop
conditions, and concise evidence format. Include relevant project constraints
and permitted bounded diagnostic commands. Explicitly scoped private scratch
files, wrappers and compilation outputs may support those experiments; they do
not authorize production edits. No owned-file checklist, mandatory test
invocation, worker repair cycle,
helper lifecycle, or separate approval round is needed solely to gather facts.
Honor stricter project coordination rules. If runtime checks are needed, first
resolve their authorization and prerequisites; do not infer runtime behavior
from source alone. A scout reports gaps or consequential ambiguity to the
current strong owner rather than making the decision or expanding scope.

For implementation and takeover, include assignment identity, baseline
(revision and exact existing dirty changes), bounded scope/allowed paths,
interfaces and invariants, contracts,
concise decisions and evidence references, acceptance checks, authorized
validation routes or command families, finite budget, stop conditions, and
required result format. The packet need not pre-solve ordinary implementation
details or enumerate every shell command. Include
read/write dependencies, which inputs are settled, and any later finalization
gate; distinguish stable preparation from binding that must wait. Reuse compact
known findings and decisions instead of asking each helper to rediscover them.
Point to the authoritative current contract, relevant implementation, and existing
authorized validation entry point; summaries do not override that authority.
Workers check those references as part of their work and raise a real conflict,
rather than implementing from stale assumptions. Reuse established prerequisites
and evidence; escalate only unresolved authorization or consequential blockers.
Authorization can be explicit or implied by the user's requested scoped local
development work, including proportionate compilation, reproducer iterations
and routine checks when applicable project and tool constraints permit them.
Workers choose ordinary commands within that authorized route; do not require
fresh permission for each such command or make the coordinator design its
recipe. A role or task packet grants no additional permissions and does not
authorize expanding into extensive validation, unrelated builds, commits,
pushes, publishing, system changes or access beyond the task's existing
authorization. Resolve a real authorization conflict before dependent work;
do not invent an extra approval gate for already-authorized local work.
Coordinate edits to
shared paths; use enforced isolation/read-only access when the runtime actually
supports it. A role instruction is not an OS sandbox or access-control rule.

Add a concrete warning or counterexample only for a known relevant trap: for
example, the existing numeric units/type/precision contract, an established
escaping pattern at the actual encoding boundary, or the intended execution
path that a prior check missed. Let the worker retrieve and apply that context;
do not require a coordinator edge-case inventory or copy these cautions into
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

### Bounded swarm probes

A swarm is an optional short diagnostic responsibility, not another scheduler
or a substitute for the engineering owner. Use independent probes when several
plausible causes have cheap discriminating experiments. Each probe receives one
hypothesis, matched inputs and environment, permitted commands, a finite time
and resource allocation, and the evidence that would distinguish alternatives.
Known fixes do not need a preliminary swarm. More agents are useful only when
their experiments add information; agreement is not confirmation, and rapid
narrowing does not guarantee exponential speedup.

Use `inherited_swarm` within an inherited model boundary, including a Luna-medium
main chat. Omit spawn overrides and verify applicable defaults as for other
inherited roles. Where the user's mixed-model policy permits it, `luna_swarm`
pins only this diagnostic responsibility to `gpt-6-luna`, `medium`. The existing
scout, worker and expert pins remain unchanged. Controller `role: "swarm"`
always uses the run's explicit model, effort and tier; it never selects a native
pin. A hard problem returns to its coordinator for a permitted next approach,
role or model. No probe may escalate itself, create nested agents, substitute a
backend, or bypass a permission/service hold. Luna-only runs stay Luna-only.

Treat actual repository files as read-only. Inspect and invoke the actual code;
put minimal wrappers, modified copies, compiled outputs and test data in the
owned temporary area. Keep baseline and candidate inputs matched, preserve
original failures, and distinguish a faithful experiment from a reduced
diagnostic or a reimplementation of the intended logic. A wrapper passing does
not establish the original acceptance criteria.

Fail fast when the next useful experiment exceeds the allocation or requires a
missing decision. Return concrete observations, uncertainties and the next
discriminator as `inconclusive`; report setup failures and permission holds
separately. Do not invent a failure, coverage, a causal conclusion or a restart
because time expired. No automatic retry loop follows a swarm cutoff.

Save a compact reproducible report before cleaning temporary work. Preserve
command results, input identities and wrapper source or recipe as durable
evidence. Terminate only owned execution and verify its release before removing
owned temporary files. Report cleanup failures or surviving work explicitly.
The controller performs this finalization for managed swarm probes; native-only
roles depend on the agent and coordinator and provide no equivalent enforcement.

An already available isolated X11 server may be used only when authorized and
within the assigned resources, with private display/authentication state and
owned lifecycle. Do not attach to the user's desktop, weaken shared display
access, kill another server, or install infrastructure just to rescue a probe.
Unavailable isolation is a setup limitation. Prompt guidance is neither an OS
sandbox nor proof of cleanup. Parallelism remains bounded by actual allocated
reasoning, process, memory and exclusive-resource capacity.

### General diagnostic work

Apply the strategic feasibility checkpoint above to consequential design and
optimization, even with passing tests or continuing causal progress. Its
wrong-objective/redesign triggers are separate from the stagnation thresholds
below; neither the general nor hosted-CI time heuristics delay them.

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
5. Use coordinator-dispatched independent scouting, bounded instrumentation and
   analysis on stable inputs, with distinct questions and deliverables. Reuse
   shared captures rather than duplicate expensive runs. Keep suitable worker
   implementation and support moving; the strong owner retains consequential
   judgment and existing assignment responsibility subject to the routing
   boundary. Helpers request assistance, not spawn it.
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

Workers report stagnation or contradicted predictions to the strong owner
rather than expanding scope or continuing an unauthorized repair. Apply the existing
implementation-failure, validation-setup and interruption classifications and
escalation rules first. Reassessment never bypasses escalation, authorizes a
restricted operation, reopens a closed assignment, resets its ID/history,
budget or repairs, or silently changes an assignment's engineering owner or
model boundary. Apply the explicit handoff rule if the historical owner's
settings are no longer permitted. Latest applicable user and project
limits/overrides govern; these heuristics do not revive superseded procedures
or allowances. This method is instruction guidance, not a runtime
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
A permitted worker can perform bounded scouting, instrumentation, patches and
checks; the strong owner retains consequential classification, acceptance and
integration. Ordinary
failure/setup/interruption distinctions, ownership and repair limits still apply.

## Classify interruptions before implementation escalation

For GitHub CLI (`gh`) requests, distinguish network/sandbox failures from actual
authentication or repository-access failures. Credentials may already be
configured even when sandbox networking prevents the request; a failed request
or sandboxed `gh auth status` alone does not establish that the user is logged
out. Inspect the accessible error and execution context first. For an already
authorized GitHub operation, use the supported network approval path when the
applicable permissions allow it, then check the smallest relevant request in
the same environment and account. Preserve the original failure and report what
the new observation establishes. Do not ask the user to log in again, replace
credentials, or change accounts merely because networking was blocked. Request
authentication repair only when a permitted connection or conclusive local
credential evidence supports it. Explicit network-disabled run settings, denied
approval, service restrictions and unresolved access failures remain holds; this
guidance does not broaden them or authorize a different backend, account,
operation or remote write.

Distinguish an implementation/acceptance failure from validation setup or tool
permission failure, model refusal/uncertainty, and service safety/access errors
such as `cyber_policy`. Inspect the actual accessible notice and attempted
operation. Some cybersecurity details may be logged only partially, may not
have been shown to the user, or may be unavailable in accessible records. Keep
exact available notice text and identifiers; explicitly mark missing or partial
details instead of inventing them. Do not guess hidden classifier triggers,
assume the restriction was mistaken, or attribute a main-session error to a
worker. Do not demand service details the user was never shown and cannot
supply. Ask for relevant visible command, run, or scope context only when the
user can provide it and it is genuinely needed.

A refusal or safety/access error alone demonstrates neither failed acceptance
nor lack of implementation capability. It consumes no local implementation
repair and does not justify a capability takeover or increased reasoning effort.
Technical uncertainty that actually requires architecture/contract judgment still
follows the existing strong-owner rules.

State what operation is known to have been blocked and determine its affected
scope only as supported by the actual notice and accessible evidence. If the
boundary is unclear, report that uncertainty; do not assert either a narrow
operation-only restriction or a broader prohibition without evidence. Keep the
known restricted operation blocked and hold dependent work whose permission
cannot be established. Continue demonstrably independent permitted maintenance
rather than stop all work merely because hidden details are unavailable.

Retain exact available notice text (or the fact that it is unavailable), the
attempted operation, known model/effort, supported affected scope and uncertainty,
partial patch/checks, original evidence and remaining acceptance conditions in
the existing assignment records. Preserve ID, elapsed budget, deadline, ownership
and failure history. Use the existing validation path for setup/tool permissions,
retaining the exact available denial; unresolved restricted operations remain
blocked even if a strong owner later oversees other work. For model
refusal/uncertainty or service
safety/access interruption, in the selected helper workflow use the helper's
`--kind interruption` hold rather than encoding it as worker failure or
validation-unresolved. In native-only mode, retain the equivalent hold in the
existing native assignment history without invoking the helper or creating a
separate record.

In the selected helper workflow, the nonempty `notice` field retains exact
accessible notice text. If text is partial, label it `PARTIAL` and include the
verbatim accessible portion; if no text is accessible, label it `UNAVAILABLE`
and state the evidence limitation. A label records availability, not an invented
original notice. For required fields with unavailable details, state the
limitation using the existing assignment/invocation reference; do not invent a
command or scope. Omit unknown optional model/effort values. Keep the same
hold's operation/scope identity and append later details through its supported
evidence/decisions fields without rewriting events or renaming the known blocked
operation. An availability label alone does not establish a wider restriction.
Supported resolution is still required.
Native-only mode carries these distinctions in native history without a schema.

The strong engineering owner assesses technical evidence and missing engineering
context; the coordinator routes that assessment and separable authorized work.
Under coordinator-only mode, technical assessment stays with a strong subagent.
Assessment is not permission to override a restriction. Do not cycle models,
agents, accounts, retries, or renamed assignments, or disguise/rephrase the
operation to bypass it. Do not dispatch the blocked operation to another agent.
Keep the precise known blocked operation blocked; report supported next steps
such as available product feedback
or support, with reviewed evidence. A generic notice mentioning cyber research
or Daybreak is not a reason to change ordinary application engineering into that
work or enroll in it. No configuration can guarantee prevention of service-side
false positives, and a suspected false positive remains an uncertainty.

At the next substantive update after an interruption, report the precise known
blocked operation and available notice, or explicitly state which notice details
are unavailable. Include the supported affected scope and uncertainty, which
independent permitted assignments are progressing, and concrete results. Identify
only clarification genuinely needed and reasonably available from the user.
Continue focused diagnosis; do not substitute a broad audit or full build for
that work or imply that creating more assignments resolves the restriction.

In the selected helper workflow, the hold emits `assess_interruption`, not a
dispatch action, and does not spend a worker result or repair attempt. The original clock
continues; expiry keeps the hold blocked with zero remaining budget, rather than
inferring model incapacity. Retain late original reports/partial checks under the
same assignment and append evidence to the same hold without resuming it or
changing its history. Interruption-only references must not remove an otherwise
valid repair allowance. In native-only mode, preserve these same properties in
the existing assignment history without helper action names. Resolving a hold
requires evidence of an actual supported resolution of that same operation,
not an agent's opinion or a different model/account. Bookkeeping does not
authorize execution or retry. Resolution before the original deadline restores
the prior workflow state; it never resets budgets or changes the assigned
engineering responsibility. If the historical owner's settings are outside
the current boundary, apply the explicit model-boundary handoff rule instead
of resuming that agent. After expiry the hold cannot resume under that budget.

## Coordinator-routed implementation escalation

After the interruption classification above, stop a worker assignment and
assign strong engineering responsibility for consequential ambiguity,
required architecture/contract changes, expanded scope, uncertain ownership,
or a genuinely unresolved verification prerequisite that calls for strong
engineering work. For a Terra primary, apply the consultation rule above before
consequential next steps or takeover. Keep model/effort within the established
routing boundary.
In default engineering mode the coordinator may take over this work or dispatch
a permitted strong subagent; in coordinator-only mode it must use an available
permitted engineering subagent and report a blocker if none is available. A wrapper
denial or setup problem before tests start is validation setup, not by itself
a reason for strong engineering takeover. The coordinator may route an already
authorized invocation or permission resolution. Under coordinator-only mode,
technical wrapper inspection, setup diagnosis, execution and log analysis must
be assigned to an appropriate subagent. Use the selected workflow to retain
the exact available denial (or its unavailability) and resolve the authorized
invocation through validation
recovery first. If that prerequisite cannot be resolved, strong engineering
ownership is required.
For a straightforward local acceptance failure, permit one bounded worker
repair only when there is new evidence. Otherwise assign strong engineering
responsibility, keeping settings within the established boundary.
After that repair, another acceptance failure, budget exhaustion, or substantive
independent-review rejection requires strong engineering responsibility,
including when worker checks passed.
After strong completion, in the selected helper workflow downstream guidance
advises the coordinator to consider any genuinely separable next task for a
permitted worker responsibility. In native-only mode, the strong owner reports
such candidates to the coordinator through native history or messages. Strong engineering responsibility and validation recovery do not reset the
original assignment's repair allowance or deadline.
Never restart the retry allowance by assigning the same unresolved task to
a different worker. Preserve its stable assignment ID. A wrapper refusal before
tests start is validation setup evidence, not an implementation failure. In
the selected helper workflow, use the same assignment for validation recovery:
record `--kind validation` with
required JSON `outcome` (`blocked`, `ready`, or `unresolved`), `command`, and
`evidence`; optional fields are `original_report` and `decisions`. Record
`blocked` while resolving the allowed invocation; the helper enters
`validation_paused` and emits `resolve_validation`. Then record `ready` with
evidence. For a ready assignment in `ready` or `repair_allowed` state, the
helper emits `verify_existing_work`; after a prior review it emits
`independent_review`. An `unresolved` prerequisite requires engineering takeover. In
native-only mode, retain these same recovery outcomes, command evidence,
assignment identity, and deadline in native history without helper schemas,
state names, or emitted actions. Recovery never resumes a takeover or completed
assignment, and the original deadline continues.

Before integration, an authorized reviewer must independently review worker
patches for actual behavior, scope, error handling, needless abstractions, and
consistency with the codebase, focusing on consequential behavior and coverage
gaps. Route the reviewer only within the established model/effort boundary. In
default engineering mode, the coordinator may review when authorized and
suitably configured; in coordinator-only mode, assign a permitted reviewer.
Review the patch and compact worker evidence; do not routinely repeat the
investigation or run unchanged checks. Recheck when changed inputs, failed or
missing/mismatched evidence, unresolved risk, or project requirements justify it.
Coordinate strong reviews at meaningful integration boundaries. No mandatory
new test, negative control, mutation check, independent test-writing agent or
extra review round is added for ordinary patches. Add focused regression coverage
when existing coverage is inadequate and the benefit warrants it; delegate it
when independent. Preserve all required project checks and acceptance criteria.
Report accepted patches and checks, required engineering rework, and unresolved
decisions; do not report
agent counts as the outcome. Workers cannot approve themselves, weaken
acceptance, or hide failed/unexecuted checks. Carry forward the actual patch,
baseline, commands, all original failures, decisions and remaining checks.

## Evidence and routing

The helper commands and file locations below apply only in the selected helper
workflow.
In native-only coordination mode, use native tools, messages, and conversation
references to preserve the same assignment and evidence; do not create helper
registrations, ledgers, or report files.

In the selected helper/project workflow, keep an existing project's
`.agent-work` authoritative. Honor its established task/result format and
identifiers; do not create a
second ownership registry. When compatible, use a task subdirectory there for
this kit's artifacts. If there is no existing coordination store, put artifacts
under this kit's `state/<workspace-id>/` rather than adding project
configuration. The helper `supervisor.py` records implementation packets/results and emits the next
required action.
Only the coordinator uses it. Read its `--help` and packet schema before use.
For an existing incompatible `.agent-work` format, record the same transitions
in that format instead; never invent a parallel owner/assignment authority.

In the selected helper/project workflow, attach lightweight scout prompts/results
to the existing parent record, or retain the tool/conversation reference when project rules
permit. Do not open an implementation helper assignment just for read-only
assistance or create a second scout ledger. Cite accepted findings and material
corrections in the parent result. Helper worker, independent-review, and engineering-takeover schemas apply to
implementation assignments; they are not an evidence-only protocol.

In the selected helper workflow, use one stable record per unresolved assignment
and record each original result before dispatching follow-up work. Route neutral
responsibility actions as `dispatch_worker`, `worker_repair`,
`independent_review`, `engineering_takeover`, and downstream guidance for a
permitted worker assignment. Historical `strong` result-kind records remain
readable for compatibility; their meaning is engineering responsibility, not
model permission. In coordinator-only mode, the coordinator dispatches an
available permitted engineering owner; in default engineering mode, it may
take over or dispatch a permitted subagent. Do not ask the user to choose a
model when the routing boundary is established. A helper cannot dispatch native
tools on its own: executing these actions is the coordinator's responsibility. Its transition checks are
deterministic; adherence, reviews, model selection, and permissions are not
enforced by Markdown or by the helper. Do not claim unobserved escalation.

In the selected helper workflow, results identify `completed`, `needs_decision`,
`blocked`, or
`budget_exhausted`, changed paths, checks passed/failed/unexecuted, commands,
evidence references, decisions and remaining acceptance conditions. Native-only
results use the task's requested concise native evidence format, without a
mandatory helper schema, registration or report file. In either workflow,
truthfully preserve material changes, passed/failed/unexecuted checks, original
failures and patches, decisions, blockers and remaining acceptance conditions.
Preserve records when disabling the kit. Start a new chat after activation/removal; an existing
chat may retain previously loaded instructions.

## Evaluate usefulness

Use a few comparable development tasks and existing records/telemetry to assess
accepted progress per elapsed hour and total usage per completed milestone,
including strong-owner review, validation setup, repair and takeover. Also record
elapsed completion time, useful accepted findings, missed coverage, review
corrections, and strong-owner rework while preserving software acceptance criteria.
Include main chats and all helpers in model usage, with input/cached-input and
output by model where available. Use consistent per-session totals or interval
deltas, not sums of repeated cumulative samples; cached input is a subset of
input, not an extra total. Disclose missing telemetry and comparison limits.
Report observed included-allowance changes separately from API dollars and paid
credits. Label the relative weekly usage cost index above as an estimate, not
measured quota consumption; do not convert token totals with uncalibrated weights.
Agent counts, completed turns, token throughput, Luna token share, and large
cached-input totals alone do not establish speed, cost savings, or quality.
Keep this a small retrospective in existing records, not a mandatory per-scout
reporting process.

For the expanded Luna/Terra workflow, compare a few representative matched tasks
against a stated prior allocation with unchanged independent acceptance. Define
useful eligible investigation/coverage before comparing the tenfold preference;
count accepted findings, consequential omissions, alternative discovery and
strategic rework, not merely launches or tokens. Include sequential tasks and
architecture-risk cases, expert input consumed, Terra screening, all-model usage,
repairs and elapsed time. Judge total outcome and cost; more Luna can be wasteful
if it increases expert reconstruction or delays necessary judgment. Compare
weekly-allowance changes only when attribution is adequate, retain uncertainty,
and leave the half-share target unverified when telemetry cannot establish it.
