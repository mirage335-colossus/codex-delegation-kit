#!/usr/bin/env python3
"""Install or disable the global delegation kit; preview changes unless --apply."""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import tomllib
import uuid


LEGACY_FILES = (
    "README.md", "policy.md", "supervisor.py", "install.py", "uninstall.py",
    "agents/luna_scout.toml", "agents/luna_worker.toml", "agents/sol_expert.toml",
)
FILES = LEGACY_FILES + (
    "agents/inherited_scout.toml", "agents/inherited_worker.toml",
    "agents/inherited_reviewer.toml",
)
LEGACY_ROLES = {
    "luna_scout": "Focused read-only source exploration and factual investigation.",
    "luna_worker": "Bounded implementation with settled contracts and acceptance checks.",
    "sol_expert": "Consequential diagnosis, architecture, independent review, and takeover.",
}
ROLES = {
    "luna_scout": "Focused read-only source exploration and factual investigation.",
    "luna_worker": "Bounded implementation with settled contracts and acceptance checks.",
    "sol_expert": "Consequential diagnosis, architecture, independent review, and takeover.",
    "inherited_scout": "Focused read-only source exploration and factual investigation with inherited settings.",
    "inherited_worker": "Bounded implementation with settled contracts and acceptance checks with inherited settings.",
    "inherited_reviewer": "Consequential diagnosis, independent review, and takeover with inherited settings.",
}
BEGIN = "# >>> CODEX GLOBAL DELEGATION KIT (managed; do not edit) >>>"
END = "# <<< CODEX GLOBAL DELEGATION KIT <<<"


class Refusal(RuntimeError):
    """A preflight or concurrent-edit check failed."""


@dataclasses.dataclass(frozen=True)
class State:
    data: bytes | None
    mode: int = 0o600


@dataclasses.dataclass(frozen=True)
class Change:
    path: Path
    before: State
    after: State


def safe_path(path: Path) -> None:
    """Do not traverse symlinks, even in an ancestor of an absent destination."""
    for item in (path, *path.parents):
        if item.is_symlink():
            raise Refusal(f"Symlink is not allowed: {item}")


def read_state(path: Path) -> State:
    safe_path(path)
    try:
        info = path.stat()
    except FileNotFoundError:
        return State(None)
    if not stat.S_ISREG(info.st_mode):
        raise Refusal(f"Expected a regular file: {path}")
    return State(path.read_bytes(), stat.S_IMODE(info.st_mode))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode(data: bytes | None, path: Path) -> str:
    try:
        return (data or b"").decode("utf-8")
    except UnicodeDecodeError as error:
        raise Refusal(f"Expected UTF-8 text: {path}") from error


def parse_toml(data: bytes | None, path: Path) -> dict:
    try:
        return tomllib.loads(decode(data, path))
    except tomllib.TOMLDecodeError as error:
        raise Refusal(f"Invalid TOML in {path}: {error}") from error


def blocks(target: Path, roles: dict[str, str] = ROLES) -> dict[str, str]:
    instructions = (
        f"{BEGIN}\n"
        "For coding, repository investigation, debugging, software design, and technical factual research tasks, "
        f"read and follow `{target / 'policy.md'}` before deciding whether to delegate.\n"
        "Preserve the user's selected primary model. Project contracts and authorization "
        "constraints remain applicable.\n"
        f"{END}\n"
    )
    config = [BEGIN]
    for role, description in roles.items():
        config.extend([
            f"[agents.{role}]",
            f"description = {json.dumps(description)}",
            f"config_file = {json.dumps(str(target / 'agents' / (role + '.toml')))}",
            "",
        ])
    config.extend([END, ""])
    return {"AGENTS.md": instructions, "config.toml": "\n".join(config)}


def check_personal_roles(home: Path) -> None:
    """Standalone discovery can use the internal name rather than the filename."""
    directory = home / "agents"
    safe_path(directory)
    if not directory.exists():
        return
    if not directory.is_dir():
        raise Refusal(f"Expected a personal agent directory: {directory}")
    for path in sorted(directory.rglob("*.toml")):
        configuration = parse_toml(read_state(path).data, path)
        name = configuration.get("name")
        if not isinstance(name, str) or not name.strip():
            raise Refusal(f"Cannot determine standalone agent name safely: {path}")
        if name in ROLES or path.stem in ROLES:
            raise Refusal(f"Personal agent discovery conflicts with a kit role: {path} (name={name!r})")


def strip_block(text: str, inserted: str | None, path: Path) -> str:
    if inserted is None:
        if BEGIN in text or END in text:
            raise Refusal(f"Unowned or incomplete managed markers in {path}")
        return text
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.count(inserted) != 1:
        raise Refusal(f"Managed block was modified or is incomplete in {path}; inspect manually")
    return text.replace(inserted, "", 1)


def load_manifest(path: Path, home: Path, expected: dict[str, str]) -> tuple[State, dict | None]:
    state = read_state(path)
    if state.data is None:
        return state, None
    try:
        value = json.loads(decode(state.data, path))
        if value["version"] != 1 or value["home"] != str(home) or type(value["active"]) is not bool:
            raise ValueError("unexpected version, home, or active flag")
        if "source_directory" in value:
            source_directory = value["source_directory"]
            if (not isinstance(source_directory, str) or not source_directory
                    or "\0" in source_directory or not Path(source_directory).is_absolute()):
                raise ValueError("invalid source directory")
        inventory = set(value["bundle_digests"])
        if inventory not in (set(LEGACY_FILES), set(FILES)):
            raise ValueError("unexpected bundle file list")
        legacy_expected = blocks(home / "delegation-kit", LEGACY_ROLES)
        activation_names = set(value["activation"])
        legacy_layout = inventory == set(LEGACY_FILES) and activation_names == set(legacy_expected)
        current_layout = inventory == set(FILES) and activation_names == set(expected)
        if not (legacy_layout or current_layout):
            raise ValueError("unexpected activation file list")
        known_blocks = legacy_expected if inventory == set(LEGACY_FILES) else expected
        for name, block in known_blocks.items():
            record = value["activation"][name]
            if record["inserted"] not in (block, "\n" + block):
                raise ValueError("unexpected managed block")
            if type(record["original_exists"]) is not bool:
                raise ValueError("invalid original file state")
        return state, value
    except (ValueError, TypeError, KeyError) as error:
        raise Refusal(f"Invalid installation manifest {path}: {error}") from error


def plan(home: Path, source: Path, uninstall: bool = False) -> list[Change]:
    home = home.absolute()
    source = source.absolute()
    if any(character in str(home) for character in "\n\r`"):
        raise Refusal("Codex home contains characters unsuitable for the instruction link")
    target = home / "delegation-kit"
    for directory in (home, target, source):
        safe_path(directory)
        if directory.exists() and not directory.is_dir():
            raise Refusal(f"Expected a directory: {directory}")
    expected = blocks(target)
    legacy_expected = blocks(target, LEGACY_ROLES)
    manifest_path = target / ".installation" / "manifest.json"
    manifest_state, previous = load_manifest(manifest_path, home, expected)
    if target.exists() and previous is None and any(target.iterdir()):
        raise Refusal(f"Existing nonempty destination has no installation manifest: {target}")
    if uninstall and previous is None:
        raise Refusal(f"No owned installation found at {target}")

    globals_before = {name: read_state(home / name) for name in expected}
    globals_clean = {}
    for name, state in globals_before.items():
        inserted = (previous["activation"].get(name, {}).get("inserted")
                    if previous and previous["active"] else None)
        globals_clean[name] = strip_block(decode(state.data, home / name), inserted, home / name)
    configuration = parse_toml(globals_before["config.toml"].data, home / "config.toml")
    clean_configuration = parse_toml(globals_clean["config.toml"].encode(), home / "config.toml")
    for configuration_to_check in (configuration, clean_configuration):
        if "agents" in configuration_to_check and not isinstance(configuration_to_check["agents"], dict):
            raise Refusal("config.toml agents must be a table")
    for role in ROLES:
        if role in clean_configuration.get("agents", {}):
            raise Refusal(f"Existing agent role conflicts with the kit: {role}")

    changes: list[Change] = []
    activation = {}
    if not uninstall:
        check_personal_roles(home)
        override = read_state(home / "AGENTS.override.md")
        if override.data and override.data.strip():
            raise Refusal(f"{home / 'AGENTS.override.md'} suppresses global AGENTS.md; resolve it first")
        bundle_digests = {}
        for name in FILES:
            original = read_state(source / name)
            if original.data is None:
                raise Refusal(f"Required bundle file is missing: {source / name}")
            if name.endswith(".toml"):
                parse_toml(original.data, source / name)
            installed = read_state(target / name)
            bundle_digests[name] = digest(original.data)
            if (installed.data is not None and previous is not None
                    and name not in previous["bundle_digests"]):
                raise Refusal(f"Existing inherited role file is not owned by the prior installation: {target / name}")
            if installed.data is not None and installed.data != original.data:
                if previous is None or digest(installed.data) != previous["bundle_digests"].get(name):
                    raise Refusal(f"Installed file has local edits; refusing to overwrite: {target / name}")
            desired = State(original.data, installed.mode if installed.data is not None else original.mode)
            if installed != desired:
                changes.append(Change(target / name, installed, desired))
        for name, block in expected.items():
            before = globals_before[name]
            text = globals_clean[name]
            original_exists = before.data is not None
            if previous and previous["active"] and name in previous["activation"]:
                old = previous["activation"][name]
                old_prefix = "\n" if old["inserted"].startswith("\n") else ""
                inserted = old_prefix + block
                if name == "AGENTS.md":
                    after_text = decode(before.data, home / name)
                else:
                    # Replace the exact owned configuration block at its original position.
                    raw = decode(before.data, home / name)
                    prior_block = old["inserted"]
                    if raw.count(prior_block) != 1:
                        raise Refusal(f"Managed block was modified or is incomplete in {home / name}; inspect manually")
                    after_text = raw.replace(prior_block, inserted, 1)
                original_exists = old["original_exists"]
            else:
                inserted = ("\n" if text and not text.endswith("\n") else "") + block
                after_text = text + inserted
            activation[name] = {"inserted": inserted, "original_exists": original_exists}
            after = State(after_text.encode(), before.mode if before.data is not None else (0o644 if name == "AGENTS.md" else 0o600))
            if before != after:
                changes.append(Change(home / name, before, after))
        parse_toml(next((change.after.data for change in changes if change.path == home / "config.toml"), globals_before["config.toml"].data), home / "config.toml")
    else:
        bundle_digests = previous["bundle_digests"]
        if previous["active"]:
            for name, text in globals_clean.items():
                before = globals_before[name]
                remove = not text and not previous["activation"][name]["original_exists"]
                after = State(None) if remove else State(text.encode(), before.mode)
                changes.append(Change(home / name, before, after))
        else:
            return []

    # This is a discovery hint, not proof of a Git checkout or permission to use it.
    # Running the installed utility (including disable) must not replace the
    # external source location with the deployment directory.
    source_directory = previous.get("source_directory") if previous else None
    if not uninstall and os.path.abspath(source) != os.path.abspath(target):
        source_directory = os.path.abspath(source)
    provenance_changed = previous is not None and previous.get("source_directory") != source_directory
    if not changes and not provenance_changed:
        return []
    transaction_id = uuid.uuid4().hex
    backup_root = target / ".installation" / "backups" / transaction_id
    backups = []
    for name, before in globals_before.items():
        if before.data is not None:
            changes.append(Change(backup_root / name, State(None), State(before.data, 0o600)))
            backups.append(str(backup_root / name))
    if manifest_state.data is not None:
        changes.append(Change(backup_root / "manifest.json", State(None), State(manifest_state.data)))
    manifest = {
        "version": 1, "home": str(home), "active": not uninstall,
        "activation": activation if not uninstall else previous["activation"],
        "bundle_digests": bundle_digests,
        "last_backups": backups,
    }
    if source_directory is not None:
        manifest["source_directory"] = source_directory
    changes.append(Change(manifest_path, manifest_state, State((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())))
    return changes


def _stage(path: Path, state: State) -> Path:
    descriptor, filename = tempfile.mkstemp(prefix=".delegation-kit-", dir=path.parent)
    staged = Path(filename)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            os.fchmod(stream.fileno(), state.mode)
            stream.write(state.data)
            stream.flush()
            os.fsync(stream.fileno())
        return staged
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


def apply(changes: list[Change]) -> None:
    """Stage first, compare before each replacement, and roll back this transaction only."""
    staged: dict[Path, Path] = {}
    directories: list[Path] = []
    committed: list[Change] = []
    try:
        for change in changes:
            if read_state(change.path) != change.before:
                raise Refusal(f"File changed since preflight: {change.path}")
        for change in changes:
            missing = []
            current = change.path.parent
            while not current.exists():
                missing.append(current)
                current = current.parent
            for directory in reversed(missing):
                directory.mkdir(mode=0o700)
                directories.append(directory)
            if change.after.data is not None:
                staged[change.path] = _stage(change.path, change.after)
        for change in changes:
            if read_state(change.path) != change.before:
                raise Refusal(f"File changed during installation: {change.path}")
            if change.after.data is None:
                change.path.unlink()
            else:
                os.replace(staged[change.path], change.path)
                staged.pop(change.path)
            committed.append(change)
    except BaseException as error:
        rollback_errors = []
        for change in reversed(committed):
            try:
                if read_state(change.path) != change.after:
                    raise Refusal(f"Concurrent edit preserved during rollback: {change.path}")
                if change.before.data is None:
                    change.path.unlink()
                else:
                    temporary = _stage(change.path, change.before)
                    try:
                        os.replace(temporary, change.path)
                    finally:
                        temporary.unlink(missing_ok=True)
            except BaseException as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise Refusal(f"Transaction failed: {error}; rollback needs attention: {'; '.join(rollback_errors)}") from error
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        for directory in reversed(directories):
            try:
                directory.rmdir()
            except OSError:
                pass


def preview(changes: list[Change]) -> None:
    for change in changes:
        if ".installation" in change.path.parts:
            print(f"Save installation metadata/backup: {change.path}")
            continue
        before = decode(change.before.data, change.path).splitlines(keepends=True)
        after = decode(change.after.data, change.path).splitlines(keepends=True)
        for line in difflib.unified_diff(before, after, fromfile=str(change.path) + " (before)", tofile=str(change.path) + " (after)"):
            sys.stdout.write(line)
            if not line.endswith("\n"):
                sys.stdout.write("\n\\ No newline at end of file\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))), help="Codex home (default: CODEX_HOME or ~/.codex)")
    parser.add_argument("--source", type=Path, default=Path(__file__).absolute().parent, help="source bundle directory")
    parser.add_argument("--apply", action="store_true", help="apply the previewed installation or disable operation")
    parser.add_argument("--uninstall", action="store_true", help="remove only owned activation blocks; retain bundle and evidence")
    args = parser.parse_args(argv)
    try:
        changes = plan(args.home.expanduser(), args.source.expanduser(), args.uninstall)
        preview(changes)
        if not changes:
            print("No changes needed.")
        elif args.apply:
            apply(changes)
            print("Kit disabled; bundle and evidence retained." if args.uninstall else "Global delegation kit installed and activated.")
        else:
            print("Dry run only. Add --apply to make these changes.")
        return 0
    except (Refusal, OSError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
