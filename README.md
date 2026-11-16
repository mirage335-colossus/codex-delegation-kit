# Codex delegation kit

This kit installs an explicitly invoked skill for bounded coding and research
coordination in Codex. Select `$delegation-kit` or its skill-picker entry for an
assignment. Ordinary requests, quoted mentions and reading this repository do not
activate DK. Its workflow guidance below applies only within that active scope.
It preserves the primary model and its settings. Choose the
coordination mode that fits the task: native-only agents, the advisory helper,
or the explicitly selected Python controller. Installing the kit does not
start a controller, enable it for a task, or change model, effort, service tier,
or concurrency settings.

The roles provide focused source discovery, scientific research, bounded
implementation, and independent review. Use the pinned roles only when the user's
current
instructions and applicable routing authorization permit them; otherwise use
the inherited roles and preserve the selected primary, effort, service tier,
and configured pins. A role name or cost estimate does not grant model
permission. The [policy](policy.md) is the canonical guide to routing,
coordination, review, evidence, safety boundaries, and interruptions.
Denied or unavailable capabilities remain permission holds; they do not
authorize a model, account, or backend fallback.

**Practical numerical work starts with the lowest useful arithmetic precision.**
Automatic mode should maximize useful capacity on challenging supported workloads
and prevent backlog; higher precision needs a demonstrated application benefit or
an explicit requirement. Compare complete algorithms, raise precision locally,
and preserve simple user overrides. Avoid arbitrary FP64-agreement or universal
loss gates and unrequested easy-case efficiency objectives. See the
[practical precision policy](policy.md#practical-numerical-precision).

**For modem, signal-processing, and other compute-intensive code in native
applications, prefer C++ or a similarly integrated native approach.** Improve
the existing pipeline before introducing a split Python/process architecture;
account for thread scheduling, overlapping batches, shared buffers, cross-chain
pruning, and reproducible GPU/cloud testing of the same production implementation.
Separate native test processes are compatible with this preference; stricter
project contracts can prohibit a second DSP implementation even for benchmarks.
See the [native numerical processing policy](policy.md#native-numerical-processing)
for the reported engineering lessons, evidence required for exceptions, and
appropriate uses of Python.

For repeated or hardware-constrained experiments, the optional
[cloud experiment guide](CLOUD.md) explains when cloud may save total time and
the standing compute authorization and private cost and cleanup controls.
Preserve task scope and normal service permissions.

**GPU selection defaults to RTX PRO 6000 Blackwell for suitable tensor and
highly parallel FP32 development, hardware-utilization demonstrations, and faster
testing.** Agents must explain a choice of A100, RTX A5000 or another older GPU.
See the [selection criteria and exceptions](policy.md#gpu-selection-and-performance-evidence)
for demonstrated precision needs (especially FP64), exact variants, software compatibility and
measured speedups.

For substantive tasks within an explicitly activated DK assignment, obtain the policy's initial `astra_initial`
(`gpt-6-astra`, `ultra`) consultation before investigation or planning; clearly
trivial mechanical requests are exempt. When the main chat proposes to stop
advancing a substantive user request and return control to the user, submit that
stopping decision to the separate
[mandatory completion review](policy.md#mandatory-astra-completion-review) by
`astra_expert` (`gpt-6-astra`, `ultra`). The trigger is the decision to stop,
regardless of response wording or whether completion is claimed. Before a final
response ends work, require a current applicable review and resolve its feasible
authorized follow-ups. The review inspects actual evidence and agent findings,
searches existing solutions, considers alternatives and performs relevant external
research. Preserve explicit stops, real blockers and project qualification limits.
The reviewer checks the actual requirements, practical configurations or
workarounds, coupled resource limits when relevant, and a next action with verified
prerequisites. The owner closes feasible authorized validation gaps, preserving
failures and distinguishing public results from evaluator data or forecasts.
The native engineering roles and controller-built prompts carry matching
execution/evidence guidance; the controller keeps its separate run policy and does not invoke native
Astra reviews. This is instruction-level guidance, not a runtime interceptor or
compliance guarantee. Ordinary fixes need no new arithmetic or evaluation phase.

In a suitable task, assign a scout to gather source evidence, a worker to make
a bounded change, and an independent reviewer to assess the patch and its
evidence. Keep consequential design and acceptance with an authorized owner.
The policy explains when to use each role and how to retain original failures,
holds, and review requirements through a continuation.

For consequential scientific work, the
[research and development workflow](policy.md#scientific-literature-research-and-development-uptake)
calls for sustained research during ordinary development when important
scientific gaps could change the work; the user need not ask for research.
Native authorship, research leadership and independent scientific critique use
the lean `sol_researcher` role when it is available in the running chat and its
Sol/ultra settings are authorized. It owns no implementation, architecture approval
or main-chat completion decision. If the role is unavailable or a harder model
boundary excludes it, use an eligible supported role such as `inherited_reviewer`
and disclose the fallback. Source registration alone does not establish runtime
availability. Start its brief with
the scientific knowledge to develop and reusable account; retain the complete
development request, envelope, constraints and factual source as application
context. Use a self-contained supported fresh context where available, without
claiming that another agent identity guarantees isolation. A broad task needing
substantial new grounding gets two independent full-problem inquiries within
one shared allowance. Each develops its own questions and evidence; preserve
both substantive initial accounts before sharing their findings or an emerging
engineering plan. At this discovery checkpoint, the research lead derives a
revisable outline of scientific subjects from the problem and inspected literature.
Inadequately grounded subjects receive focused investigations, each the author's
sole substantive research assignment in a separate working context; an existing
context dedicated to that subject may continue. Each investigator receives the
whole problem and constraints, its subject question and boundaries, relevant
source leads and factual context, and adjacent-subject relationships. It develops
the scientific account before a compact integration handoff. The lead integrates
subject accounts and owns unresolved relationships; the engineering owner owns
the implementation plan. The coordinator can schedule subjects sequentially
within the shared allowance and staffing limits. Adequate research is reused,
and routine questions need no such division. The lead retains scientific
authorship for material subjects it does not delegate, without recursively
commissioning another research pair.
Broad assignments define coverage across the relevant operating envelope and
require explanatory and discriminating depth in each material domain. Authorized
reference calculations or public-observation checks support consequential
quantitative choices; independent review returns useful depth gaps for correction.
Subject investigators choose useful follow-ups without waiting for the main chat to
supply missing branches, papers or tests. The lead integrates their accounts
without replacing them with a compact plan summary, and the task owner retains
responsibility through review and uptake. Settled engineering can continue.
The scientific critic first uses bounded primary-literature discovery to scope
questions from the original problem, then reconciles the accounts against that
source-informed scope. It receives the initial discovery and subject accounts
and factual source context while engineering-plan artifacts and prior tranche approvals
remain withheld through its scientific disposition. Early architecture review,
when needed, uses a separate existing responsibility or waits for its dependency.
In the existing reconciliation, retain every material inquiry and critic question,
including unanswered ones, and map each conclusion and its conditions to the
distinctions that the performed evidence actually resolves. A narrow
successful example does not close broader alternatives. Before accepting a
deployment or calibration boundary, inspect relevant sources more deeply or
perform useful representative comparisons when feasible without the missing
target inputs. Corrections return to subject authors; the owner and lead
retain specific unresolved conclusions and verify engineering uptake. Subject
division adds no model permission or recursive main-chat gate. It preserves
genuine limits
without treating a ready first step as full
scientific coverage.
It combines foundational and recent primary literature, competing mechanisms,
contrary evidence and checks for equivalent existing capabilities. Detailed
research feeds a compact source-to-decision handoff that workers and reviewers
reconcile with current code and new findings. Routine settled work needs no
literature campaign. `_ref/` and `_appraisal/` remain user-curated and require an
explicit request to write there; agent research uses an authorized `research/`
location or existing task evidence. The dedicated role is native-only; the
controller keeps its existing responsibilities and uniform run-selected models,
and its research guidance does not supply this lean role. Neither route gains
network or tool permissions from this guidance.

Research accounts contain authored explanations, comparisons, useful checks,
conclusions and citations. Downloaded papers, datasets, copied third-party source,
extracted text and raw tool responses belong in authorized outside-repository
scratch or a narrow cache such as `/.research-artifacts/`. Establish and verify
effective repository `.gitignore` coverage before writing any acquired content,
including staging and final paths. Global exclusions alone are insufficient;
tracked files remain tracked despite ignore rules. Keep `research/` available for
authored knowledge and preserve the curated-directory boundary. Existing acquired
material needs a deliberate retention or migration decision, not automatic deletion.

Research authors checkpoint useful findings, source access, completed checks and
open questions as work progresses. Guard interruptions preserve that handoff and
the exact failure; supported continuations reuse it under the original holds,
budget and deadline. Independent permitted work continues, while dependent work
waits for actual resolution. Preserved partial findings are not automatically
accepted, and neither a user stop nor a sealed historical outcome is overwritten.
These native-agent duties are prompt guidance, not an interceptor for arbitrary
tool calls or filesystem writes. See the [research policy](policy.md#scientific-literature-research-and-development-uptake)
and [interruption procedure](policy.md#classify-interruptions-before-implementation-escalation).

The optional Python controller adds concrete safeguards: durable bounded public
message checkpoints, recovery context for explicitly resolved agent holds, and
artifact-path admission for new state, owned captures and source-bearing evidence.
The retained study relay checks both staging and final payload paths. Existing
state access and cancellation receipts remain available after an ignore-rule
change so storage checks cannot strand owned execution. These are scoped
preflight checks, not a filesystem sandbox or a scientific acceptance decision.
See the [implementation lessons and limits](research/interruption-and-storage.md).

Evaluation protocols, results and limitations are recorded in the
[depth and uptake study](studies/scientific-depth-2026-11-14/README.md) and the
[autonomous research study](studies/autonomous-scientific-depth-2026-11-14/README.md).
These records preserve original failures, source and resource limits, and the
scope of each conclusion. Source-delivery tests alone do not establish comparable
scientific depth, reliability or token savings.

For included Desktop Codex allowance, the user's current planning index is
Luna 0.1, Terra 1, Sol about 10, and Astra about 20. It is a unitless estimate,
separate from API prices and purchased credits; see the [weekly usage cost
definition](policy.md#weekly-usage-cost).
If an older installed policy lists Luna as unknown, the current user estimate
above supersedes that value.

## Parallel challenges when work stalls

An optional assignment pattern for the policy's [diagnostic
reassessment](policy.md#general-diagnostic-work) is to obtain independent
challenges to the current approach:

- Give each helper the original user objective, stable source/revision and input
  provenance, constraints, observed failures and raw observations, plus relevant
  authorization/scope facts and source access, without the current recommendation.
  Use a fresh/context-limited branch so the candidate is not already in its
  history. Ask it to retain a proposed contract, checks and feasible next action
  before sharing the current recommendation; then reconcile contrary evidence
  and run an authorized discriminator for a consequential discrepancy. Assign
  different questions about requested behavior and the existing contract: what must change,
  what behavior must remain true, or which materially different counterexample
  separates plausible causes. Use helpers when unresolved uncertainty warrants an
  independent view; skip the round when the next action is clear. Ask helpers to
  challenge the source and scope of consequential
  acceptance/stopping criteria as well as the implementation; independent
  agreement is not validation.
- Ask for a source-grounded finding and an executed, authorized discriminator
  where feasible. A useful challenge can reject the current framing; agreement
  and additional suggestions alone do not establish progress.
- Keep the owner advancing independent work while helpers investigate. Apply
  supported findings to the next experiment or implementation, or explain why
  they do not apply. Wait only where a decision depends on missing evidence.

Select parallel branches only when they can add distinct information; a settled
fix needs no extra challenge round. Existing routing, ownership, budgets and
acceptance apply. An end-to-end exercise in this development demonstrated
fresh-context independent contract reasoning, reconciliation against a candidate
repair, an executed counterexample, owner correction and independent acceptance.
This evidence describes that exercised pipeline only; it does not establish general
reliability or that adding reviewers alone improves outcomes. Record whether the
branch actually began without candidate context and what authorized check/result
followed; do not infer success from helper availability or agreement.

## Choose a mode

| Mode | Use it when | Where state lives |
| --- | --- | --- |
| Native-only | Native agents and the coordinator are sufficient, or this mode is selected | Native task history |
| Advisory helper | The coordinator wants helper actions and evidence guidance | Existing evidence files; the helper does not dispatch work |
| Controller | The user explicitly selects managed dispatch and scheduling | One SQLite run directory, owned executions, and retained evidence |

These modes are independent of model routing and concurrency. Controller runs
do not create native subagents. Read [coordination modes and controller
operation](policy.md#applicability-and-operating-modes) before selecting a
workflow. For a selected controller run, start with the [public run
format](ORCHESTRATION.md#public-run-format), the [engineering run and task
format](ORCHESTRATION.md#engineering-run-and-task-format), and the [small
operator surface](ORCHESTRATION.md#small-operator-surface). The controller is
opt-in and has no detached service.

For an authorized run, `controller.py --run RUN start inventory.json` creates
the run and starts its foreground loop. Use the same run directory for status,
results, pause, recovery, or stop operations. A completed worker turn is a
proposed result; check the actual evidence and required independent acceptance.

## Requirements

Git is needed to clone the source. The installer, helper, and controller use
Python 3.11 or newer and the standard library. Linux is required for the
controller's owned process cancellation; Windows controller support is not claimed.
On Windows, run the controller in WSL. The
managed agent backend also needs a compatible Codex app-server executable and
authorized account and model access. A model appearing in a catalog does not
establish access.

## Install, update, and disable by scope

Use Python 3.11+ from the source checkout. Every command previews changes unless
`--apply` is added. Installing makes the skill available; it does not activate a
DK assignment, launch a controller, or authorize project changes.

| Scope | Preview install/update | Preview uninstall (explicit target) |
| --- | --- | --- |
| Global Codex home | `python3 install.py --home /path/to/codex-home` | `python3 uninstall.py --home /path/to/codex-home` |
| One repo or working folder | `python3 install.py --project /path/to/repo` | `python3 uninstall.py --project /path/to/repo` |
| Collection and named child repos | `python3 install.py --tree /path/to/collection --repo podboss --repo podprocessor` | `python3 uninstall.py --tree /path/to/collection` |

Review the preview, then repeat the same command with `--apply`. For example:

```sh
python3 install.py --tree /path/to/podcast_feed --repo podboss --repo podprocessor --apply
python3 uninstall.py --tree /path/to/podcast_feed --apply
```

Installation without a scope option uses the global Codex home. Uninstall without
a scope option discovers its target using the rules below.

Global installation uses `CODEX_HOME`, defaulting to `~/.codex`, and places the
runtime in `delegation-kit/`, the explicit-only skill in `skills/delegation-kit/`,
and marked role registrations in `config.toml`. It is global to sessions using
that home, not to the entire machine. Windows and WSL can use different homes.
Verify that the intended runtime discovers the installed skill; a compatible
per-home skill loader is required. The installer prints all destinations.

Project installation uses `<project>/.codex/delegation-kit/` for the runtime,
`<project>/.codex/config.toml` for role registration and
`<project>/.agents/skills/delegation-kit/` for the skill. Project configuration
must be trusted and loaded by the runtime. Existing project `AGENTS.md` files
are never edited.

A tree root need not be a Git repository. Tree installation registers the same
runtime at the root and at each explicitly named `--repo` child Git repository.
Paths are relative to the collection and may contain intermediate folders.
This supports both a chat opened at `podcast_feed` and independently opened
PodBoss/Processor chats without changing Git-root discovery or global settings.
It does not scan or silently install into every descendant. To add members,
rerun with the complete desired list. Removed members lose only owned activation
files. Disable uses the recorded members, so `--repo` is not needed for uninstall.
Choose one scope for a work area; overlapping installations can expose duplicate
skill names or competing role registrations.

Fresh installs do not add DK instructions to global `AGENTS.md`. Upgrades remove
only the recognized, unchanged DK-managed legacy block while preserving user
text, unrelated settings, role pins and evidence. The current 26-file bundle and
all published 8/11/17/18/20/21/22/23/24-file inventories are supported. Edited or
unowned skill destinations and managed blocks are refused instead of overwritten.
Start a fresh Codex session after upgrading so old automatic instructions are no
longer retained in context. Installation flags select storage/discovery scope;
skill invocation still selects the assignment scope in each conversation.

Disable removes only owned skill-discovery files and role-registration blocks.
It retains runtime files, installation backups and execution evidence. It does
not remove your project or global instructions, or stop an existing controller.
Use that run's `controller.py --run /path/to/run stop` or `drain` separately when
authorized. Uninstall discovers the installation and its recorded scope without
requiring `--home`, `--project`, or `--tree`:

```sh
# From a repo, collection root, or named tree member (including a subfolder):
python3 /path/to/codex-delegation-kit/uninstall.py
python3 /path/to/codex-delegation-kit/uninstall.py --apply

# An installed utility identifies its own installation from any working folder:
python3 /path/to/repo/.codex/delegation-kit/uninstall.py --apply
```

The installed utility's own manifest takes priority. When using the source
utility, discovery checks the working folder and its ancestors for an owned skill
runtime pointer or local manifest, stopping after checking the nearest Git root.
Both `.git` directories and `.git` files (worktrees/submodules) are boundaries.
If no local installation is found before that boundary, discovery refuses to
select an ancestor or global installation. A registered tree member's own pointer
can identify its shared runtime outside the repo; an unlisted or nested independent
repo cannot discover the parent tree. The non-Git collection root finds its own
pointer directly. If no Git boundary is reached and there is no local installation,
discovery uses `CODEX_HOME` (default `~/.codex`).

The manifest supplies project versus tree scope and every tree member; the user
does not repeat that information. A disabled local manifest remains the target for
repeat uninstall, so it does not fall through to another installation. After a
tree member's pointer is removed, repeat uninstall from that child reports no
local installation; use the retained installed utility or the collection root for
an idempotent repeat. Invalid local pointers or ownership records are refused.
Discovery never scans unrelated folders or attempts to remove every installation.
For a custom global home, run its installed utility, set `CODEX_HOME`, or use the
explicit `--home` option. Explicit scope options in the table remain available to
select a different target. The preview prints the discovered scope and runtime
path before showing changes; review that target before adding `--apply`.

Global installation and publication require
separate authorization; tests use disposable scopes, never the actual user home.

For a source-checkout verification against a compatible Codex executable, see
[`examples/verify_skill_invocation.py`](examples/verify_skill_invocation.py). It
checks all three installation scopes with a local synthetic provider and no real
model inference; it does not install into your actual Codex home or projects.

## Initial use and follow-ups

```text
$delegation-kit Investigate the CLARE issue across PodBoss and Processor.
Use synthetic fixtures; do not deploy or initiate paid processing.
```

Native-only coordination is the default. Related follow-ups such as "also test
changed downloads" or "address the review finding" reuse the active assignment
and its applicable initial consultation. Status questions do not restart reviews.
Updated substantive work needs current applicable completion review before it
ends. A final response alone does not terminate related follow-ups. "DK off" or
an explicit end stops DK requirements immediately, with no exit review. Unrelated
work remains inactive unless separately invoked. These are ordinary instructions,
not new slash commands. Activation does not authorize additional actions.

Fresh blank chats are inactive. Resumes and forks retain the assignment shown in
their history at that point. Forking before activation or after off is inactive;
forking an active assignment retains that scope. Later branch changes do not
propagate, and copied reviews do not validate new changes. Reconcile shared files,
live jobs and budgets before executing in a fork. This is instruction guidance,
not automatic fork detection or a hard dispatch boundary. Explicit standalone
role requests remain possible without enabling the entire DK workflow.

## Installed files and license

The runtime bundle has 26 files: this README, `policy.md`, `CLOUD.md`,
`ORCHESTRATION.md`, `supervisor.py`, `install.py`, `uninstall.py`,
`controller.py`, `controller_store.py`, `execution.py`, `agent_backend.py`,
`scheduling.py`, `engineering.py`, eleven role TOML files in `agents/`, and the two
source skill files under `skills/delegation-kit/`.
`CONTRIBUTING.md`, tests, examples, and verification materials are source-only
and are not installed. The policy describes expected behavior; each program
enforces only its documented checks.

Author and CC0 affirmer: **mirage335**. This repository is dedicated to the
public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
