# Controller implementation contract

This opt-in controller moves scheduling bookkeeping into Python 3.11 standard
library code. Native-only and the existing advisory supervisor remain available.
No controller starts on installation. External Codex executions are independent
sessions, not children in this chat's native subagent tree.

For included Desktop Codex allowance, the [weekly usage cost index](policy.md#weekly-usage-cost)
uses the user's rough relative estimates: Luna = 0.1, Terra = 1, Sol
approximately 10 and Astra approximately 20. This is separate from API USD, purchased
credits and the scheduler's time/resource costs. It neither adds a run-format
field nor changes ranking, role selection, uniform run settings or budget
enforcement. Observed tokens do not by themselves calibrate weekly allowance use.

The durable authority is `run/state.sqlite3`. Execution receipts and logs in
`run/operations/<operation-id>/` are observations reconciled into that authority.
Only one controller holds `run/controller.lock`. Short SQLite transactions allow
status, stop, submission and result reporting while execution is active.

## Internal interfaces (version 1)

`execution.py` exports `launch(directory: Path, spec: dict) -> dict`,
`observe(directory: Path) -> dict`, and `cancel(directory: Path, reason: str) -> dict`.
An operation directory is unique and never reused for another attempt. Launch is
idempotent for identical specs and rejects changed specs. Spec contains `argv`
(list), `cwd` (absolute), `env` (explicit overrides), `timeout_seconds`, and
`operation_id`. No shell evaluation. The adapter must durably fence execution
before launch, own a process group, keep output in `stdout`/`stderr` files, retain
process start/boot identity, and never release a reservation merely from a missing
heartbeat. It can return `prepared`, `running`, `completed`, `cancelled`,
`setup_error`, or `uncertain` in the `state` field. Observations include `released` (true only with
verified absence), `returncode`, `started_at`, `finished_at`, and `detail` when
known. Unknown launch outcomes become `uncertain`, never automatic relaunch.
Cancellation is cooperative with a bounded kill escalation; descendants must be
gone before `released=true`. Surviving unidentifiable execution retains a hold.
Adapter receipts may survive controller crashes; identical re-observation is safe.

`agent_backend.py` exports `prepare(task, policy, directory) -> execution spec`
and `collect(directory, observation) -> dict`. Uses one supported Codex backend,
explicit per-run model/effort/sandbox/approval/network/tool constraints, and no
fallback on denial. Exposes configured vs observed model/effort separately.
Collect returns `status` (`completed`, `failed`, `hold`, `invalid`, or verified
swarm `cutoff`), `result`
(parsed final JSON if present), `effective` settings and telemetry if available,
and `detail`. Engineering results also retain runtime-observed `commands` and
`file_changes`; full events remain in `backend-events.jsonl`. A completed turn
is not engineering acceptance. No nested agent
creation: managed work is submitted through the controller CLI. A runtime that
cannot enforce a requested boundary must refuse it. Native tree integration is
not claimed.

`scheduling.py` exports `rank(tasks, now, policy) -> list[dict]`, returning copies
of eligible tasks in selection order with `selection_reason` and `score`, and
`should_preempt(active, candidate, now, policy) -> bool`.
Task dictionaries contain id, priority (larger first), origin (`original` or
`followup`), created_at, ready_at, estimate_seconds (null unknown), setup_seconds,
restart_seconds, uncertainty (0..1), unlock_value, service_seconds, quantum_seconds,
preemptions, preemption (`never` or `restart`), started_at, and resources.
Only controller passes eligible tasks and accounts for capacity. Ranking respects
priority, favors cost to next usable result with uncertainty/unlock value, ages
finite original work, and gives unknown work a discovery opportunity. Quanta are
progressive after deferral; elapsed service is a lower bound, not a completed
duration. Preemption requires a safe restart declaration, minimum service,
hysteresis, interruption cap, and demonstrable expected benefit including lost
work. No blanket preemption of slow work.

## Public run format

JSON `version: 1`, optional `id`, `workspace`, `policy`, `tasks`. An omitted run
ID is generated once during creation. Policy specifies
`capacity` (reasoning, processes, cpu, memory_mb), `allowed_cwds`,
`allowed_executables`, `model`, `effort`, `service_tier` when agent work is used,
`sandbox`, `approval`, `network`, `max_active_seconds`, `deadline_seconds`, and
optional scheduling controls. Task includes optional stable `id`, `kind` (`process` or
`agent`), `argv` or `prompt`, `cwd`, narrow `inputs`, `outputs`, `resources`,
`depends_on` (task IDs or {task, evidence}), `acceptance`, estimates and preemption.
Process commands are structured arguments, never inventory prose executed by a
shell. Agent command guidance is an instruction to the worker, not direct shell
evaluation or a command allowlist.
Acceptance is an explicit command exit/result contract or a legacy helper packet
requiring independent review. Task completion, execution outcome, evidence
validity and engineering acceptance remain separate. Hold and review commands
are assertions by the authorized operator, not authentication mechanisms.

## Engineering run and task format

Select the existing automatic backend with `agent_profile: "engineering"`.
Use explicit settings authorized for this run. The following is a minimal run
wrapper; replace the paths and settings with the allocated environment:

```json
{
  "version": 1,
  "id": "bounded-fix",
  "workspace": "/authorized/project-area",
  "policy": {
    "capacity": {"reasoning": 3, "processes": 3, "cpu": 3, "memory_mb": 1536},
    "allowed_cwds": ["/authorized/project-area"],
    "allowed_executables": [],
    "process_boundary": "inherited",
    "boundary_description": "Authorized local launcher; each worker uses a private repository copy with network disabled.",
    "codex_binary": "/absolute/path/to/codex",
    "agent_profile": "engineering",
    "model": "gpt-6-luna",
    "effort": "medium",
    "service_tier": "default",
    "sandbox": "workspace-write",
    "approval": "never",
    "network": false,
    "max_active_seconds": 900,
    "deadline_seconds": 1200
  },
  "tasks": [{
    "role": "worker",
    "cwd": "repo",
    "prompt": "Fix total() to include every item, preserving empty-input behavior. Inspect the actual implementation and run its tests.",
    "write_scope": ["totals.py", "test_totals.py"],
    "allowed_commands": ["Read and search source", "python3 -B -m unittest -v"],
    "acceptance_checks": ["all items included", "empty input returns zero", "tests pass"],
    "timeout_seconds": 120
  }]
}
```

The number of slots is an explicit allocation, not a default target. The run
model, effort and tier apply to every worker, reviewer and takeover turn. The
controller does not use native role pins or `review/start` to select another
model. Requested settings and the app-server's resolved settings are retained
separately; they are not provider-side per-token identity telemetry.

The initial native `astra_initial` consultation uses `gpt-6-astra` at `ultra`;
later reviews use the optional native `astra_expert` adviser pinned to
`gpt-6-astra` at `ultra`. Neither role adds a task-level model override to this
format. The native [strategic brainstorming and human
input](policy.md#strategic-brainstorming-and-human-input) and [Astra review
gates](policy.md#astra-strategic-review) preserve hard model ceilings and do
not authorize changing a restricted run, resuming a stop or bypassing a hold.
They also do not change the controller's uniform single-model policy. Any
separately authorized advice stays within the shared resource allocation; the
existing run, patch ownership and independent acceptance remain unchanged.
The native Luna evidence-discovery strategy is summarized in
[policy.md](policy.md#evidence-discovery-and-terra-screening); controller runs
retain their uniform explicit model/effort/tier boundary.

The input `cwd` names the source repository. Code prepares one independent
private copy per original task under the run's workspaces and records
`source_repository`; workers never receive write access to the original root.
The copy includes current Git-visible dirty files and uses independent bytes,
not shared hardlinks. Repair, review and takeover use the same retained private
copy. No automatic merge or original-repository edit follows acceptance.

A task needs `role`, a bounded `prompt`, `cwd`, `allowed_commands`, and its scope
and acceptance. `worker` and `owner` need nonempty `write_scope` and original
`acceptance_checks`; `reviewer` stages cannot change the patch. A scout may leave
`write_scope` empty or explicitly own private experimental files/directories,
for example `["experiments/"]`. A nonempty scope requires workspace-write
permission in the run. A trailing slash can name a not-yet-created directory.
Use a worker responsibility for the correction itself. Known implementation
work can be submitted directly without a preceding scout.

With a workspace-write run, code generates a private scratch directory for each
stage and includes it in that stage's ownership. `TMPDIR` points there and
`PYTHONDONTWRITEBYTECODE=1` avoids incidental Python caches. A reviewer may create
wrappers, compiled outputs and test artifacts only in its scratch directory;
its source and patch are immutable by the role contract and post-run audit.
The OS sandbox is still workspace-write for the entire private repository, not
file-level separation within it. The original source root is outside writable
roots. `audit_scope` retains prior experimental/scratch directories across stages
so ignored files there remain part of the reviewed evidence.

Code generates omitted task IDs, attempts, timestamps, result directories,
repository snapshots, and helper acceptance packets. `submit task.json` accepts
one task or a list and returns IDs. Identical packets deduplicate; use an
explicit `id` when other tasks must refer to it. `depends_on` retains its
existing `{ "task": "id", "evidence": "label" }` form. Optional `inputs` are
source-relative and rebased to the private copy; omission uses the copied
Git-visible inventory. Worker output is proposed evidence, not acceptance.
Default continuations arrange independent review, the existing single
new-evidence repair, and takeover without changing the assignment's budget,
criteria or history. Takeover authors also require independent review.

## Parallel differential diagnosis

A diagnostic task adds a hypothesis, an experiment that distinguishes it from
alternatives, and matched input/environment metadata. Put expected observations
and their meaning in the prompt. For a fixture with a parser and total reducer,
two bounded assignments might be:

```json
[
  {
    "id": "parse-case",
    "role": "scout",
    "cwd": "repo",
    "prompt": "Report the actual parser output, searched paths and uncertainty. Do not infer that the reducer is correct from this experiment.",
    "hypothesis": "Parsing drops the first number before total() runs.",
    "experiment": "Call the actual parser on '2,3' and compare its output with [2,3].",
    "comparison": {"case": "two-positive-values", "input": "2,3", "environment": "same local Python interpreter"},
    "allowed_commands": ["Read and search source", "Run the bounded parser comparison with python3 -B"],
    "write_scope": []
  },
  {
    "id": "reduce-case",
    "role": "scout",
    "cwd": "repo",
    "prompt": "Report actual direct-call results for [2,3], a singleton and an empty list, preserving the failing output.",
    "hypothesis": "The reducer skips the first item independently of parsing.",
    "experiment": "Bypass parsing and call total() directly on the matched values; compare with Python sum().",
    "comparison": {"case": "two-positive-values", "input": [2,3], "environment": "same local Python interpreter"},
    "allowed_commands": ["Read and search source", "Run the bounded direct reducer comparison with python3 -B"],
    "write_scope": []
  }
]
```

Each task gets its own copy, including when experimental edits overlap. Record
shared preparation as an explicit stable input; private copies do not include
ignored build caches. The scheduler ingests each result as it arrives. A
correction can depend specifically on
`{ "task": "reduce-case", "evidence": "failure_reproduced" }` while an unrelated
slower branch continues. Do not make every task depend on the entire diagnostic
batch. Review the observations before selecting a correction or integrating
competing patches; agent agreement is not confirmation of a cause.

The diagnostic JSON result contains `outcome`, `findings` and `evidence`.
`hypothesis_rejected` and `failure_reproduced` require observed completed command
activity; otherwise the controller labels the result `not_tested`. `observed`
can carry a source finding and is distinguished from a runtime experiment.
`setup_failed` and `not_tested` do not release a successful diagnostic gate.
Completed useful observations expose their outcome label and `result` as
narrow evidence. Original snapshots, failing outputs and matched comparison
metadata remain historical observations when a later patch passes; they are
not rewritten as current-source passes.

An `observed` result can contain a successful discriminating experiment without
using the narrow label needed by a dependent task. Read `result --task ID` and
its actual command evidence first. An authorized coordinator can then record a
concrete interpretation without rerunning the experiment:

```sh
python3 -B controller.py --run /authorized/path/run assess --task reduce-case \
  --outcome failure_reproduced \
  --reason "The recorded direct-call command returned 3 for [2,3]; the matched expected sum is 5."
```

`assess` accepts `failure_reproduced` or `hypothesis_rejected` only for a completed
`observed` diagnostic with released, ingested command execution, unchanged
audited bytes, and no hold. It adds separate `diagnostic_assessment` evidence
under the selected label; the raw model result, original outcome and execution
history remain unchanged. An identical assessment is idempotent. It cannot
replace an existing assessment, accept a patch, manufacture a new completion,
clear user controls or establish causality by agreement. The supplied reason is
engineering judgment by an authorized operator; the interface does not
authenticate that operator or prove the interpretation.

## Bounded swarm probes

`role: "swarm"` is a small preset on the existing scout path. It uses the same
run, scheduler, private copies, execution ownership and diagnostic evidence.
It does not select a model or create native subagents. Use Luna/medium at run
level when the whole run must remain Luna medium. The optional native roles
`inherited_swarm` and `luna_swarm` are separate entrypoints for native delegation;
only the latter pins Luna medium, and neither provides controller bookkeeping.

For example, submit this packet to an engineering run with workspace-write
permission and an available allocation:

```json
{
  "role": "swarm",
  "cwd": "repo",
  "prompt": "Inspect and call the actual reducer. Return the observed values and uncertainty; do not correct source.",
  "hypothesis": "The reducer omits the first value independently of parsing.",
  "experiment": "Compare aggregate([]), aggregate([7]) and aggregate([2,3]) with sum() on the same lists.",
  "comparison": {"inputs": [[], [7], [2,3]], "expected": [0, 7, 5], "environment": "local Python 3, same source snapshot"},
  "allowed_commands": ["Read and search source", "Run a bounded python3 -B wrapper calling the actual aggregate helper"],
  "timeout_seconds": 60
}
```

No caller-owned source edits are accepted. Code generates the scratch scope and
`TMPDIR`; keep wrappers, modified copies and compiled artifacts there. The
private baseline and original repository remain read-only by assignment. The
runtime sandbox protects the original repository, while file-level scope inside
the private workspace is enforced by instructions and post-run audit, not an OS
read-only mount. Source mutations become holds. A wrapper must call actual code
or clearly identify its copied modifications and matched comparison; a faithful
reduced diagnostic still does not replace full acceptance checks.

The default probe limit is 60 seconds; explicit limits remain bounded by the
run's budgets. Allow for model startup and useful execution when selecting a
limit. When a cheap discriminator is unavailable, return `inconclusive` with
observations, uncertainty and the next useful experiment. A verified budget
cutoff also becomes inconclusive. Neither outcome supplies a `result` dependency
label, counts as useful completed coverage, retries the task, nor escalates to a
different model. Setup failures, permission/service holds and user stops keep
their distinct meanings. The coordinator decides what to try next within the
same authorization boundary. An expanding supply of cheap probes must not
replace the original engineering objective.

Leave useful wrapper source for the controller to capture. It retains compact
observations, command logs, snapshots and reproducer material outside the private
workspace, then removes eligible temporary work only after verified execution
release. Cleanup has durable intent and completion records, so recovery finishes
interrupted cleanup without relaunching a probe. Held or uncertain work remains
available for reconciliation. Inspect retained evidence and any omission or
cleanup notice before relying on replayability. Durable reports are intentionally
kept; they are not expendable temporary files.

`result` exposes `cleanup` with its state and capsule location. Capture is bounded
to 128 KiB per text file and 2 MiB total; binaries, toolchains and other omissions
are listed, so a complete replay environment is not promised. Oversized scratch
source keeps the workspace instead of deleting its only copy. A cleanup marked
`failed` remains visible for inspection and does not retry automatically;
`recover` resumes committed `intent` states. `assess` can interpret a completed
observation after intentional cleanup only after verifying the retained capsule
and receipt hashes. It still cannot convert an inconclusive probe into coverage.

Existing `start`, `submit`, `status`, `result`, `pause`, `resume`, `stop` and
`recover` commands are unchanged. Fast results can release their own dependents
while other probes continue. Limit concurrency to allocated capacity and useful
distinct experiments. No exponential speedup or massive-scale benchmark is
claimed.

Prepare a self-contained two-hypothesis example without model calls:

```sh
python3 -B examples/engineering_tasks.py --directory /tmp/new-swarm-example \
  --kind swarm --model gpt-6-luna --effort medium --service-tier default \
  --codex-binary /absolute/path/to/codex
python3 -B controller.py --run /tmp/new-swarm-example/run start /tmp/new-swarm-example/inventory.json
python3 -B controller.py --run /tmp/new-swarm-example/run report
```

The first command prepares only; `start` makes actual model calls. Use the
normal durable control commands in another terminal while the loop runs.
An isolated X11 server is optional only when already available and authorized,
with private display/authentication state and owned descendants. No X11 runtime
is installed or integration promised by the preset; unavailable isolation is a
setup limitation. Native role instructions alone cannot guarantee cleanup or
enforce an OS sandbox.

## Design limits

Admission enforces declared reservations and exclusive outputs across this run.
It does not infer other chats' allocations or make process limits into global
host resource enforcement. Runs must receive an allocated share of the actual
ceiling. External workers do not inherit the controlling chat's sandbox merely
because they were launched here. Backend capability checks and explicit policy
are required; unsupported constraints fail closed. No detached service is
installed. Stopping the chat is not a supported stop signal to the controller;
use its persistent `stop` command. Unknown external side effects are held for
reconciliation; universally exactly-once execution is not promised.

## Small operator surface

Use `examples/controller_demo.py --directory /tmp/new-demo` to generate a complete
portable inventory with the current Python executable and a disposable workspace.
Use `examples/engineering_tasks.py --help` for disposable coding and diagnostic
fixture preparation, and `examples/live_agent.py --help` for the separate,
explicitly configured supplied-context model exercise. The latter makes actual
model calls and preserves their evidence;
`--prepare-only` does not. The examples and tests remain checkout-only resources.

`start inventory.json` creates once and runs in the foreground. `status`,
`explain`, and `report` derive from the database; `events --after N` gives
incremental decisions. `result --task ID` gives the producing attempt's actual
commands, proposed result, changed paths, resolved settings and helper history,
with the directory containing full evidence. `pause` prevents dispatch; `drain` finishes active work; `stop` persists
the decision and requests owned cancellation even when the loop has died. After
an explicit `resume`, run `recover` to restart the loop. Recovery itself never
clears user controls. `run --max-seconds N` bounds the observing loop only: owned
execution survives it, and its original deadline/timeout still applies.

The loop polls with bounded backoff (50–500 ms). A late timer, new submission or
accepted prerequisite wakes it without another model turn. It remains available
while held or review-dependent inventory exists, until its wall/service budget or
a user control ends it. It exits once the finite inventory is terminal. Adding
new work to an exited run requires `recover`.

`submit tasks.json --parent-attempt ID` admits a managed subprocess worker's list through the same
capacity and ownership checks. No worker should synchronously wait for a child
while retaining all capacity or outputs that child needs: publish a valid partial
and finish/yield the parent first. Arbitrary waits inside worker processes are not
observable dependency declarations.

## Partial evidence and engineering continuations

A task can declare `partials` such as
`{"header":{"path":"header.txt","text":"ready\n"}}`, with `header.txt` in its
`outputs`. The active worker can call `publish --task ID --attempt ATTEMPT
--evidence header`. Code verifies the declared text (or `sha256`) and input
identity. Only a dependency on `{ "task": "ID", "evidence": "header" }` releases.
Partial publication retains the producer's reservations. Later artifact changes
invalidate that evidence and its dependent evidence chain.

For `acceptance.type="helper"`, use the existing supervisor packet schema.
Optional `continuations` maps `review`, `worker` (one repair), or `strong`
(engineering takeover) to a bounded prompt. Code creates independent stage
attempts under the same run's model policy and original assignment/deadline/repair
history. Stage service is charged to the original active budget. Actual bounded
declared input/output content accompanies review; unavailable or oversized
material leaves an engineering decision pending while preserving the worker
report. Without a template, legacy supplied-context tasks can use `record` for
authorized independent acceptance. Engineering tasks require an observed
independent controller stage instead of a manual review claim. Stage completions are excluded from useful-result pass/failure metrics.

The helper reducer enforces the original checks, one evidence-based repair and
author separation. Engineering runs retain actual runtime command completions
and independent reviewer sessions, including after takeover edits. A command
completion alone does not establish that its assertions cover the criterion; the
reviewer must assess the actual patch, source and evidence. Legacy external
`record` actor names are assertions, not authenticated identities. Process tasks
with explicit result contracts remain available for separately admitted checks.
The controller derives helper `changed_paths` from the patch audit and helper
`commands` from completed runtime receipt IDs, exit codes and command-log
references. It preserves the model's raw packet separately; formatting that
bookkeeping is not a worker responsibility or proof of execution.

`resolve --task ID --operation ATTEMPT resolution.json` requires references in
`{"evidence":["supported resolution of the same operation"]}` and verified
execution release. It retains the hold in history and never changes model,
account, permissions, deadlines or consumed budgets. Helper interruptions use
their matching `record --kind interruption` schema instead. A lost runner with
unknown descendants cannot be released by an operator's bookkeeping assertion.
For interrupted engineering work, inspect the retained private patch, command
logs and current files first. Its resolution also needs
`"action": "continue"` and `"workspace_digest": "<reviewed current digest>"`.
Compute that digest with `engineering.snapshot(private_cwd, audit_scope)["digest"]`
using the installed module and the task's retained `audit_scope`, and cite the
review/resolution in `evidence`. The audit scope includes prior scratch outputs;
using only the current write scope can omit evidence.
The controller records the previous attempt and reviewed workspace for an
explicit continuation; it never blindly restarts a coding assignment. Resolving
a hold does not clear a durable user pause or stop; only `resume` does that.

When automatic owner/review stage allowances are exhausted, an operator can make
an explicit engineering decision with
`continue --task ID --reason "new experiment or review decision"`. It admits
one further owner or review stage only after prior execution has released and
within the original criteria, repair history, service budget and deadline. It
keeps the existing private patch; it does not start a fresh worker allowance,
resolve a permission hold, or clear a user pause/stop. Use `resume` separately
when the user explicitly authorizes resumption.

The same `continue` command can revalidate a retained invalid **original** helper
report after a reviewed report-format correction and the normal runtime migration.
It is eligible only before any worker result has been consumed, with released,
ingested, completed execution, no hold, an unchanged audited patch and remaining
original deadlines. Revalidation uses stored evidence and launches no replacement
coding attempt. `report_validation_history` preserves the original error and the
operator's reason, while the raw model packet remains unchanged. Successful
revalidation still routes the patch to independent review; it is not acceptance.

After a reviewed runtime upgrade, pause/drain and reconcile all owned execution,
then use `migrate --reason "review reference"`, explicit `resume`, and `recover`.
Migration records old and new runtime hashes; it preserves task and event history.

## Budgets, resources and evidence

`timeout_seconds` is an attempt correctness cutoff. `quantum_seconds` only wakes
reassessment. Optional `active_budget_seconds` is cumulative for the original
task and its helper stages; the run also has cumulative `max_active_seconds` and
an absolute deadline derived once from `deadline_seconds`. Interrupted service
is a lower bound and restart waste, not a completed duration. The controller
reserves finite service allowances for active attempts, so unused hard budget
reservations can temporarily defer other work. It never divides a task's useful
service allowance by empty worker slots.

Runners receive their allocated service/wall cutoff, even if the controller dies.
Termination has a bounded cooperative grace (up to 1.5 seconds plus polling),
which is reported as consumed service; OS scheduling and uninterruptible kernel
work prevent an instantaneous wall-clock stop guarantee. Unknown survival retains
reservations. No suspend/resume capability is claimed: process tasks may be
nonpreemptible or explicitly safe cancellation-and-restart. Engineering agent
tasks reject automatic restart preemption.

For ordinary process and supplied-context tasks, inputs are individual files.
Evidence binds their hashes, declared output hashes, dependency evidence,
task/environment configuration and runtime hashes. A bounded inode/size/mtime/ctime hash cache
avoids re-reading unchanged artifacts on every poll. Declare all correctness-
relevant files, flags, environment and toolchain context; undeclared changes
cannot be inferred. Final stdout equality and declared exit contracts are real
process evidence; JSON answers are only their explicitly checked bounded result.

Engineering tasks additionally retain `engineering-before.json`,
`engineering-after.json`, `patch.diff`, and runtime command events in their
operation directory. The baseline includes pre-existing dirty bytes. Authorized
private edits are compared against that baseline; changes outside ownership
become a hold. Patch ownership survives the gap between worker exit and review,
without reserving CPU or reasoning capacity after verified process release.
Source repository, private copy and reviewed produced bytes remain distinct.

The source and private workspaces must be standalone Git roots. Linked
worktrees, symlink entries and submodules are refused rather than treated as
verified isolation. Snapshots include Git-visible files plus ignored descendants
of explicit audit directories. They cover at most 20,000 files, 8 MiB per file
and 128 MiB total; captured owned text is separately bounded. Binary or
oversized patch text is listed as an omission, never a complete textual diff.
Ignored caches outside the audit scope and Git metadata are not a full mutation
audit; ignored caches are not copied from the original repository. The runtime's
workspace sandbox supplies the write boundary; the audit,
`write_scope`, `allowed_commands`, and declared resource allocation do not
replace it. This runtime does not provide repository-only read isolation.

The installed runtime's engineering path requires the bundled
`features.code_mode_host=true` together with shell execution; `code_mode`
remains disabled. Engineering requests one explicit **local** execution
environment with the private working directory and runtime workspace roots.
The adapter checks the returned local environment identity and roots before
inference. This does not authorize remote environments or claim per-file OS
isolation. The supplied-context profile retains `environments=[]` and its
execution host remains disabled. These are backend compatibility settings,
not global configuration changes or proof of a completed engineering exercise.

The worker's native commands run under its runtime sandbox and admitted task
allocation. Their subcommands bypass the process-task executable allowlist;
there is no OS CPU/memory quota per command. The Linux subreaper retains owned
descendants, including background commands, until actual release. Changing the
backend must not broaden the authorized boundary, and a permission failure is
not permission to select another profile.

Current limits are deliberately visible: no automatic host-wide CPU/memory
pressure controller, no nested model delegation, no native-subagent integration,
no exhaustive builtin tool allowlist, and no automatic release after an
unidentifiable runner death. Capacity is declared admission, not measured global
enforcement. The benchmark is a deterministic simulation; it includes poor-
estimate regressions and does not establish universal throughput gains.
