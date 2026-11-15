> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Actual-primary harness independent diagnosis

2026-11-15 UTC. Same harness assignment and repair history; **not accepted for
server setup or live inference by this review**. This is a requested study
evidence artifact, not a new assignment registry. No server, inference,
credential-content inspection, authentication repair, installation, configuration
change, app-chat creation, or D5 operation occurred.

## Ownership and preserved failures

Existing dirty source
files and the untracked study tree were preserved. The worker's original run was
10/12: helper argv unpack failed before boundary assertions, and the reversed
gateway-marker test exposed an implementation defect. Its one bounded repair
fixed both; the next run was 11/12 because the final namespace assertion wrongly
assumed host and private namespaces cannot reuse a numeric PID. Earlier
allowed-write, denied-write, private-tmpfs and low-child-PID assertions in that
test passed, while its later host-side assertions did not execute. Existing
parent-death and detached-grandchild cleanup tests passed. The worker's evidence
remains in `primary-harness-implementation.md`.

The coordinator's offer of another worker repair was withdrawn. This reviewer
was then assigned source takeover, but its developer-level role explicitly
prohibits source/patch edits. The coordinator corrected the assignment: the
root became the explicit source takeover owner under the same identity and
history, while this agent retained independent read-only diagnosis/acceptance.
Neither correction resets failures, repair allowance, acceptance or settings.
This reviewer changed only this evidence note.

## Independently reproduced defects

Three small non-model Python wrappers imported the actual harness helper. Their
protocol messages and inputs were synthetic; none is evidence of agent behavior.
The wrappers ran with `python3 -B` and exited 0 after reporting observations.

1. **The send path exceeds its RPC deadline.** A synthetic child slept for
   0.8 seconds without reading stdin. Sending a 128 KiB request through
   `Rpc.call` with a 0.100-second deadline raised `TimeoutError` only after
   **0.812 seconds**. `Rpc.send` blocks in raw `stdin.write` before checking the
   read deadline; it also ignores a potentially partial write result. All
   request and server-error replies need a complete, nonblocking write loop
   bounded by the same monotonic deadline. A blocked-read-only test is not
   coverage of this defect.
2. **Synchronous metadata reads consume root completion.** A synthetic child
   returned `turn/completed` for the root before the reply to `thread/read`.
   `Rpc.call` delivered completion to its observer and returned child metadata;
   the following read reported `server EOF before reply`. The original
   `run` observer does not retain completion state, so its main loop can miss
   that completion. Store completion durably in the observer, including during
   `turn/start`, and process it after synchronous calls while collecting the
   final pending child observations without waiting for another completion.
3. **Frozen-source traversal misses directory symlinks.** On a disposable copy
   of V5, adding an unmanifested symlink to an empty directory was accepted by
   `frozen_inventory`. Its `is_file()` filter skips the entry before `safe()`
   can reject it. Validate every traversed node before file filtering, reject
   symlinks/nonregular inputs, and apply the same rule to `verify_prepared`.
   Preserve regressions for empty-directory and broken symlinks.

These are separate from the invalid PID discriminator. The correct namespace
test compares actual child PID/IPC namespace identities with the host identities;
numeric PID collision remains valid.

## Additional source findings and required checks

- Separate actual child `thread/read` RPC responses from native notifications.
  The original `study/ownedThreadRead` entry inside the native-event stream
  incorrectly presents a driver-created envelope as a server notification.
- Preserve supported `turn/interrupt` on externally requested termination,
  then bounded owned cleanup. Namespace parent-death protection remains useful
  but does not itself send an interrupt.
- A reaped launcher with no observed PID namespace must receive a limited
  cleanup classification. It is not observed namespace-release evidence.
- Validate own-tree membership before reading child history. The original
  observer adds receivers of every collaboration operation, including message
  or resume operations; an arbitrary referenced ID is not established as a
  newly owned child. Use native spawn provenance or validated parent metadata.
- Verify available ephemeral-root metadata and reject explicit persistence
  contradictions. Confirm schema fields with the existing version-matched
  schema evidence before requiring them; unavailable fields are visibility
  gaps, not proof of persistence or an invented approval requirement.
- Existing tests validate preparation components and a simplified bwrap
  boundary. Add a successful complete synthetic preparation/verification round
  trip and an actual assembled-containment smoke check before real server setup.
- Protocol/event byte limits do not bound runtime logs, scratch, tmpfs or memory.
  Do not claim an aggregate storage, memory or token cap. Enforce any actual
  experimental output/storage limit selected for a later live run, and retain
  its accounting limits explicitly.

The source owner received all findings through native messages. This reviewer
did not rerun the unchanged 11/12 suite or alter source/test files. The next
reviewable essential suite command is:

```sh
python3 -B -m unittest discover \
  -s studies/autonomous-scientific-depth-2026-11-14/tools/tests \
  -p 'test_primary_lifecycle*.py' -v
```

Remaining acceptance is the source owner's repair, focused regressions for the
confirmed defects and necessary contract gaps, essential non-model checks, and
independent review of that final patch. A setup-only private stdio check may
follow those prerequisites under the existing scope; it must initialize, inspect
safe configuration and the ephemeral root, and close without `turn/start`.
Retain genuine startup failures without changing authentication or guards.
Live inference remains outside this reviewer assignment. No gate compliance,
scientific-depth reliability, authenticated inference, child-history coverage,
or local/sidebar/remote visibility is established here.

## Review of the root owner's repair

The same reviewer subsequently inspected the repaired source and regressions.
The owner reported these non-model suite results, which this reviewer did not
redundantly rerun: **12/12** after correcting the PID/IPC discriminator;
**18/18** after the protocol/inventory/cleanup repairs; and **20/20** after the
complete synthetic preparation and actual assembled-containment smoke test
(0.586 seconds for the final suite). During the final test addition, a misplaced
prior configuration assertion caused `NameError` after the assembled-mount
assertions had already passed. The owner moved that assertion back into its
original test and reran the suite successfully. That test-edit failure is
preserved and does not erase the earlier coverage.

Inspection confirms complete nonblocking writes with shared deadlines,
`NativeTree` completion retention across synchronous calls, distinct
`rpc_response` evidence, spawn/parentage-based child admission, validation of
all traversed inventory nodes, explicit ephemeral-persistence contradiction
holds, honest unknown-namespace cleanup classification, and preservation of
inherited network/profile restriction indicators. The complete synthetic
preparation uses fake authentication sentinels and does not hash credentials;
its assembled bwrap smoke exercises actual fixture immutability, scratch
writes, gateway availability and hidden history/evidence paths.

**Setup-only acceptance:** the repaired source and reported non-model checks
support one authorized setup-only attempt with real prepared inputs. This is
permission to test existing authorization, not a claim that startup, role
visibility or authentication works. The root owner may initialize, inspect
safe configuration, create/read the ephemeral root and close without any
`turn/start`. Real startup failure must remain a hold without weakened guards
or authentication repair. This reviewer ran no server or inference.

**Live readiness remains conditional** on successful setup and two additional
confirmed evidence/deadline repairs. Two bounded `python3 -B` wrappers imported
the actual helper and exited 0 after reporting these observations:

1. `Rpc.read` with a buffered `{}\n` and a deadline one second in the past
   returned `{}` instead of raising `TimeoutError`. Check the deadline before
   returning buffered messages, not only while waiting for another newline.
2. A synthetic full `run(..., live=True)` wrapper returned valid fake setup
   metadata, then raised `OSError` on its fake `turn/start` call. No real
   executable/server/model was involved. The final state was `setup_hold`,
   `turn_started=false`, although the durable
   `turn-dispatch-may-have-occurred` fence existed. Preserve attempted-versus-
   acknowledged dispatch and its uncertainty in the final evidence; a lost
   reply can follow actual inference and must not be reported as a known
   pre-turn setup failure. The existing fence still prevents replay.

The earlier signal-handling and aggregate-storage observations remain disclosed
limitations, not new setup gates. The settled contract requires timeout
interruption and parent-death/descendant cleanup; it does not independently
mandate a particular external-signal handler or establish an aggregate storage,
memory or token cap. The source must not claim enforcement it lacks. Required
live lifecycle observation, own-child history and autonomous adviser behavior
remain unexecuted and cannot be accepted from synthetic fixtures.

## Final preflight readiness review

**Accepted for one fresh bounded 20-minute actual-primary lifecycle smoke**
under the frozen task, unchanged V5 source and existing containment/settings.
This accepts an observation run, not its prospective lifecycle result or any
scientific-depth claim. No concrete remaining blocker to that single smoke was
found. This reviewer did not launch inference or a server.

The root repaired both final findings: `Rpc.read` now checks its deadline before
consuming buffered input and again before return; dispatch evidence separates
attempted and acknowledged `turn/start`, preserves `dispatch_uncertain` on a
lost reply, and uses `turn_started=null` while acknowledgment is unknown. The
root reported **22/22**, then **24/24** passing tests (0.588 seconds for the final
reported run) after subsequent startup-specific repairs.

The additional setup repairs retain the boundary: one canonical concurrency
field; private writable binds for `CODEX_HOME/tmp` and `installation_id` whose
host sources are inside the owned runtime directory; a read-only frozen-source
alias at the installed-role path; and acceptance only of optional runtime-added
`nickname_candidates` with null/list-of-strings shape. All other role fields
still compare exactly. The driver now freezes and verifies its own hash and
checks every bind source for symlinks. These are process-local changes, not
active configuration or installation changes.

The reviewer read the safe retained results for setup operations s21–s24:

- s21: `setup_hold`, `server EOF before reply`.
- s22: `setup_hold`, candidate role entry not confirmed.
- s23: `setup_hold`, diagnostic fields isolated the additional
  `nickname_candidates` property; all expected role fields matched.
- s24: `setup_completed`.

All four results record no turn dispatch and observed namespace release. The
earlier startup failures remain preserved in their own operation directories
and the owner's `evaluation/primary-preflight/setup-s21` through `setup-s24`
archives; none was silently retried in place. s24 records an ephemeral root,
null rollout path, no parent/agent role, `gpt-6-astra` / `ultra`, provider
`openai`, native `readOnly` sandbox, approval `never`, and the expected global
instruction path. Its observed `default` service tier is runtime metadata;
the selected main-chat tier remains unknown and no tier override was introduced.

The reviewed driver matched s24's frozen hash:
`284cd71d972d05d8e40087a53d0c2e0fc0582ca1932c3a0eb23fd3ddabcff79a`.
The reviewer independently ran these changed-path tests from `tools/tests`:

```sh
python3 -B -m unittest \
  test_primary_lifecycle.PreparationTests.test_full_synthetic_prepare_and_assembled_containment \
  test_primary_lifecycle.PreparationTests.test_one_concurrency_spelling_and_no_raw_response_option \
  test_primary_lifecycle.PreparationTests.test_runtime_display_defaults_do_not_mask_role_changes \
  test_primary_lifecycle.ProtocolTests.test_synthetic_buffered_message_still_obeys_deadline \
  test_primary_lifecycle.ProtocolTests.test_dispatch_uncertainty_cannot_be_downgraded_to_setup_hold -v
```

Result: **5/5 passed in 0.290 seconds**. An additional actual-helper synthetic
counterexample check accepted a valid nickname list, rejected numeric nickname
metadata and rejected an additional role `model` field. No full unchanged suite
was repeated by this reviewer.

The smoke must use a newly prepared operation; s21–s24 have consumed launch
fences. The original root must invoke both advisers itself, with no driver
reminders or scientific rescue. Native concurrency configuration and the
monotonic deadline have implemented controls; the task's total-helper and public
web-item ceilings must also be assessed from observations and are not separate
hard driver counters. No aggregate token/storage/memory cap is established.
Actual authentication/inference, native child tools, history completeness, gate
ordering, adviser returns and feasible follow-through remain the purpose of
the smoke and must be evaluated from its evidence. A completed root status
alone will not establish those outcomes. The frozen tiny ledger task is a
lifecycle prerequisite, not a scientific-depth confirmation episode.
