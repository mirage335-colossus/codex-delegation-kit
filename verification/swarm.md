# Bounded swarm extension

Validated October 21, 2026 (America/Chicago). Maintained source:
`https://github.com/mirage335-colossus/codex-delegation-kit.git`, checkout
`/home/user/___quick/maintenance-cloud/codex-delegation-kit`. Starting revision
`3c8b2c38907fe069d74d28bf750cbf084c79c762` was clean. The installed source hint
was verified against this checkout. This extension remains uncommitted; no push
or publication was performed. Earlier engineering evidence remains historical
in [engineering.md](engineering.md).

## Scope and behavior

Added two concise native roles: selector-free `inherited_swarm` and optional
`luna_swarm` pinned to `gpt-6-luna`, `medium`. All six earlier role files and
pins are unchanged. Inherited operation respects the permitted parent boundary;
the pinned role requires matching authorization. A responsibility never grants
permission to escalate models. Controller `role: "swarm"` uses the existing
scout/backend path and explicit run settings, not a native role pin.

Each compact probe names one hypothesis, discriminating experiment, matched
comparison and permitted commands. Code creates an independent private copy,
scratch directory, attempt and result locations. Source is read-only by role
contract; all writes belong in generated scratch. Wrappers and modified copies
can exercise actual source and compile/run local code. The default 60-second
budget is clamped to run limits. An inconclusive result or verified cutoff
retains observations but creates no result dependency, test result, useful
coverage, automatic retry or model escalation. Stops and restriction holds stay
authoritative. A coordinator chooses a genuinely different permitted experiment
or engineering responsibility when needed.

After released execution and a clean scope audit, code saves evidence outside
the workspace, commits cleanup intent, then deletes only the recorded private
directory inode. Recovery completes interrupted cleanup without rerunning the
probe. Unknown execution, scope violations and holds retain their workspaces.
Cleanup failures remain visible instead of retrying in a loop. Historical
diagnostic assessment verifies the retained capsule and receipt hashes.

## Automated and independent validation

- [Full test log](swarm-tests.txt): **241 tests passed**, 45.837 seconds. Includes
  all earlier checks, 13 new deterministic swarm tests and three real-process
  integrations using explicitly synthetic agent reports.
- Real-process tests cover an escaped descendant, release before deletion and
  replenishment, timeout without coverage, persistent stop and explicit resume,
  and runner loss retaining ownership and preventing replacement.
- Deterministic tests cover scratch-only admission, model preservation,
  inconclusive dependency behavior, cleanup crash boundaries, preserved source,
  historical assessment, capsule mutation, symlinks, oversized source and
  compiled binary cleanup. Backend protocol tests preserve startup/permission
  holds and require acknowledged execution before a typed cutoff.
- [Existing matched scheduling simulation](swarm-benchmark.json): all five
  fixtures still pass the predeclared targets. This is not a swarm scale,
  model-quality or X11 benchmark; no scheduling algorithm changed.
- Independent review resolved an old-install disable collision, a capsule
  hash/parse race, and an ordinary-scout prompt mismatch. No material finding
  remains in the reviewed implementation.

## Live validation and installation

The actual [Luna-medium main chat settings](swarm-main-chat-settings.json) cover
two operator turns in chat `01a15ca3-2c20-72d1-9382-fb0333421839`. The chat
constructed [its own inventory](swarm-main-inventory.json), using two slots for
three probes, and operated the controller through normal commands. It did not
invoke a prewritten demo or perform diagnostic execution outside the controller.

The first launch failed before inference because the outer launcher could not
create Codex PATH aliases. Its three setup holds and stopped run remain intact;
see [initial setup report](swarm-main-initial-setup.md). An explicitly authorized,
reviewed host launch initialized the runtime for a fresh run with identical
worker settings. This was assisted validation, not unassisted first-pass success.
No runtime fix, model/account/backend substitution or worker permission expansion
was needed. All three actual worker sessions resolved Luna/medium/default,
approval never, network disabled, and their exact private workspace.

The [main chat report](swarm-main-report.md), [worker settings](swarm-main-settings.json),
[timing and capsule records](swarm-main-timings.json), and
[final status](swarm-main-final-status.json) show:

- Parser comparisons matched three expected lists and rejected that hypothesis.
- The reducer probe created and compiled a [small wrapper](swarm-main-captured-reducer_probe.py)
  calling actual code. It reproduced `aggregate([7]) == 0` instead of 7 and
  `aggregate([2,3]) == 3` instead of 5, preserving original failing evidence.
- The queued slow probe was claimed about 102 ms after the parser released;
  the reducer was still active. No coordinator turn replenished the slot.
- The slow command started and reached its 25-second cutoff. Its baseline stdout
  was not retained and no after-delay comparison completed. Its inconclusive
  disposition supplies no result label, pass/failure count, or coverage credit.
- All three single attempts released and were ingested. Their capsules verify;
  all three private workspaces were removed after capture. Original source
  hashes are unchanged. The successful runtime test run is durably stopped with
  zero active work and no holds. It honestly reports 2/3 original diagnostic
  outcomes complete, with the remaining question inconclusive.

Independent review checked the actual receipts, settings, wrapper, original
source, cleanup and timing. Main-chat service tier was not exposed; worker tier
was observed. Earlier setup workspaces remain held, rather than being silently
discarded or counted as completed experiments.

[Installation verification](swarm-installation.json): maintained installer
previewed and applied; all 20 files match source and manifest; repeat preview
reports `No changes needed.` Historical 8/11/17/18-file upgrades and disable are
covered by tests. Existing role bytes, global primary settings, unrelated config
bytes and global AGENTS were preserved. Three trust entries automatically created
by the live runtime for the now-deleted test workspaces were removed; no other
configuration was changed outside the managed kit block.

No controller was enabled for unrelated work. Start a fresh chat to load the
new native role registrations; their fresh-chat activation was not separately
exercised. The installed controller is available immediately. Existing retained
runs keep their history and require the documented explicit runtime migration
before continuing against changed controller code. No commit or push was made.

## Operating guide and limits

See [the compact swarm packet and example](../ORCHESTRATION.md#bounded-swarm-probes).
Use existing `start` or `submit`, then `status`, `result` and `report`; code does
the dispatch, ingestion and replenishment. `pause` stops new dispatch; `stop`
persists the user decision and cancels owned execution. Only explicit `resume`
clears it; `recover` restarts observation and pending cleanup, not the probe.
Stopping the controlling chat alone is not a supported controller stop signal.

Native-only roles rely on the agent/coordinator for cleanup and accounting.
Controller sessions are independent sessions, not native children of the main
chat. The runtime sandbox protects the original root; scratch-only scope inside
the private copy is enforced by instructions and post-run audit, not an OS
read-only mount. Command guidance is not an executable sandbox or per-command
resource quota. Allocations do not establish global host resource enforcement.

The capsule keeps bounded text (128 KiB per file, 2 MiB total), hashes, command
receipts and original results. It lists omitted binary/toolchain material and
does not promise a complete replay environment. Oversized scratch source is
retained rather than silently deleted. Durable evidence intentionally remains.

Isolated temporary X11 is conditional on existing, authorized, verifiable
isolation and owned cleanup. Neither Xvfb nor Xephyr is available here; no X11
test or installation was performed. Massive-scale throughput and exponential
narrowing are unverified. More probes help only when they add discriminating
information within allocated capacity.
