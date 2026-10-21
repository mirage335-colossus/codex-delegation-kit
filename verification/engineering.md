# Engineering controller delivery

Validated October 20, 2026 (America/Chicago). Maintained source is
`https://github.com/mirage335-colossus/codex-delegation-kit.git`, checkout
`/home/user/___quick/maintenance-cloud/codex-delegation-kit`. Starting revision
`cfe6cc5ae65b0f280cc0f4d461ad30fd332fccd4` was clean. The delivered changes remain
uncommitted; no commit, push, publication, or unrelated workload was performed.
The installed manifest's source path was verified against this Git checkout.

## Result and implementation

The existing standard-library controller now dispatches real engineering work
through independent local Codex app-server sessions. It reuses the SQLite state,
scheduler, owned process runner, helper acceptance reducer and installer. It adds
one private-repository snapshot/copy module and an engineering backend profile;
there is no new service, framework, scheduler or competing ledger.

Original repositories are read-only inputs. Code creates independent private
copies, stable task/attempt identities, scratch locations, snapshots and command
records. Scouts can inspect actual source and create/compile/run temporary
wrappers or modified copies within scope. Workers edit owned private files;
reviewers inspect the actual patch and evidence, run checks, and cannot approve
their own authorship. Owner/takeover stages preserve the assignment, patch,
failures, allowances, budget and independent-review requirement. Proposed patches
are retained for authorized integration; they are not automatically merged back.

Task submission, dispatch, observation, evidence ingestion, resource release,
replenishment and restart reconciliation run in code. `result` exposes concise
evidence. `assess` records a genuine interpretation decision about an observed
diagnostic without rewriting its report. `continue` can revalidate an unconsumed
original report after a format correction without rerunning its coding work.
Commands and changed paths derive from actual receipts/snapshots, avoiding
duplicate bookkeeping by workers. Model completion alone never accepts a patch.

## Acceptance evidence

| Evidence class | Result | Record |
| --- | --- | --- |
| Deterministic/synthetic protocol and real controlled-process tests | 213 tests passed in 38.046 seconds; existing tests preserved | [Full log](engineering-tests.txt) |
| A: bounded implementation | Actual source inspection; four original failures among six tests; private reducer correction; all six unchanged tests passed; distinct reviewer inspected and checked it | [Coding/recovery receipts](engineering-coding-recovery.json) |
| B: parallel differential diagnosis | Actual Luna-medium main chat authored its inventory, ran concurrent hypotheses, interpreted evidence, submitted a counterfactual follow-up and completed correction plus independent review | [Diagnostic receipts](engineering-diagnosis.json), [main inventory](engineering-main-inventory.json), [operator report](engineering-main-report.md) |
| C: interruption and recovery | Owned controller terminated during an active native command after patch creation; same worker attempt and patch survived; recovery did not replace coding work; pause/stop persisted until explicit resume | [Coding/recovery receipts](engineering-coding-recovery.json) |
| Actual main-chat settings | All five observed main-chat turn contexts used `gpt-6-luna`, effort `medium` | [Settings evidence](engineering-main-settings.json) |
| Packaging/deployment | Eighteen installed files match source and manifest; repeat preview says `No changes needed.` | [Installation verification](engineering-installation.json) |

A's direct harness finished in approximately 62.5 seconds with two actual model
sessions, including its controlled 25-second recovery window. Its harness is
separate from the actual-main-chat requirement. That main chat is
`01a15ca3-2c20-72d1-9382-fb0333421839`; it received only the source fixture,
problem, limits and normal operating guidance initially, then constructed its
own inventory. It did not invoke a prewritten engineering demo or manually fix
the fixture. All six successful sessions in B (four scouts, worker, reviewer)
resolved Luna/medium/default with approval `never`, disabled worker network,
and the exact local private workspace. A used the same settings. Main-chat
effective service tier was unavailable; runtime settings are not provider-side
per-token identity. No stronger reviewer or takeover model was substituted.

The initial three B scouts started within 0.11 seconds. Parser and reducer
results were ingested about 61 seconds before the original slow branch finished.
The reducer scout actually created and compiled a scratch wrapper and compared
the actual helper against matched expected sums: `[2,3]` produced 3 instead of 5,
`[7]` produced 0 instead of 7, and empty input produced 0. A missing `python`
executable was retained as a setup error before its successful `python3` check.
The parser hypothesis was rejected from actual parsed-list comparisons.

The first diagnostic pass did not release correction immediately: the reducer
reported `observed` rather than the required `failure_reproduced` label. The main
chat explicitly assessed its evidence using the new supported command. Later,
the original correction started at Unix time 1792556184.18 and was ingested at
1792556200.94 while the added counterfactual experiment remained active until
1792556250.50. That experiment compiled a modified scratch copy and compared the
same five cases against the original; baseline mismatched four, candidate matched
all five. Its 45-second delay tested overlap, not a timing qualification.

The original correction had exactly one coding attempt. Its malformed command
report was retained, revalidated from actual receipts, and then independently
reviewed. The reviewer independently ran all six unchanged tests. The final run
reported 4/4 original tasks complete, the additional diagnostic complete, all nine
attempts released (including three initial setup failures), no holds, and stopped.
Original source hashes remained unchanged in both live exercises.

## Interventions and limits

This was **assisted end-to-end validation**, not unassisted first-pass proof.
Live development exposed and corrected these issues while preserving evidence:

- The old reasoning profile disabled both the tool host and execution
  environments. Engineering now selects the verified local environment and
  bundled host at thread and turn start. Initial mismatches and held attempts
  remain in [setup history](engineering-setup-history.json).
- App-server initialization required the authorized host launcher because the
  invoking shell could not write runtime state. Workers retained their narrower
  verified workspace sandbox. The main chat explicitly resolved the exact
  released setup holds; no restriction triggered model/account/backend changes.
- The diagnostic label required explicit engineering interpretation. The original
  report and its label remain intact beside the separate assessment.
- The original stored prompt allowed an ambiguous command representation.
  Receipt-derived commands and explicit retained-report revalidation fixed this
  without rerunning coding, resetting budgets or claiming acceptance. The
  reviewer was delayed by this correction, not by the slow experiment.
- The main chat's final narrative retained a stale heading/session count despite
  correct durable status. The copied delivery narrative corrects those two
  fields from state. Code-derived status is authoritative.

These sessions are not native subagents of the main chat. The OS write boundary
is the entire private workspace; narrower file ownership is audited after
execution. Command guidance is not an executable allowlist or OS sandbox.
Filesystem reads outside the workspace, unrelated execution and global/per-command
CPU or memory use are not fully restricted/accounted by this adapter. Commands
and descendants share the assignment reservation until the Linux owned runner
confirms release. No safe suspension/checkpoint mechanism is claimed. Unknown
survival remains held; stopping a chat alone has no controller stop bridge.

The snapshot adapter deliberately supports bounded standalone Git repositories;
linked worktrees, symlinks, submodules/nested repositories and oversized inputs
are rejected explicitly. Owner/repair semantics have focused deterministic
coverage; these successful live fixtures did not require an implementation
takeover. Independent review was exercised live. These fixtures do not establish
large-repository performance, general model reliability, or globally optimal
scheduling. Existing scheduling benchmarks remain the historical records; this
extension does not introduce a new scheduling algorithm or benchmark claim.

Consequential backend, ownership, recovery, evidence, acceptance and packaging
changes received independent review. Material findings were resolved; final
independent checks included 35 engineering-controller and 21 backend tests and
inspection of the actual A/B/C receipts.

## Installation and operation

The maintained installer was previewed and applied to `/home/user/.codex`.
Source/install/manifest parity and repeat-install idempotence passed. The runtime
created seven trust entries for disposable test workspaces; after all execution
released, only those additions were removed. Global `config.toml` and `AGENTS.md`
then matched their pre-task hashes exactly. Model, effort, role pins, service-tier
and unrelated configuration settings were preserved. No controller was enabled
for unrelated work. Start a fresh chat to load updated policy/role guidance;
the installed Python controller is available immediately.

See [the quick start](../README.md#submit-engineering-work) and
[run/task format](../ORCHESTRATION.md#engineering-run-and-task-format). The
checkout's `examples/engineering_tasks.py --help` prepares self-contained coding
or differential-diagnosis fixtures without launching inference. Provide your
authorized workspace and explicit permitted model/effort/tier.

```sh
python3 -B controller.py --run /authorized/run start inventory.json
python3 -B controller.py --run /authorized/run status
python3 -B controller.py --run /authorized/run result --task TASK_ID
python3 -B controller.py --run /authorized/run pause --reason "operator pause"
python3 -B controller.py --run /authorized/run recover
python3 -B controller.py --run /authorized/run resume --reason "explicit resume"
python3 -B controller.py --run /authorized/run recover
python3 -B controller.py --run /authorized/run stop --reason "operator stop"
```

`recover` reconciles the same run and respects pause/stop. `pause` stops new
dispatch; `stop` cancels owned execution through supported ownership checks.
Do not start a fresh run against potentially modified copies to avoid a hold.
Reports keep original outcomes, deferred/held work, diagnostics, setup errors,
and independently accepted patches distinct. Raw disposable receipts remain
under `/tmp/delegation-engineering-live-a1`, `/tmp/delegation-engineering-live-a2`
and `/tmp/delegation-engineering-main-fixture`; compact durable evidence is saved
alongside this report.
