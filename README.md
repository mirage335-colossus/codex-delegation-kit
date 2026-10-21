# Codex delegation kit

This user-level Codex kit provides a focused read-only scout role, a bounded
implementation role, and a strong review/takeover role. Its optional Python
controller executes a structured work inventory and keeps routine scheduling
out of the model's conversation. It preserves the primary model and effort
selected for the user's chat. Read [`policy.md`](policy.md)
for the full operating guidance, including delegation boundaries, evidence,
review, escalation, and validation.

## Choose the coordination mode

| Mode | What keeps work moving | State and limits |
| --- | --- | --- |
| Controller, explicitly selected | `controller.py` admits, dispatches, observes and replenishes work in a loop | One SQLite authority per run; owned subprocesses and independent Codex app-server sessions |
| Advisory helper | The coordinator follows `supervisor.py` actions using available native tools | Existing evidence files; the helper does not dispatch work |
| Native-only, explicitly selected | Native agent tools and the coordinator | Native history; no controller or helper ledger |

Installation enables role guidance only. It starts no controller, changes no
existing run, and changes no global model, effort, tier or concurrency setting.
Coordinator-only engineering allocation is a separate choice from these modes.

## Controller quick start

From the source checkout, run the self-contained process example:

```sh
python3 -B examples/controller_demo.py
# To retain its inventory, workspace and run state for inspection:
python3 -B examples/controller_demo.py --directory /tmp/new-controller-demo
```

The example uses a disposable workspace and real local subprocesses. It makes
no model calls. The older `examples/demo.py` simulates advisory evidence, while
`examples/benchmark.py` simulates scheduling with matched resources. Neither a
simulation nor a process test establishes live model integration.

For actual work, prepare a version-1 JSON inventory using the format in
[`ORCHESTRATION.md`](ORCHESTRATION.md). Give the run an explicit allocated share
of resources, narrow dependencies, structured command arguments, and concrete
acceptance contracts. Then use one run directory for its lifetime:

```sh
python3 -B controller.py --run /authorized/path/run start inventory.json
# In another terminal while that loop is running:
python3 -B controller.py --run /authorized/path/run status
python3 -B controller.py --run /authorized/path/run explain
python3 -B controller.py --run /authorized/path/run events --after 0
python3 -B controller.py --run /authorized/path/run report
python3 -B controller.py --run /authorized/path/run result --task TASK_ID
```

`start` ingests once and runs the foreground event loop. `start --prepare-only`
only validates and creates the run; `run` starts its loop later. The controller
owns claims, resource reservations, timers, result ingestion and replenishment.
Workers handle their bounded engineering questions and return the requested
result; they do not maintain a parallel ledger or reconstruct the queue after
compaction. Use `submit tasks.json` for one task or a JSON list of newly discovered
tasks. It returns task IDs; omitted IDs are generated from the submitted packet
so an identical resubmission is deduplicated. Managed subprocess workers identify
their active assignment with `--parent-attempt`.
Do not execute inventory prose as shell code.

The control commands persist the decision before acknowledging it:

```sh
python3 -B controller.py --run /authorized/path/run pause
python3 -B controller.py --run /authorized/path/run drain
python3 -B controller.py --run /authorized/path/run stop
# Explicitly resume, then ensure the event loop is running:
python3 -B controller.py --run /authorized/path/run resume
python3 -B controller.py --run /authorized/path/run recover
```

`pause` prevents new dispatch and lets active work finish. `drain` also lets
owned work finish before the loop exits. `stop` persists a stop and requests
cancellation of owned execution, including when the controller loop is absent;
resources remain reserved until release is observed. `recover` reconciles
receipts and retained results without clearing a user pause, stop, hold or hard
budget. Only explicit `resume` clears a user pause or stop. Stopping the chat is
not a supported stop signal to detached execution: use the `stop` command.

Inspect each task's scheduling status, execution outcome and acceptance status.
A valid failing test can complete a check inventory entry; a cancelled attempt,
setup failure, deferred check or unaccepted patch cannot. `all_original_complete`
refers to the original inventory, so an empty fast queue is not completion.
Helper acceptance retains the existing checks, independent review, original
failures and repair allowance. Engineering tasks receive a separate observed
reviewer turn, including after takeover edits. For legacy helper work, record
authorized review or interruption evidence with
`record --task ID --kind KIND --actor ACTOR result.json`. A completed model turn
is never automatic patch acceptance; actor names and submitted claims alone
are not proof that a command ran.

The automatic agent backend has two explicit profiles. `read-only-no-exec`
keeps the supplied-context reasoning path. `engineering` lets a scout inspect
actual source and run bounded diagnostics, a worker edit owned paths and check
its patch, a separate reviewer inspect that patch and evidence, and an owner
continue consequential repair. These are independently controlled app-server
sessions, **not native subagents of the controlling chat**. Every stage uses the
same explicit per-run model, effort and service tier; role labels never select
a model. A Luna-medium run therefore keeps review and takeover at Luna medium.
The backend verifies available resolved settings before inference. A denied or
unavailable capability becomes a hold, never a model/account/backend fallback.

Engineering commands use the runtime's sandboxed shell. Each original task
receives a private repository copy; the original repository stays outside the
writable roots. Code provides private scratch space for wrappers, compilation
and checks, sets `TMPDIR` there, and sets `PYTHONDONTWRITEBYTECODE=1`. A reviewer
may write only its scratch directory and must leave the private patch unchanged.
Scouts can also use an explicitly owned experimental scope. The runtime
sandbox covers the entire private repository; role instructions and a post-run
audit enforce the narrower patch-ownership contract. The controller retains
before/after snapshots, a patch and ownership through review and repair. The OS boundary is the whole workspace:
file ownership and `allowed_commands` are narrower instructions and audited
contracts, **not an executable allowlist or a file-level OS sandbox**. Reads are
not confined to the repository by this runtime's read-only profile. Known
connector, network and nested-delegation paths remain disabled; no exhaustive
builtin-tool allowlist is claimed.

Process execution inherits the controller's existing OS sandbox. The run's
allowed executable/cwd checks apply to submitted process tasks; a model's shell
subcommands do not pass through that executable check. Native commands and
descendants share the worker's admitted allocation and owned runner. A finished
turn cannot release resources while descendants survive. Declared CPU, memory,
process and reasoning reservations do not enforce global host limits or
per-command CPU/memory quotas. Allocate capacity after accounting for the main
chat and other work; unobservable outside work is not accounted automatically.

## Submit engineering work

Create a run with `agent_profile: "engineering"`, explicit model/effort/tier and
resource allocation, and an authorized sandbox boundary as shown in
[`ORCHESTRATION.md`](ORCHESTRATION.md#engineering-run-and-task-format).
The task's `cwd` identifies its source repository; code creates and records the
private workspace. Keep run records outside the writable copy. The small packet
below is enough for an already clear implementation; no scout stage is required:

```json
{
  "role": "worker",
  "cwd": "repo",
  "prompt": "Fix total() so it includes every input; preserve empty-input behavior.",
  "write_scope": ["totals.py", "test_totals.py"],
  "allowed_commands": ["Read and search this repository", "python3 -B -m unittest -v"],
  "acceptance_checks": ["all inputs are included", "empty input returns zero", "unit tests pass"]
}
```

Submit it with `controller.py --run /authorized/path/run submit task.json`.
Code supplies IDs, attempts, private workspaces, evidence locations, a bounded
result schema, and review/repair/takeover continuations. The loop dispatches and
ingests them without another coordinator turn. Read `status` for progress and
`result --task ID` for the producing attempt's actual commands, proposed result,
effective settings and acceptance history. Its `result_location` points to full
command events, before/after snapshots and `patch.diff`. A reviewer must judge
whether the actual commands and patch establish the original criteria.

For parallel differential diagnosis, submit distinct scout tasks with
`hypothesis`, `experiment`, and `comparison` metadata. Name tasks only when a
dependency needs a stable reference. Depend on the useful result's evidence label,
such as `{ "task": "reproduce", "evidence": "failure_reproduced" }`, so a slow
independent branch does not delay a ready correction. Preserve the original
failing comparison; several agents agreeing is not causal evidence. The full
example is in [the controller contract](ORCHESTRATION.md#parallel-differential-diagnosis).
`examples/engineering_tasks.py --help` describes the checkout's disposable
fixture/example generator; preparation itself makes no model calls.

If a completed diagnostic reports `observed` but its actual command evidence
supports a narrower conclusion, inspect `result --task ID`, make that engineering
judgment, then record it with `assess --task ID --outcome failure_reproduced
--reason "the cited command returned 3 for [2,3], whose expected sum is 5"`
(or `hypothesis_rejected`). Code adds a separate assessment gate while retaining
the raw result and outcome. It does not rerun work, infer a cause, accept a patch
or count another completed result. The interpretation is an operator assertion,
not authenticated or automatically proven reasoning.

Original assignments receive separate private copies, so concurrent experiments
can modify overlapping file names without sharing those bytes. Repair, review
and takeover retain the same assignment's copy and patch ownership. The
controller returns reviewable patches and never merges them into the source
repository. Integrate only after reviewing the diagnostic evidence and when the
task authorizes integration. Engineering snapshots require standalone Git source
roots and reject unsupported linked worktrees, symlink files and submodules;
ignored descendants inside declared audit directories are captured, including
prior scratch outputs across stages. Other ignored caches are not copied or
audited. See the contract for bounded snapshot limits.

If the controller is interrupted, recover the **same run**. A cancelled writing
attempt retains its patch and becomes a hold. After verified process release,
inspect the current workspace and use the documented `resolve` continuation
with its reviewed digest; neither recovery nor explicit resume blindly replays
coding against possibly modified files. Permission holds require resolution of
the same operation and cannot be bypassed through another profile. If automatic
owner/review stages are exhausted, `continue --task ID --reason "engineering
decision"` authorizes one further owner or review stage within the same history
and budgets. It never clears a user pause or stop.

For an invalid original worker report caused by a reviewed format issue,
`continue` can revalidate the retained report after the normal runtime migration,
without rerunning the worker. This requires completed released execution, an
unchanged audited patch, no hold, no consumed worker result, and remaining
original deadlines. The raw report and original validation error remain visible
in `result`; independent review is still required. Command summaries come from
actual runtime receipts, so a model need not reproduce that bookkeeping format.

The run pins its runtime file identities. An upgrade cannot silently authorize
new runtime code for existing work: changed runtime files hold new dispatch for
review. Preserve the whole run directory, including SQLite state and operation
receipts. Unknown launches or lost ownership remain held for reconciliation;
the controller does not claim universally exactly-once external side effects.

## Routing and engineering responsibilities

Establish the applicable routing boundary from the user's instructions and
reliable current-session evidence of the selected main model and reasoning
effort. A global default is not evidence of the active chat's settings. Unknown
model context or uncertain eligibility defaults to native inheritance; do not
guess a tier from model version names, availability, price, or historical work.

| Current routing boundary | Scout and bounded worker | Independent review, consequential design, integration, and takeover |
| --- | --- | --- |
| Known high-end selection, with the user's standing mixed-quality preference | Pinned `luna_scout` and `luna_worker` | Pinned `sol_expert`, or the permitted primary in default engineering mode |
| Known low-cost selection, including Luna medium | `inherited_scout` and `inherited_worker` | `inherited_reviewer` |
| Unknown active settings or eligibility | Native inherited roles | Native inherited reviewer |

The three existing pins remain intentional: the Luna roles request
`gpt-6-luna` with `high`; `sol_expert` requests `gpt-6.1-sol` with `ultra`.
For short independent diagnostic experiments, the additional `inherited_swarm`
role inherits the permitted parent settings; optional `luna_swarm` pins that
responsibility to Luna medium within an authorized mixed-model strategy. Neither
changes the existing roles. A Luna-medium ceiling applies to review and takeover
as well as probes. See [bounded swarm probes](ORCHESTRATION.md#bounded-swarm-probes).
High-end routing keeps the quality-oriented strategy: delegate suitable bounded
work and retain consequential ownership and independent review. It does not
automatically maximize agent occupancy. Known low-cost and unknown operation
must use inheritance unless the user explicitly authorizes a scoped exception.
For example, authorizing the pinned expert for one final review does not
authorize pinned workers or later expert execution outside that review.

The inherited role TOMLs omit both `model` and `model_reasoning_effort`. In
inherited operation also omit spawn-time model and effort overrides, and never
select a pinned custom role to obtain inheritance. The documented resolution
uses explicit spawn settings, then agent defaults, then the parent; a custom
role file's explicit selectors take precedence afterward. Weaker spawn values
therefore cannot override a stronger pin. See the official [subagent
configuration guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Omission inherits the parent only when effective agent/profile defaults do not
override it. Keep existing unset global subagent model and effort defaults
unset. If a conflicting effective default is known, preserve unrelated
configuration and report the precise limitation rather than silently edit it
or claim inheritance. With no overriding defaults, a Luna-medium parent is
intended to supply Luna medium to both inherited workers and reviewers. Prove
actual resolution from current-session runtime settings when available;
configuration checks, a role's own model claim, and this example do not prove a
fresh Luna-medium session behaved that way.

The current desktop supports the existing `[agents.<name>]` descriptions and
`config_file` registration form. A fresh session is needed to expose newly
registered inherited role names. If the current native role table does not
expose them, use a supported unpinned native default with the neutral role's
instructions and no model/effort overrides; do not claim a custom role was
loaded. Report any inability to achieve permitted settings rather than use an
excluded pin. Current capability investigation found no documented native
conditional setting that selects roles by parent model tier, or an automatic
cost hierarchy/runtime-enforced ceiling. Exact current-session settings can be
evidence when available; uncertain eligibility still requires inheritance.
No new conditional TOML keys, model ranking, or pricing mechanism is installed.

Engineering responsibilities do not grant model permission. Independent
review, diagnosis, escalation, and takeover stay within the current routing
boundary through repairs, continuations, and handoffs. A historical Sol owner
must not be resumed under a low-cost or unknown boundary merely to preserve
ownership. Arrange an explicit permitted-owner handoff under the same
assignment, retaining evidence, acceptance criteria, original failures,
repair use, budget, deadline, and ownership history. Use independent permitted
reasoning, narrower experiments, or a precise unresolved issue when necessary;
do not weaken acceptance or automatically upgrade models. A reviewer cannot
approve a patch it produced or substantively repaired.

## Coordination and useful parallelism

Model routing, engineering allocation, coordination mechanism, and concurrency
are independent choices. The latest applicable user delegation instruction can
select coordinator-only or native-only coordination and supersede conflicting
kit or user-level delegation preferences. System, developer, tool, substantive
project, and authorization constraints still apply.

In coordinator-only mode all engineering goes to permitted subagents, including
tiny source lookups, wrappers/tests, builds, artifact analysis, existing-run
monitoring, integration, and review. The primary handles assignment, dispatch,
routing, and status/completion from delegated acceptance evidence. In native-only
mode use native messages/history without the controller, kit helper or new coordination
registries, ledgers, or report files. Authorized engineering artifacts, logs,
reproducers, and task-requested outputs remain allowed.

Choose concurrency for useful accepted progress and quality. When the task or
user calls for aggressive parallelism, keep current native capacity usefully
occupied by real independent assignments and replenish ready work. Do not add
filler, duplicate investigations, or a historical agent-count target. Ready
implementation and regression work must not be starved by broad scouting.
Respect read/write dependencies and machine limits: reasoning-agent capacity
is separate from compiler/test jobs and isolated timing measurements. Assign
one monitor to an existing run and preserve its identity instead of restarting
or duplicating it. No concurrency strategy authorizes different model settings,
changes to the selected primary, higher service tiers, or altered limits.

The policy's [five scheduling rules](policy.md#keep-useful-work-moving-after-scouting)
prioritize quick useful outcomes, dispatch before waiting, reassess slow work,
keep resource restrictions temporary, and use lightweight progress feedback.
Publish stable partial results and split unstarted backlogs when useful.
Required expensive work, validation, and escalation remain necessary; deferral
is not completion. These instruction rules add no fixed time caps or runtime
scheduler to advisory or native-only operation. The explicitly selected
controller implements its documented scheduling policy in code.

## Application maintenance and interruptions

For a task that actually authorizes application maintenance, use bounded
reproductions and causal narrowing to identify and correct ordinary defects.
Reduce inputs and execution paths, prefer tiny wrappers around the real helper
or API where useful, compare unchanged and corrected behavior, and check relevant
boundaries and regressions. Keep work within authorized repositories, execution
environments, and services, preserving task-specific access and write limits.
This scope excludes fuzzing campaigns, exploit development, security scanning,
tests targeting external systems, unauthorized access, credential handling,
and security-control changes; it is not blanket authorization for another task.
Authorized cloud runners and CI services, including GitHub Actions, may execute
application checks; that execution is not itself testing an external system.

Use small wrappers and short targeted compiles when they can answer the question.
Do not use broad/full builds, long or expensive cloud/CI jobs, or repeated workflow
runs merely to avoid writing a feasible small reproducer or wrapper. Minimal
checks may run in authorized cloud environments. Larger integration, regression,
platform/toolchain, and performance checks remain appropriate when their
validation or environment requirements justify them.

Cybersecurity notices may have limited logged detail, may never have been shown
to the user, or may be unavailable. Preserve the exact available notice and
attempted operation with the same assignment, partial work, and failure history.
Report absent details honestly; do not guess a reason, assume a mistake, or ask
the user for hidden details they cannot supply. Relevant visible command/run
context may still be requested when genuinely needed.

If the optional helper is selected, its nonempty `notice` field retains exact
accessible text. Label partial text `PARTIAL` and include the verbatim accessible
portion; if no text is accessible, label the evidence limitation `UNAVAILABLE`.
These labels are not fabricated service notices, and legacy exact-text records
remain valid. State unknown required-field details with the existing assignment
or invocation reference; omit unknown optional model/effort values. Preserve the
same hold's operation/scope identity and append new evidence/decisions without
rewriting original events or renaming the blocked operation. An availability
label alone does not establish a wider restriction.
Native-only coordination needs no helper schema or new records.

Determine the affected scope only from actual available evidence. Keep the known
restricted operation blocked, pause dependent work with unclear permission, and
continue demonstrably independent permitted work. Do not retry the operation
through another agent, model, account, renamed assignment, or disguised wording.
Useful aggressive maintenance remains possible within the selected routing and
resource limits: each independent question needs a concrete hypothesis, disjoint
writes and private technical output paths where applicable, and a small
discriminating test. Confirmed fixes can proceed alongside independent inquiries.
Separate paths do not create OS isolation; no new coordination registry is added.

At the next substantive interruption update, state the known blocked operation,
available notice or missing-detail limitation, supported scope and uncertainty,
permitted assignments progressing, concrete results, and any genuinely needed
user-suppliable clarification. A broad audit or full build does not replace
focused diagnosis, and parallel assignments cannot bypass a restriction.
See the policy's [maintenance scope](policy.md#application-maintenance) and
[interruption procedure](policy.md#classify-interruptions-before-implementation-escalation).

## Requirements and model support

Cloning requires Git. The installer, evidence helper and controller require
Linux and Python 3.11 or newer. They use the Python standard library and install
no packages or services. Owned cancellation also requires Linux `pidfd` support
and child-subreaper support; the adapter refuses unavailable ownership support.
The agent backend additionally requires a compatible Codex app-server executable
and authorized account/model access. A model catalog entry is not proof of access.
Windows support is not claimed. Use the evidence helper only when its workflow
is selected; it is skipped in native-only operation. Its action names describe
responsibilities, not models, and its legacy `strong` result kind remains a
compatibility label.

Check that a selected pinned model/effort is both supported and authorized;
report an unavailable setting instead of silently substituting. The role
instructions govern behavior, while the installer/helper enforce only their
specific checks. The controller dispatches its supported independent backend;
it does not schedule native chat subagents, automatically recognize every
parent tier, or establish permissions absent from its actual runtime.

## Clone, install, update, and disable

Clone the public repository:

```sh
git clone https://github.com/mirage335-colossus/codex-delegation-kit.git
cd codex-delegation-kit
python3 --version
```

The installer previews changes by default. Review the diff before applying it:

```sh
python3 install.py
python3 install.py --apply
```

To target a separate Codex home, pass `--home` or set `CODEX_HOME` for a
single command. These examples quote paths so spaces are handled as one
argument and do not persist an environment change:

```sh
python3 install.py --home "$HOME/Codex Home"
CODEX_HOME="$HOME/Codex Home" python3 install.py --apply
```

To update, fetch the desired repository revision, inspect the changes, then
run the same dry-run and apply sequence from the updated clone. The installer
refuses to overwrite local edits to managed installed files. Back up or
reconcile those edits before updating. Reinstallation is idempotent.

For requests to improve the delegation kit itself, edit the verified Git clone
first, validate and review the changes, then install from that clone when the
task authorizes updating the active global kit. Follow `policy.md` under
"Improving this kit"; preserve any source-only or no-global-write instruction.
Editing only the installed copy leaves the repository unchanged. Git updates
and global installation are separate steps, and neither automatically commits
or pushes changes. Report source revision/dirty state, validation, installation,
and commit/push status separately; preserve remote-write restrictions.

The installed `.installation/manifest.json` optionally records `source_directory`,
the absolute external bundle source last used by the installer. Verify that
candidate is still the intended Git checkout with its development files before
using it. It may be missing in an older installation, moved, or an unpacked
bundle; it is not proof of Git identity, authorization, or remote state. Use an
explicit current user source when supplied, and resolve a missing or ambiguous
source rather than falling back to installed-only edits. Installing from a new
source path refreshes this hint even when bundle bytes are unchanged. Running
the installed utility or disabling preserves the existing hint, including an
unknown source. This metadata does not make Git-to-global synchronization
automatic.

Updates from the original eight-file bundle migrate its three managed role
registrations to the current eight. Updates from that bundle or the eleven-file
bundle add the controller modules. The seventeen-file controller bundle adds
`engineering.py`; the eighteen-file engineering bundle adds the two swarm role
files. Every upgrade retains run state and evidence. Active and disabled
installations are supported.
The installer preserves unrelated configuration and retained evidence, and
refuses conflicting registrations or unowned files at newly introduced paths.

Preview disabling, then apply it:

```sh
kit_home="${CODEX_HOME:-$HOME/.codex}"
# If installation used --home, set kit_home to that same path first.
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home"
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home" --apply
```

The default destination is `$CODEX_HOME/delegation-kit`, where `CODEX_HOME`
defaults to `~/.codex`. Disable removes only the kit's marked activation blocks
from global `AGENTS.md` and `config.toml`. It retains the installed bundle,
backups, and task evidence; it does not remove or restore unrelated settings,
project configuration, or local edits. Disabling the kit does not stop an active
controller; explicitly stop or drain each owned run before removing its runtime.
Review the preview and preserve any needed files before separate cleanup decisions.
Start a fresh Codex
session after installing, updating role instructions, or disabling: existing
sessions may retain instructions already loaded.

The runtime install contains twenty files: this README, `policy.md`,
`supervisor.py`, `install.py`, `uninstall.py`, `controller.py`,
`controller_store.py`, `execution.py`, `agent_backend.py`, `scheduling.py`,
`engineering.py`, `ORCHESTRATION.md`, and eight role TOML files in
`agents/`: four pinned roles and four selector-free inherited roles.
`CONTRIBUTING.md`, `tests/`, and `examples/` are clone-only development
resources and are not copied into the installed bundle. The policy governs
agent behavior; each program enforces only its documented checks. Markdown
instructions are not a permission boundary, and the controller does not enforce
every engineering or authorization requirement in the policy.

## Development (source checkout)

Read `CONTRIBUTING.md` in the clone for development and compatibility guidance.
From the repository root, run the isolated standard-library checks and optional
examples:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B examples/demo.py
python3 -B examples/controller_demo.py
python3 -B examples/benchmark.py
```

These examples make no model calls and do not prove live routing or model
quality. Keep deterministic scheduling simulation, real subprocess execution
and real model integration evidence separate. These development resources are
available in the source checkout only.

## License

Author and CC0 affirmer: **mirage335**.

This repository is dedicated to the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
The full `LICENSE` text is included in the source checkout; it is clone-only
and is not copied into the installed runtime bundle.
