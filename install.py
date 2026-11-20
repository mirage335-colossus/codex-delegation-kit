#!/usr/bin/env python3
"""Install or disable explicit-only DK skills; preview changes unless --apply."""

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
# Preserve every published inventory so owned installations remain readable
# during upgrade or disable.
ADVISORY_FILES = LEGACY_FILES + (
    "agents/inherited_scout.toml", "agents/inherited_worker.toml",
    "agents/inherited_reviewer.toml",
)
CONTROLLER_FILES = ADVISORY_FILES + (
    "controller.py", "controller_store.py", "execution.py", "agent_backend.py",
    "scheduling.py", "ORCHESTRATION.md",
)
ENGINEERING_FILES = CONTROLLER_FILES + ("engineering.py",)
SWARM_FILES = ENGINEERING_FILES + (
    "agents/inherited_swarm.toml", "agents/luna_swarm.toml",
)
# Published twenty-one-file bundle and role map. Keep these frozen so its
# activation can be validated after the current bundle gains another role.
OLD21_FILES = (
    "README.md", "policy.md", "supervisor.py", "install.py", "uninstall.py",
    "agents/luna_scout.toml", "agents/luna_worker.toml", "agents/sol_expert.toml",
    "agents/inherited_scout.toml", "agents/inherited_worker.toml",
    "agents/inherited_reviewer.toml",
    "controller.py", "controller_store.py", "execution.py", "agent_backend.py",
    "scheduling.py", "ORCHESTRATION.md", "engineering.py",
    "agents/inherited_swarm.toml", "agents/luna_swarm.toml",
    "agents/astra_expert.toml",
)
LEGACY_ROLES = {
    "luna_scout": "Focused read-only source exploration and factual investigation.",
    "luna_worker": "Bounded implementation with settled contracts and acceptance checks.",
    "sol_expert": "Consequential diagnosis, architecture, independent review, and takeover.",
}
# These descriptions and their order are part of published activation blocks.
PRE_SWARM_ROLES = {
    "luna_scout": "Focused read-only source exploration and factual investigation.",
    "luna_worker": "Bounded implementation with settled contracts and acceptance checks.",
    "sol_expert": "Consequential diagnosis, architecture, independent review, and takeover.",
    "inherited_scout": "Focused read-only source exploration and factual investigation with inherited settings.",
    "inherited_worker": "Bounded implementation with settled contracts and acceptance checks with inherited settings.",
    "inherited_reviewer": "Consequential diagnosis, independent review, and takeover with inherited settings.",
}
PRE_ASTRA_ROLES = {
    **PRE_SWARM_ROLES,
    "inherited_swarm": "Bounded read-only diagnostic experiments with inherited settings.",
    "luna_swarm": "Bounded read-only diagnostic experiments with Luna at medium effort.",
}
OLD21_ROLES = {
    "luna_scout": "Focused read-only source exploration and factual investigation.",
    "luna_worker": "Bounded implementation with settled contracts and acceptance checks.",
    "sol_expert": "Consequential diagnosis, architecture, independent review, and takeover.",
    "inherited_scout": "Focused read-only source exploration and factual investigation with inherited settings.",
    "inherited_worker": "Bounded implementation with settled contracts and acceptance checks with inherited settings.",
    "inherited_reviewer": "Consequential diagnosis, independent review, and takeover with inherited settings.",
    "inherited_swarm": "Bounded read-only diagnostic experiments with inherited settings.",
    "luna_swarm": "Bounded read-only diagnostic experiments with Luna at medium effort.",
    "astra_expert": "Sparse strategic review of difficult engineering decisions.",
}
OLD22_FILES = OLD21_FILES + ("agents/astra_initial.toml",)
OLD22_AGENTS_GATEWAY = (
    "For coding, repository investigation, debugging, software design, and technical factual research, "
    "before substantive work on each new main task, obtain one initial review from the pinned `astra_initial` "
    "role (`gpt-6-astra` at `ultra`) using only the original prompt and context already available. Do no "
    "preparatory investigation, planning, decomposition, or implementation, and do not dispatch any other "
    "subagent, before obtaining that review. Ask about intent, constraints, ambiguities, approaches and "
    "alternatives, and early user questions. Clearly trivial mechanical authorized configuration edits, "
    "Git pulls, or basic recompiles may skip this review; if unsure, get the review. Reuse it for ordinary "
    "progress and continuations and delegated subtasks; do not repeat it or apply it recursively. Then read "
    "and follow `{policy}` before deciding whether to delegate.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
)
OLD23_PREVIOUS_AGENTS_GATEWAY = (
    "For coding, repository investigation, debugging, software design, and technical factual research, "
    "before substantive work on each new main task, obtain one initial review from the pinned `astra_initial` "
    "role (`gpt-6-astra` at `ultra`) using only the original prompt and context already available. Do no "
    "preparatory investigation, planning, decomposition, or implementation, and do not dispatch any other "
    "subagent, before obtaining that review. Ask about intent, constraints, ambiguities, approaches and "
    "alternatives, and early user questions. Clearly trivial mechanical authorized configuration edits, "
    "Git pulls, or basic recompiles may skip this review; if unsure, get the review. Reuse it for ordinary "
    "progress and continuations and delegated subtasks; do not repeat it or apply it recursively. Then read "
    "and follow `{policy}` before deciding whether to delegate.\n"
    "Before concluding substantive work as complete, \"done for now\", a partial handoff, "
    "or waiting for user input because useful progress appears exhausted, obtain the mandatory completion review "
    "from `astra_expert` (`gpt-6-astra` at `ultra`) described in the policy. It must examine current evidence, "
    "search existing solutions, brainstorm alternatives and perform relevant external research. Resolve feasible "
    "authorized next steps before concluding. Honor explicit user stops and genuine permission/budget limits; "
    "report unavailable review honestly. This gate is separate from the initial consultation and is not recursive "
    "for delegated subtasks.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
)
# Freeze the published ten-role / twenty-three-file activation independently
# of subsequent native roles and their inventory.
OLD23_AGENTS_GATEWAY = (
    "For coding, repository investigation, debugging, software design, and technical factual research, "
    "before substantive work on each new main task, obtain one initial review from the pinned `astra_initial` "
    "role (`gpt-6-astra` at `ultra`) using only the original prompt and context already available. Do no "
    "preparatory investigation, planning, decomposition, or implementation, and do not dispatch any other "
    "subagent, before obtaining that review. Ask about intent, constraints, ambiguities, approaches and "
    "alternatives, and early user questions. Clearly trivial mechanical authorized configuration edits, "
    "Git pulls, or basic recompiles may skip this review; if unsure, get the review. Reuse it for ordinary "
    "progress and continuations and delegated subtasks; do not repeat it or apply it recursively. Then read "
    "and follow `{policy}` before deciding whether to delegate.\n"
    "Before the main chat decides to stop advancing a substantive user request and return control to the user, "
    "submit its proposed stopping decision to `astra_expert` (`gpt-6-astra` at `ultra`) for the mandatory "
    "completion review described in the policy. Before issuing a final response that ends work, require a current "
    "applicable review and resolve feasible authorized next steps. The trigger is the decision to stop, regardless "
    "of response wording or whether completion is claimed. The review must examine current evidence and available "
    "agent findings, search existing solutions, brainstorm alternatives and perform relevant external research. "
    "Preserve explicit user stops, genuine governing limits, necessary clarification and ongoing tool waits; report "
    "unavailable review honestly. This gate is separate from the initial consultation and is not recursive for "
    "delegated subtasks.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
)
OLD23_ROLES = {
    **OLD21_ROLES,
    "astra_initial": "One-time consultation of the original prompt and available context before substantive work.",
}
OLD23_FILES = OLD22_FILES + ("CLOUD.md",)
OLD24_ROLES = {
    **OLD23_ROLES,
    "sol_researcher": "Scientific authorship, research leadership, and independent scientific critique.",
}
OLD24_FILES = OLD23_FILES + ("agents/sol_researcher.toml",)
ROLES = {name: "Explicit DK assignment or explicit standalone role request only. " + description
         for name, description in OLD24_ROLES.items()}
SKILL_FILES = ("skills/delegation-kit/SKILL.md", "skills/delegation-kit/agents/openai.yaml")
FILES = OLD24_FILES + SKILL_FILES
BEGIN = "# >>> CODEX GLOBAL DELEGATION KIT (managed; do not edit) >>>"
END = "# <<< CODEX GLOBAL DELEGATION KIT <<<"
LEGACY_AGENTS_GATEWAY = (
    "For coding, repository investigation, debugging, software design, and technical factual research tasks, "
    "read and follow `{policy}` before deciding whether to delegate.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
)
OLD21_AGENTS_GATEWAY = (
    "For coding, repository investigation, debugging, software design, and technical factual research, "
    "before substantive work on each new main task, obtain one initial Astra review using only the original "
    "prompt and context already available. Do no preparatory investigation, planning, decomposition, "
    "or implementation, and do not dispatch any other subagent, before obtaining that review. "
    "Ask about intent, constraints, ambiguities, approaches "
    "and alternatives, and early user questions. Clearly trivial mechanical authorized configuration edits, "
    "Git pulls, or basic recompiles may skip this review; if unsure, get the review. Reuse it for ordinary "
    "progress and continuations and delegated subtasks; do not repeat it or apply it recursively. Then read "
    "and follow `{policy}` before deciding whether to delegate.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
)


class Refusal(RuntimeError):
    """A preflight or concurrent-edit check failed."""


@dataclasses.dataclass(frozen=True)
class State:
    data: bytes | None
    mode: int = 0o600

    def __post_init__(self):
        if os.name == "nt":
            # Windows chmod/stat expose a read-only bit, not POSIX permissions.
            object.__setattr__(self, "mode", 0o666 if self.mode & stat.S_IWRITE else 0o444)


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
    if roles in (OLD24_ROLES, OLD23_ROLES):
        gateway = OLD23_AGENTS_GATEWAY.format(policy=target / "policy.md")
    elif roles == OLD21_ROLES:
        gateway = OLD21_AGENTS_GATEWAY.format(policy=target / "policy.md")
    else:
        gateway = LEGACY_AGENTS_GATEWAY.format(policy=target / "policy.md")
    instructions = f"{BEGIN}\n{gateway}{END}\n"
    config = [BEGIN]
    for role, description in roles.items():
        config.extend([
            f"[agents.{role}]",
            f"description = {json.dumps(description)}",
            f"config_file = {json.dumps(str(target / 'agents' / (role + '.toml')))}",
            "",
        ])
    config.extend([END, ""])
    if roles == ROLES:
        return {"config.toml": "\n".join(config)}
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
        if inventory not in (set(LEGACY_FILES), set(ADVISORY_FILES), set(CONTROLLER_FILES),
                             set(ENGINEERING_FILES), set(SWARM_FILES), set(OLD21_FILES),
                             set(OLD22_FILES), set(OLD23_FILES), set(OLD24_FILES), set(FILES)):
            raise ValueError("unexpected bundle file list")
        if inventory == set(LEGACY_FILES):
            known_blocks = blocks(home / "delegation-kit", LEGACY_ROLES)
        elif inventory == set(SWARM_FILES):
            known_blocks = blocks(home / "delegation-kit", PRE_ASTRA_ROLES)
        elif inventory == set(OLD21_FILES):
            known_blocks = blocks(home / "delegation-kit", OLD21_ROLES)
        elif inventory == set(OLD22_FILES):
            known_blocks = blocks(home / "delegation-kit", OLD23_ROLES)
            target = home / "delegation-kit"
            old_gateway = OLD22_AGENTS_GATEWAY.format(policy=target / "policy.md")
            known_blocks["AGENTS.md"] = f"{BEGIN}\n{old_gateway}{END}\n"
        elif inventory == set(OLD23_FILES):
            known_blocks = blocks(home / "delegation-kit", OLD23_ROLES)
        elif inventory == set(OLD24_FILES):
            known_blocks = blocks(home / "delegation-kit", OLD24_ROLES)
        elif inventory == set(FILES):
            known_blocks = expected
        else:
            known_blocks = blocks(home / "delegation-kit", PRE_SWARM_ROLES)
        if set(value["activation"]) != set(known_blocks):
            raise ValueError("unexpected activation file list")
        for name, block in known_blocks.items():
            record = value["activation"][name]
            allowed = (block, "\n" + block)
            if inventory == set(OLD21_FILES) and name == "AGENTS.md":
                legacy = blocks(home / "delegation-kit", PRE_ASTRA_ROLES)[name]
                allowed += (legacy, "\n" + legacy)
            if inventory == set(OLD23_FILES) and name == "AGENTS.md":
                target = home / "delegation-kit"
                old_gateway = OLD22_AGENTS_GATEWAY.format(policy=target / "policy.md")
                old_block = f"{BEGIN}\n{old_gateway}{END}\n"
                previous_gateway = OLD23_PREVIOUS_AGENTS_GATEWAY.format(policy=target / "policy.md")
                previous_block = f"{BEGIN}\n{previous_gateway}{END}\n"
                allowed += (old_block, "\n" + old_block,
                            previous_block, "\n" + previous_block)
            if record["inserted"] not in allowed:
                raise ValueError("unexpected managed block")
            if type(record["original_exists"]) is not bool:
                raise ValueError("invalid original file state")
        return state, value
    except (ValueError, TypeError, KeyError) as error:
        raise Refusal(f"Invalid installation manifest {path}: {error}") from error


def _plan_runtime(home: Path, source: Path, uninstall: bool = False) -> list[Change]:
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
    manifest_path = target / ".installation" / "manifest.json"
    manifest_state, previous = load_manifest(manifest_path, home, expected)
    if target.exists() and previous is None and any(target.iterdir()):
        raise Refusal(f"Existing nonempty destination has no installation manifest: {target}")
    if uninstall and previous is None:
        raise Refusal(f"No owned installation found at {target}")

    # AGENTS.md is read only to remove a recognized legacy gateway or refuse
    # unowned markers. Fresh installations never add instructions to this file.
    globals_before = {name: read_state(home / name) for name in ("AGENTS.md", "config.toml")}
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
    changes: list[Change] = []
    activation = {}
    if not uninstall:
        # Disable removes only the prior owned block; new role names may belong
        # to the user in an older installation and must remain untouched.
        for role in ROLES:
            if role in clean_configuration.get("agents", {}):
                raise Refusal(f"Existing agent role conflicts with the kit: {role}")
        check_personal_roles(home)
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
                raise Refusal(f"Existing bundle file is not owned by the prior installation: {target / name}")
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
                # Replace the exact owned block at its original position, retaining
                # user text around it for both activation files.
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
        if previous and previous["active"] and "AGENTS.md" in previous["activation"]:
            before = globals_before["AGENTS.md"]
            text = globals_clean["AGENTS.md"]
            remove = not text and not previous["activation"]["AGENTS.md"]["original_exists"]
            after = State(None) if remove else State(text.encode(), before.mode)
            if before != after:
                changes.append(Change(home / "AGENTS.md", before, after))
        parse_toml(next((change.after.data for change in changes if change.path == home / "config.toml"), globals_before["config.toml"].data), home / "config.toml")
    else:
        bundle_digests = previous["bundle_digests"]
        if previous["active"]:
            for name in previous["activation"]:
                text = globals_clean[name]
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
        if before.data is not None and any(c.path == home / name for c in changes):
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


def _members(root: Path, repositories: list[str]) -> list[Path]:
    """Explicit tree members avoid scanning or changing unrelated nested repos."""
    members = [root]
    for name in repositories:
        relative = Path(name)
        if relative.drive or relative.root or ".." in relative.parts or relative == Path("."):
            raise Refusal("--repo must be a child repository path relative to --tree")
        member = root / relative
        safe_path(member)
        if not member.is_relative_to(root):
            raise Refusal("Tree member escapes the collection root")
        if not member.is_dir() or not (member / ".git").exists():
            raise Refusal(f"Tree member is not an existing Git repository: {member}")
        if member not in members:
            members.append(member)
    return members


def _discovery_files(home: Path, source: Path, scope: str, members: list[Path]) -> dict[Path, bytes]:
    target = home / "delegation-kit"
    result = {}
    for member in members:
        skill = (home / "skills" if scope == "global" else member / ".agents" / "skills") / "delegation-kit"
        result[skill / "SKILL.md"] = read_state(source / SKILL_FILES[0]).data
        result[skill / "agents/openai.yaml"] = read_state(source / SKILL_FILES[1]).data
        result[skill / "runtime.json"] = (json.dumps({"runtime_directory": str(target)}, indent=2) + "\n").encode()
        if scope == "tree" and member != members[0]:
            result[member / ".codex/config.toml"] = blocks(target)["config.toml"].encode()
    return result


def plan(home: Path, source: Path, uninstall: bool = False, *, scope: str = "global",
         root: Path | None = None, repositories: list[str] | None = None) -> list[Change]:
    """One atomic plan for runtime, registrations, and owned skill entry points."""
    if scope not in {"global", "project", "tree"}:
        raise Refusal("Unknown installation scope")
    home, source = home.absolute(), source.absolute()
    root = home if scope == "global" else (root or home.parent).absolute()
    safe_path(root)
    manifest_path = home / "delegation-kit/.installation/manifest.json"
    # Validate legacy activation before using any paths from its manifest.
    manifest_before, previous = load_manifest(manifest_path, home, blocks(home / "delegation-kit"))
    if scope != "global" and home != root / ".codex":
        raise Refusal("Project and tree homes must be the root's .codex directory")
    if previous and previous.get("scope", "global") != scope:
        raise Refusal("Installation scope differs; use its original --home, --project, or --tree option")
    prior_members = previous.get("members", [str(root)]) if previous else [str(root)]
    if (not isinstance(prior_members, list) or not prior_members or prior_members[0] != str(root)
            or any(not isinstance(p, str) or not Path(p).is_absolute()
                   or ".." in Path(p).parts or not Path(p).is_relative_to(root) for p in prior_members)
            or (scope != "tree" and prior_members != [str(root)])
            or len(set(prior_members)) != len(prior_members)):
        raise Refusal("Invalid installation member paths")
    for member in prior_members:
        safe_path(Path(member))
    members = [Path(p) for p in prior_members] if uninstall else (
        _members(root, repositories or []) if scope == "tree" else [root])
    if scope == "tree" and not uninstall and len(members) == 1:
        raise Refusal("A tree installation needs at least one explicit --repo child path")
    old_files = previous.get("discovery", {}) if previous else {}
    if not isinstance(old_files, dict):
        raise Refusal("Invalid skill ownership records")
    old_expected = _discovery_files(home, source, scope, [Path(p) for p in prior_members])
    if old_files and set(old_files) != {str(p) for p in old_expected}:
        raise Refusal("Unexpected skill or tree activation paths")
    if previous and set(previous["bundle_digests"]) == set(FILES) and not old_files:
        raise Refusal("Current installation is missing skill ownership records")
    for name, record in old_files.items():
        path = Path(name)
        if not isinstance(record, dict) or type(record.get("original_exists")) is not bool:
            raise Refusal("Invalid skill ownership record")
        if path.name == "config.toml":
            block = old_expected[path].decode()
            if record.get("inserted") not in (block, "\n" + block):
                raise Refusal("Unexpected tree role activation block")
        elif (record.get("original_exists") or not isinstance(record.get("digest"), str)
              or len(record["digest"]) != 64):
            raise Refusal("Invalid owned skill digest")
    changes = _plan_runtime(home, source, uninstall)
    manifest_change = next((c for c in changes if c.path == manifest_path), None)
    manifest = json.loads(manifest_change.after.data) if manifest_change else previous
    desired = {} if uninstall else _discovery_files(home, source, scope, members)
    discovery = {}
    for path in sorted({Path(p) for p in old_files} | set(desired)):
        before = read_state(path)
        record = old_files.get(str(path))
        owned = previous and previous["active"] and record is not None
        if not owned and path not in desired:
            continue
        if path.name == "config.toml":
            text = decode(before.data, path)
            clean = strip_block(text, record["inserted"] if owned else None, path)
            if path in desired:
                config = parse_toml(clean.encode(), path)
                if not isinstance(config.get("agents", {}), dict):
                    raise Refusal(f"config.toml agents must be a table: {path}")
                if set(config.get("agents", {})) & set(ROLES):
                    raise Refusal(f"Existing agent role conflicts with DK in {path}")
                check_personal_roles(path.parent)
                block = desired[path].decode()
                inserted = record["inserted"] if owned else (("\n" if clean and not clean.endswith("\n") else "") + block)
                original = record["original_exists"] if owned else before.data is not None
                data = text.replace(record["inserted"], inserted, 1) if owned else clean + inserted
                after = State(data.encode(), before.mode if before.data is not None else 0o600)
                discovery[str(path)] = {"inserted": inserted, "original_exists": original}
                parse_toml(after.data, path)
            else:
                after = State(None) if not clean and not record["original_exists"] else State(clean.encode(), before.mode)
        else:
            if (path.name == "SKILL.md" and not record and path.parent.exists()
                    and any(path.parent.iterdir())):
                raise Refusal(f"Existing skill directory is not owned: {path.parent}")
            if owned and (before.data is None or digest(before.data) != record["digest"]):
                raise Refusal(f"Installed skill has local edits or is missing: {path}")
            if not owned and before.data is not None:
                raise Refusal(f"Skill destination is not owned by this installation: {path}")
            after = State(desired[path], before.mode if before.data is not None else 0o644) if path in desired else State(None)
            if path in desired:
                if after.data is None:
                    raise Refusal(f"Required source skill is missing: {path}")
                discovery[str(path)] = {"digest": digest(after.data), "original_exists": False}
        if before != after:
            changes.append(Change(path, before, after))
    # Disabled discovery files are intentionally absent, but keep their ownership
    # descriptions for validation, idempotent disable, and later reactivation.
    if uninstall:
        discovery = old_files
        if not changes:
            return []
    if manifest is None:
        raise Refusal("No installation manifest")
    manifest.update(scope=scope, members=[str(p) for p in members], discovery=discovery)
    after_manifest = State((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
                           manifest_before.mode if manifest_before.data is not None else 0o600)
    changes = [c for c in changes if c.path != manifest_path]
    if changes or manifest_before != after_manifest:
        changes.append(Change(manifest_path, manifest_before, after_manifest))
    return changes


def _stage(path: Path, state: State) -> Path:
    descriptor, filename = tempfile.mkstemp(prefix=".delegation-kit-", dir=path.parent)
    staged = Path(filename)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            if hasattr(os, "fchmod"):
                os.fchmod(stream.fileno(), state.mode)
            else:
                os.chmod(staged, state.mode)
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
    if hasattr(sys.stdout, "reconfigure"):
        # A legacy Windows console must not prevent installing UTF-8 documents.
        sys.stdout.reconfigure(errors="backslashreplace")
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


def _uninstall_location(home: Path) -> tuple[Path, str, Path, dict]:
    home = home.absolute()
    path = home / "delegation-kit/.installation/manifest.json"
    _, manifest = load_manifest(path, home, blocks(home / "delegation-kit"))
    if manifest is None:
        raise Refusal(f"No owned installation found at {home / 'delegation-kit'}")
    scope = manifest.get("scope", "global")
    if not isinstance(scope, str) or scope not in {"global", "project", "tree"}:
        raise Refusal(f"Invalid installation scope in {path}")
    return home, scope, home if scope == "global" else home.parent, manifest


def discover_uninstall(cwd: Path, script_directory: Path, default_home: Path) -> tuple[Path, str, Path]:
    """Use this deployment, then nearest local ownership, then the Codex home.

    Stop at the nearest Git root after checking its own entry points. Invalid
    local ownership never falls back to a different installation, and retained
    disabled manifests remain targets within that boundary.
    """
    script_directory = script_directory.absolute()
    metadata = script_directory / ".installation"
    if (metadata.exists() or metadata.is_symlink()
            or (script_directory.name == "delegation-kit" and not (script_directory / ".git").exists())):
        if script_directory.name != "delegation-kit":
            raise Refusal(f"Unexpected installed runtime directory: {script_directory}")
        return _uninstall_location(script_directory.parent)[:3]
    cwd = cwd.absolute()
    for member in (cwd, *cwd.parents):
        skill = member / ".agents/skills/delegation-kit"
        pointer = skill / "runtime.json"
        state = read_state(pointer)
        if state.data is not None:
            try:
                value = json.loads(decode(state.data, pointer))
                runtime = Path(value["runtime_directory"])
                if (not runtime.is_absolute() or ".." in runtime.parts or "\0" in str(runtime)
                        or runtime.name != "delegation-kit"):
                    raise ValueError("invalid runtime directory")
            except (ValueError, TypeError, KeyError) as error:
                raise Refusal(f"Invalid runtime pointer {pointer}: {error}") from error
            home, scope, root, manifest = _uninstall_location(runtime.parent)
            records = manifest.get("discovery", {})
            members = manifest.get("members", [])
            record = records.get(str(pointer), {}) if isinstance(records, dict) else {}
            if (scope == "global" or not member.is_relative_to(root)
                    or not isinstance(members, list) or str(member) not in members
                    or not isinstance(record, dict) or record.get("digest") != digest(state.data)):
                raise Refusal(f"Runtime pointer is not owned by this installation: {pointer}")
            return home, scope, root
        if read_state(skill / "SKILL.md").data is not None:
            raise Refusal(f"Installed skill is missing its runtime pointer: {pointer}")
        home = member / ".codex"
        target = home / "delegation-kit"
        if target.exists() or target.is_symlink():
            location = _uninstall_location(home)
            if location[1] != "global":
                return location[:3]
        marker = member / ".git"
        if marker.exists() or marker.is_symlink():
            raise Refusal(f"No owned DK installation found within repository boundary {member}; "
                          "refusing ancestor or global discovery. Use the installed uninstaller "
                          "or select an explicit target.")
    return _uninstall_location(default_home)[:3]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--home", type=Path, help="Global Codex home (default: CODEX_HOME or ~/.codex)")
    scope.add_argument("--project", type=Path, help="Install only in this repository or working folder")
    scope.add_argument("--tree", type=Path, help="Non-Git collection root; explicitly list its child repositories")
    parser.add_argument("--repo", action="append", default=[], help="Child Git repository relative to --tree; repeat for each member")
    parser.add_argument("--source", type=Path, default=Path(__file__).absolute().parent, help="source bundle directory")
    parser.add_argument("--apply", action="store_true", help="apply the previewed installation or disable operation")
    parser.add_argument("--uninstall", action="store_true", help="auto-discover scope unless selected; remove owned discovery, retain bundle and evidence")
    args = parser.parse_args(argv)
    if args.repo and not args.tree:
        parser.error("--repo requires --tree")
    try:
        default_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
        if args.uninstall and not any((args.home, args.project, args.tree)):
            home, installation_scope, root = discover_uninstall(Path.cwd(), Path(__file__).absolute().parent, default_home)
            print(f"Discovered {installation_scope} installation at {home / 'delegation-kit'}")
        else:
            root = args.project or args.tree
            installation_scope = "tree" if args.tree else "project" if args.project else "global"
            home = root.expanduser().absolute() / ".codex" if root else (args.home or default_home).expanduser()
        changes = plan(home, args.source.expanduser(), args.uninstall, scope=installation_scope,
                       root=root.expanduser().absolute() if root else None, repositories=args.repo)
        preview(changes)
        if not changes:
            print("No changes needed.")
        elif args.apply:
            apply(changes)
            print("Kit disabled; bundle and evidence retained." if args.uninstall else
                  f"Delegation kit installed for {installation_scope} scope; explicit skill invocation required.")
        else:
            print("Dry run only. Add --apply to make these changes.")
        return 0
    except (Refusal, OSError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
