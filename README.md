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

For substantive tasks, obtain the policy's initial `astra_initial`
(`gpt-6-astra`, `ultra`) consultation before investigation or planning; clearly
trivial mechanical requests are exempt.

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

The runtime bundle has 21 files: this README, `policy.md`,
`ORCHESTRATION.md`, `supervisor.py`, `install.py`, `uninstall.py`,
`controller.py`, `controller_store.py`, `execution.py`, `agent_backend.py`,
`scheduling.py`, `engineering.py`, and nine role TOML files in `agents/`.
`CONTRIBUTING.md`, tests, examples, and verification materials are source-only
and are not installed. The policy describes expected behavior; each program
enforces only its documented checks.

Author and CC0 affirmer: **mirage335**. This repository is dedicated to the
public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
