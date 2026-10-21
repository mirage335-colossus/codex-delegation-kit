# Host-launched swarm probe

**Outcome: two diagnostics completed, the repeatability probe ended inconclusive at its cutoff.** This is a successful runtime exercise after an explicit setup intervention, not an unassisted first-pass success. The original run at `run/` was left stopped with its three PATH-alias holds; this new run used `host-run/` and the existing inventory.

## Intervention and settings

The controller start used the user-authorized `require_escalated` host launcher after the original run’s three sessions failed before inference. No worker settings were broadened: each successful session verified `gpt-6-luna` / medium / default, approval never, network disabled, `environmentId: local`, and workspace-write rooted at its exact controller-created private copy. Capacity remained 2 reasoning, 2 processes and 2 CPU; run limits remained 240 seconds active and 300 seconds wall deadline. The main chat’s own effective service tier is not separately exposed by telemetry. The escalation applies only to this new controller process; no alternate model, account, backend, X11, retry of the old run, or worker permission change occurred.

## Probe results and automatic scheduling

The parser probe matched all three expected parsed lists and reported `hypothesis_rejected`; it does not establish reducer behavior. The reducer probe created and compiled `reducer_probe.py` under generated `TMPDIR`, imported actual private-copy `totals.py`, and observed `aggregate([7])=0` vs 7, `aggregate([2,3])=3` vs 5, and `total("2,3")=3` vs 5; it reported `failure_reproduced`. The wrapper source was captured at `host-captured-reducer_probe.py` before cleanup. The capsule records a non-UTF-8 omission for compiled `.pyc`; its source wrapper is retained.

The third task was queued behind both fast probes and dispatched after capacity released. Its direct-call command started with the 25-second timeout; the executor recorded it in progress with no completed output, then verified a budget cutoff and process release. The tool did not return a baseline value, the 60-second sleep did not finish, and no after-delay comparison was observed. The correct outcome is `inconclusive`, not a diagnostic pass/failure or setup hold.

All three workspaces were cleaned only after their receipts were released and capsule evidence committed; `host-run/workspaces/` is empty. No source or test file changed. The prior stopped run and holds remain intact. The new run was durably stopped with zero active work.

## Evidence

`host-result-swarm-parser.json`, `host-result-swarm-reducer.json`, `host-result-swarm-repeatability-cutoff.json`, `host-settings.json`, `host-timings.json`, `host-events.json`, `host-status.json`, and `host-final-status.json` retain individual outcomes, actual commands, thread/settings identities, receipts, cleanup state and event timing.

Source snapshot hashes (unchanged after the probes): `totals.py` `7eaedc46536ed878311cd976f85877e0b2f7792fc5b3c64601de1cbff555d300`; `test_totals.py` `745ec14ec8368fafd39f184f5db6905e963cc7a399b7b9b4f24841043988d339`.
