# Codex delegation kit

This user-level Codex kit provides a focused read-only scout role, a bounded
implementation role, and a strong review/takeover role. It preserves the
primary model and effort selected for the user's chat. Read [`policy.md`](policy.md)
for the full operating guidance, including delegation boundaries, evidence,
review, escalation, and validation.

## Requirements and model support

Cloning requires Git. The installer and evidence helper require Linux and
Python 3.11 or newer; those are the verified runtime prerequisites. They use
only the Python standard library and install no packages or services. The
installer uses Linux filesystem operations and is not documented as portable
to Windows.

Role files pin their requested models and reasoning efforts. Before activating
the kit, verify that the Codex client in use supports the requested model and
effort for the operation. In particular, `sol_expert` requests `gpt-6.1-sol`
with `ultra`; the Luna roles request `gpt-6-luna` with `high`. Availability
depends on the client and account. If a role cannot be run at its configured
settings, follow the policy's escalation guidance; do not silently substitute
settings. A native role selector is preferred where available. Explicit model
and effort overrides are the documented fallback only when the client exposes
them; a role name alone does not load a role file.

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
project configuration, or local edits. Review the preview and preserve any
needed files before making separate cleanup decisions. Start a fresh Codex
session after installing, updating role instructions, or disabling: existing
sessions may retain instructions already loaded.

The runtime install contains exactly eight files: this README, `policy.md`,
`supervisor.py`, `install.py`, `uninstall.py`, and the three role TOML files in
`agents/`. `CONTRIBUTING.md`, `tests/`, and `examples/` are clone-only
development resources and are not copied into the installed bundle. The
policy governs agent behavior; the helpers enforce specific installer and
evidence-ledger checks only. Markdown instructions are not a permission
boundary, and the helpers do not enforce every policy requirement.

## Development (source checkout)

Read `CONTRIBUTING.md` in the clone for development and compatibility guidance.
From the repository root, run the isolated standard-library checks and optional
synthetic helper examples:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B examples/demo.py
```

The examples make no model calls and do not prove live routing or model quality.
These development resources are available in the source checkout only.

## License

Author and CC0 affirmer: **mirage335**.

This repository is dedicated to the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
The full `LICENSE` text is included in the source checkout; it is clone-only
and is not copied into the installed eight-file runtime bundle.
