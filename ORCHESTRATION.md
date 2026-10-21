# Controller implementation contract

This opt-in controller moves scheduling bookkeeping into Python 3.11 standard
library code. Native-only and the existing advisory supervisor remain available.
No controller starts on installation. External Codex executions are independent
sessions, not children in this chat's native subagent tree.

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
Collect returns `status` (`completed`, `failed`, `hold`, `invalid`), `result`
(parsed final JSON if present), `effective` settings and telemetry if available,
and `detail`. A completed turn is not engineering acceptance. No nested agent
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

JSON `version: 1`, `id`, `workspace`, `policy`, `tasks`. Policy specifies
`capacity` (reasoning, processes, cpu, memory_mb), `allowed_cwds`,
`allowed_executables`, `model`, `effort`, `service_tier` when agent work is used,
`sandbox`, `approval`, `network`, `max_active_seconds`, `deadline_seconds`, and
optional scheduling controls. Task includes stable `id`, `kind` (`process` or
`agent`), `argv` or `prompt`, `cwd`, narrow `inputs`, `outputs`, `resources`,
`depends_on` (task IDs or {task, evidence}), `acceptance`, estimates and preemption.
Commands are structured arguments, never inventory prose executed by a shell.
Acceptance is an explicit command exit/result contract or a legacy helper packet
requiring independent review. Task completion, execution outcome, evidence
validity and engineering acceptance remain separate. Hold and review commands
are assertions by the authorized operator, not authentication mechanisms.

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
Use `examples/live_agent.py --help` for the separate, explicitly configured real
model exercise. The latter makes actual model calls and preserves their evidence;
`--prepare-only` does not. The examples and tests remain checkout-only resources.

`start inventory.json` creates once and runs in the foreground. `status`,
`explain`, and `report` derive from the database; `events --after N` gives incremental
decisions. `pause` prevents dispatch; `drain` finishes active work; `stop` persists
the decision and requests owned cancellation even when the loop has died. After
an explicit `resume`, run `recover` to restart the loop. Recovery itself never
clears user controls. `run --max-seconds N` bounds the observing loop only: owned
execution survives it, and its original deadline/timeout still applies.

The loop polls with bounded backoff (50–500 ms). A late timer, new submission or
accepted prerequisite wakes it without another model turn. It remains available
while held or review-dependent inventory exists, until its wall/service budget or
a user control ends it. It exits once the finite inventory is terminal. Adding
new work to an exited run requires `recover`.

`submit tasks.json --parent-attempt ID` admits a worker's list through the same
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
report. Without a template, use `record` for authorized independent acceptance.
Stage completions are excluded from useful-result pass/failure metrics.

The helper reducer enforces the original checks, one evidence-based repair and
actor separation. It does not authenticate reviewer identities or establish that
arbitrary claimed check references were executed. Represent required actual tests
as process tasks with explicit result contracts and use their narrow evidence
dependencies; engineering judgment must assess the patch and coverage.

`resolve --task ID --operation ATTEMPT resolution.json` requires references in
`{"evidence":["supported resolution of the same operation"]}` and verified
execution release. It retains the hold in history and never changes model,
account, permissions, deadlines or consumed budgets. Helper interruptions use
their matching `record --kind interruption` schema instead. A lost runner with
unknown descendants cannot be released by an operator's bookkeeping assertion.

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
reservations. No suspend/resume capability is claimed: supported task types are
nonpreemptible or explicitly safe cancellation-and-restart.

Inputs are individual files, not implicit repository-wide snapshots. Evidence
binds their hashes, declared output hashes, dependency evidence, task/environment
configuration and runtime hashes. A bounded inode/size/mtime/ctime hash cache
avoids re-reading unchanged artifacts on every poll. Declare all correctness-
relevant files, flags, environment and toolchain context; undeclared changes
cannot be inferred. Final stdout equality and declared exit contracts are real
process evidence; JSON answers are only their explicitly checked bounded result.

Current limits are deliberately visible: no automatic host-wide CPU/memory
pressure controller, no nested model delegation, no native-subagent integration,
no exhaustive builtin tool allowlist, and no automatic release after an
unidentifiable runner death. Capacity is declared admission, not measured global
enforcement. The benchmark is a deterministic simulation; it includes poor-
estimate regressions and does not establish universal throughput gains.
