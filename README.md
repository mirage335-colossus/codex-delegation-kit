# Codex delegation kit

This kit adds optional role guidance and tools for coordinating bounded coding
work in Codex. It preserves the primary model and its settings. Choose the
coordination mode that fits the task: native-only agents, the advisory helper,
or the explicitly selected Python controller. Installing the kit does not
start a controller, enable it for a task, or change model, effort, service tier,
or concurrency settings.

The roles provide focused source discovery, bounded implementation, and
independent review. Use the pinned roles only when the user's current
instructions and applicable routing authorization permit them; otherwise use
the inherited roles and preserve the selected primary, effort, service tier,
and configured pins. A role name or cost estimate does not grant model
permission. The [policy](policy.md) is the canonical guide to routing,
coordination, review, evidence, safety boundaries, and interruptions.
Denied or unavailable capabilities remain permission holds; they do not
authorize a model, account, or backend fallback.

For repeated or hardware-constrained experiments, the optional
[cloud experiment guide](CLOUD.md) explains when cloud may save total time and
the standing compute authorization and private cost and cleanup controls.
Preserve task scope and normal service permissions.

**GPU selection defaults to RTX PRO 6000 Blackwell for suitable tensor and
highly parallel FP32 development, hardware-utilization demonstrations, and faster
testing.** Agents must explain a choice of A100, RTX A5000 or another older GPU.
See the [selection criteria and exceptions](policy.md#gpu-selection-and-performance-evidence)
for precision (especially FP64), exact variants, software compatibility and
measured speedups.

For substantive tasks, obtain the policy's initial `astra_initial`
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
The native roles and controller-built prompts carry matching execution/evidence
guidance; the controller keeps its separate run policy and does not invoke native
Astra reviews. This is instruction-level guidance, not a runtime interceptor or
compliance guarantee. Ordinary fixes need no new arithmetic or evaluation phase.

In a suitable task, assign a scout to gather source evidence, a worker to make
a bounded change, and an independent reviewer to assess the patch and its
evidence. Keep consequential design and acceptance with an authorized owner.
The policy explains when to use each role and how to retain original failures,
holds, and review requirements through a continuation.

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
controller's owned process cancellation; Windows support is not claimed. The
managed agent backend also needs a compatible Codex app-server executable and
authorized account and model access. A model appearing in a catalog does not
establish access.

## Install or update

Clone the repository and inspect the installer's preview:

```sh
git clone https://github.com/mirage335-colossus/codex-delegation-kit.git
cd codex-delegation-kit
python3 --version
python3 install.py
```

Apply after reviewing the proposed changes:

```sh
python3 install.py --apply
```

To install into another Codex home, pass `--home PATH` to both commands. For
updates, fetch the intended revision, inspect it, then repeat the preview and
apply steps from that clone. The installer refuses to overwrite edits to
managed installed files; reconcile those edits before updating. Reinstallation
is idempotent. After installing or updating role instructions, start a fresh
Codex session so it loads the current roles.

The installed copy is a deployment, not the maintained source. The policy's
[source workflow](policy.md#improving-this-kit) covers source discovery and
preservation.

## Disable and stop a run

Disabling removes the kit's marked activation blocks from global `AGENTS.md`
and `config.toml`. It retains the installed runtime files and run evidence. The
installed utility previews by default; use the same Codex home that was used
for installation:

```sh
kit_home="${CODEX_HOME:-$HOME/.codex}"
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home"
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home" --apply
```

Disabling does not stop a running controller, and ending the chat is not a
controller stop signal. Use its run directory to stop or drain that run before
removing runtime files:

```sh
python3 "$kit_home/delegation-kit/controller.py" --run /path/to/run stop
# Or let active work finish before the loop exits:
python3 "$kit_home/delegation-kit/controller.py" --run /path/to/run drain
```

After disabling, start a fresh session to load the changed activation state.
For controller recovery, holds, and continuation behavior, use the
[operator surface](ORCHESTRATION.md#small-operator-surface) and the policy's
[interruption procedure](policy.md#classify-interruptions-before-implementation-escalation).

## Installed files and license

The runtime bundle has 23 files: this README, `policy.md`, `CLOUD.md`,
`ORCHESTRATION.md`, `supervisor.py`, `install.py`, `uninstall.py`,
`controller.py`, `controller_store.py`, `execution.py`, `agent_backend.py`,
`scheduling.py`, `engineering.py`, and ten role TOML files in `agents/`.
`CONTRIBUTING.md`, tests, examples, and verification materials are source-only
and are not installed. The policy describes expected behavior; each program
enforces only its documented checks.

Author and CC0 affirmer: **mirage335**. This repository is dedicated to the
public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
