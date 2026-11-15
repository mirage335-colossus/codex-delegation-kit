> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Actual-primary harness implementation evidence

2026-11-15 UTC. **Partial implementation, not accepted for live use.** No model
inference, server setup, installation, login, credential-content inspection,
active configuration edit, app-chat creation, or D5 operation occurred here.

## Scope and source

The maintained checkout is `/home/user/___quick/p/_cur/codex-delegation-kit`. Existing dirty root files and
the untracked study tree were preserved. This assignment changed only:

- `tools/primary_lifecycle.py`
- `tools/tests/test_primary_lifecycle.py`
- this note

Paths above are relative to this study. The source-v5 candidate remains frozen
at `evaluation/source-v5/checkout`; its manifest contains 23 runtime files and
two test files. The actual inventory/hash test passed. No runtime inventory,
installer, role pin, policy, backend, global installation, commit, or push changed.

The adapter has three explicit operations. `prepare` is the default and does
not execute the CLI. It validates and copies the frozen inventory, task and
fixture into a unique direct child of `/tmp`; invokes the frozen installer's
`blocks` function without installation; replaces only the managed global
gateway in a private instruction view; freezes hashes and safe settings; and
rejects symlinks, reused operation paths, instruction overrides and unreviewed
routing environment variables. Credential paths receive metadata checks only;
their contents are never read, hashed or copied by the driver.

`setup` is intended to initialize private stdio, inspect safe configuration,
create/read one fresh ephemeral root, then close with no `turn/start`.
`preflight` is a separate explicit code path that submits the frozen original
task once and observes it. Neither operation dispatches advisers, supplies gate
reminders or injects a delegated-parent exemption. **Neither operation was run.**

The mount plan uses read-only `/`, a private home view exposing only the
official CLI distribution, read-only original config/rules/auth and the staged
gateway; private `/tmp`, `/run`, `/var/tmp`, `/proc`, `/dev`; and writable binds
only for owned runtime and scratch. This excludes the original study, installed
kit, app sockets, session/history/state/log trees from the home view. PID/IPC
isolation and `--die-with-parent` are required. No overlay, network-namespace
workaround, escalation, writable auth, shared daemon, fallback model or provider
substitution is used. Native `read-only` shell sandboxing is requested separately.

The exact selection remains `gpt-6-astra` / `ultra`. Unknown selected service
tier is omitted from both thread and turn overrides. Runtime configuration
responses are projected to safe fields; the full config and environment are
not retained. Supported process-local integration feature settings and named
MCP disable settings are checked before root creation. Source roles retain
their bytes and pins.

## Design correction from version-matched schema

The schema support owner corrected the earlier review's suggestion to enable
`experimentalRawEvents`: that field is internal raw Responses API output, not
additional native collaboration observability. The coordinator accepted omission
of it and raw private reasoning. Standard `item/started` / `item/completed`
collaboration events and own-tree metadata remain the intended evidence route.
See the implementation follow-up in `primary-harness-review.md` for exact local
schema/parser evidence. `model/verification` is not model attestation;
`disabledPluginIds` does not filter plugin capabilities; neither is used to
claim a boundary here. Configured role/model/effort metadata is distinct from
provider-side execution telemetry.

## Executed checks and preserved failures

Command, both runs:

```sh
python3 -B -m unittest discover \
  -s studies/autonomous-scientific-depth-2026-11-14/tools/tests \
  -p 'test_primary_lifecycle*.py' -v
```

First run: **12 tests, 10 passed, 2 failed**.

1. The write-denial probe failed before its assertions with
   `ValueError: too many values to unpack (expected 2)`: the helper unpacked
   all three arguments into two path variables. Zero boundary assertions ran
   in that check. The coordinator authorized slicing the two path arguments.
2. The gateway negative test found that END-before-BEGIN was not rejected when
   the end-marker length overlapped the beginning-marker index. The repair
   compares marker start positions directly. This was an implementation defect;
   both original and corrected tests remain in the same suite.

One coordinator-authorized bounded repair corrected those two issues.
Second run: **12 tests, 11 passed, 1 failed**.

- Frozen inventory and required adviser pins: passed.
- Exact candidate gateway and preservation of unmanaged text, missing/duplicate/
  reversed marker rejection: passed.
- Symlink and frozen-source hash mismatch rejection: passed.
- Reused operation and durable launch/turn-dispatch fence rejection: passed.
- Unknown routing and instruction override rejection: passed.
- Planned mount inventory and auth-read-only/evidence-exclusion assertions: passed.
- Real parent death with detached children: passed.
- Real timeout cleanup with detached grandchild: passed; private PID namespace
  and multiple owned process identities were observed.
- Synthetic partial JSON, RPC errors, truncation, malformed/non-object messages,
  timeout and collaboration/role/effort preservation with reasoning omission:
  passed. These fixtures are explicitly synthetic and prove no model behavior.
- Real write-denial test: **failed at its last assertion**. The corrected helper
  first completed allowed-write, outside-owned-write-denial, private-tmpfs-write
  and low child-PID checks. It then incorrectly asserted that the host parent's
  numeric PID cannot exist under the private `/proc`. Numeric PID collisions
  between namespaces are valid. This failure is not evidence of a namespace
  leak; the discriminator must compare actual PID/IPC namespace identities.
  Host-side assertions after the failed subprocess return did not execute.

The coordinator offered an additional specific repair, but the worker's role
requires a takeover after failure of its one repair. No second source/test repair
was executed. The same assignment, failure history and acceptance conditions
were returned for a permitted takeover, without resetting them.

## Remaining checks and review issues

Setup-only and all inference remain **unexecuted** because the essential
containment suite is not yet green. Full preparation against actual task/fixture
inputs has also not run. The passing inventory and pure preparation unit checks
do not establish complete preparation or startup success.

The takeover should correct the invalid namespace discriminator, rerun the
required suite, then examine these specific implementation gaps before live use:

- Protocol stdin writes are currently blocking; the monotonic read deadline does
  not yet bound a blocked send. External driver termination relies on namespace
  parent-death cleanup, rather than a signal handler first issuing supported
  `turn/interrupt`.
- The byte limits bound protocol/event capture; runtime logs/scratch writes are
  not covered by a hard aggregate storage or memory quota. No aggregate token
  cap is implemented or claimed.
- A `turn/completed` notification received while synchronously reading child
  metadata can currently be consumed by the observer before the main loop sees
  it. Completion observation must survive this interleaving.
- Own-child read results currently use a `study/ownedThreadRead` envelope within
  the native event log. They should be labeled separately as actual RPC response
  evidence, not represented as a native server notification. Child history
  visibility and final child-read timing remain untested.
- Namespace release proof records observed members; startup failure before any
  namespace identity is observed needs an explicit limited cleanup classification.
  A reaped launcher alone should not be presented as observed namespace closure.
- Full mount execution, native shell operation, role availability, ephemeral
  child metadata/history, gate ordering/return/follow-through, authenticated
  inference and local/sidebar/remote visibility are not established by these tests.

The source implementation is reviewable, but its existence is not approval to
launch the live operation. A permitted owner should resolve the listed gaps and
report actual setup errors without weakening the boundary or repairing auth.

## Reviewable command shape after acceptance

The coordinator must supply and freeze the original task, fixture and accepted
resource envelope. The code's current prospective maximum is 1,200 seconds,
two open children, 30 seconds cleanup, and bounded protocol/event bytes; it is
not measured sufficiency or hard token/memory accounting. No task was invented
or launched by this worker.

```sh
python3 -B studies/autonomous-scientific-depth-2026-11-14/tools/primary_lifecycle.py \
  prepare --directory /tmp/primary-lifecycle-SETUP-UNIQUE \
  --task APPROVED_TASK --fixture APPROVED_FIXTURE
python3 -B studies/autonomous-scientific-depth-2026-11-14/tools/primary_lifecycle.py \
  setup --directory /tmp/primary-lifecycle-SETUP-UNIQUE
```

Setup consumes its launch fence. A later accepted live exercise uses a separately
prepared fresh operation with the same frozen approved inputs, then exactly:

```sh
python3 -B studies/autonomous-scientific-depth-2026-11-14/tools/primary_lifecycle.py \
  preflight --directory /tmp/primary-lifecycle-LIVE-UNIQUE --wall-seconds 1200
```

These are explicit command shapes with unresolved input placeholders, not a
ready launch command or a claim that setup/inference succeeded. Unknown launch
status forbids replay of an existing operation directory.
