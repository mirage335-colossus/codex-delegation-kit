#!/usr/bin/env python3
"""Sanitize historical verification material and seal a public byte inventory.

The sanitizer publishes a deterministic representation of the historical
evidence. It does not claim that transformed excerpts are exact checkout bytes.
The manifest records SHA-256 values for the current, post-sanitization bytes;
it provides integrity checking, not authenticity or timing proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
import re
import sys


UUID_RE = re.compile(
    r"(?<![0-9a-fA-F])[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?![0-9a-fA-F])"
)
WEB_REF_RE = re.compile(r"\bturn\d+(?:search|view|fetch|open|click|find)\d+\b")
POSIX_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./@-])/(?!/)(?:[^\s\"'<>|]+)")
WINDOWS_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:[A-Za-z]:\\(?:[^\s\"'<>|]+))")
PROJECT_NAMES = {"codex-delegation-kit", "pumpModem", "software-foundation"}
REPOSITORY_RECIPES = (
    "tools/publish_verification.py",
    "examples/verification_replay.py",
    "examples/recompute_verification_usage.py",
    "tests/test_verification_publication.py",
    "tests/test_verification_replay.py",
    "tests/test_verification_usage.py",
)


def _trim_path(value: str) -> tuple[str, str]:
    suffix = ""
    while value and value[-1] in ".,;:!?)]}":
        suffix = value[-1] + suffix
        value = value[:-1]
    return value, suffix


def _portable_path(raw: str) -> str:
    path, punctuation = _trim_path(raw)
    normalized = path.replace("\\", "/") if re.match(r"^[A-Za-z]:\\", path) else path
    if ":" in normalized and normalized.startswith("/"):
        # Captured PATH values contain several roots in a single token.
        return ":".join(_portable_path(part) for part in normalized.split(":")) + punctuation
    for index, part in enumerate(normalized.split("/")):
        if part in PROJECT_NAMES:
            rel = "/".join(normalized.split("/")[index + 1:])
            if part == "codex-delegation-kit":
                return (rel or "repository root") + punctuation
            return part + ("/" + rel if rel else "") + punctuation
    # Private home/install paths become logical labels without usernames.
    m = re.match(r"^/(?:home|Users)/[^/]+(?:/\.codex)?(?:/(.*))?$", normalized)
    if m:
        tail = m.group(1) or ""
        kind = "unbundled-installation" if "/.codex" in normalized else "unbundled-home"
        if kind == "unbundled-installation":
            tail = re.sub(r"^[^/]+/", "", tail)
        return kind + ("/" + tail if tail else "") + punctuation
    m = re.match(r"^/(?:tmp|var/tmp|private/var/folders)/(.+)$", normalized)
    if m:
        _, _, tail = m.group(1).partition("/")
        runtime_root = normalized[:len(normalized) - len(tail) - 1] if tail else normalized
        alias = hashlib.sha256(runtime_root.encode()).hexdigest()[:16]
        return "unbundled-runtime/run-h" + alias + ("/" + tail if tail else "") + punctuation
    if re.match(r"^[A-Za-z]:/", normalized):
        parts = normalized[3:].split("/")
        if len(parts) > 0 and parts[0].lower() in {"users", "user"}:
            parts = parts[2:]
        return "unbundled-runtime/" + "/".join(parts) + punctuation
    # Standard system paths are fixture labels, not dependencies.
    system_roots = ("/dev", "/usr", "/bin", "/sbin", "/opt", "/etc", "/Library")
    if any(normalized == base or normalized.startswith(base + "/") for base in system_roots):
        return "system-fixture/" + normalized.lstrip("/") + punctuation
    return raw


def _sanitize_text(text: str, aliases: dict[str, str]) -> str:
    # Process complete tokens, never a root substring before its suffix.
    text = POSIX_PATH_RE.sub(lambda m: _portable_path(m.group(0)), text)
    text = WINDOWS_PATH_RE.sub(lambda m: _portable_path(m.group(0)), text)
    # Earlier published bundles used this non-relative prefix. Drop it only
    # when it starts a path token; URL path segments are left intact.
    text = re.sub(r"(?<![A-Za-z0-9_./-])repo/(?=[A-Za-z0-9_.-])", "", text)
    def alias(value: str, prefix: str) -> str:
        key = value.lower()
        result = prefix + "-h" + hashlib.sha256(key.encode()).hexdigest()[:16]
        if result in aliases.values() and aliases.get(key) != result:
            raise ValueError("publication alias collision")
        return aliases.setdefault(key, result)
    text = WEB_REF_RE.sub(lambda m: alias(m.group(0), "study-source"), text)
    text = UUID_RE.sub(lambda m: alias(m.group(0), "study-id"), text)
    return text


def _remove_private_logs(obj: object) -> bool:
    changed = False
    if isinstance(obj, dict):
        for key in list(obj):
            if key in {"source_log", "root_log"}:
                obj[key] = "reported-source (unbundled private log; not included)"
                changed = True
            else:
                changed = _remove_private_logs(obj[key]) or changed
    elif isinstance(obj, list):
        for item in obj:
            changed = _remove_private_logs(item) or changed
    return changed


def _sanitize_json_strings(obj: object, aliases: dict[str, str]) -> object:
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            new_key = _sanitize_text(key, aliases)
            if new_key in result:
                raise ValueError("publication transform would merge distinct JSON keys")
            result[new_key] = _sanitize_json_strings(value, aliases)
        return result
    if isinstance(obj, list):
        return [_sanitize_json_strings(value, aliases) for value in obj]
    if isinstance(obj, str):
        return _sanitize_text(obj, aliases)
    return obj


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in source; refusing lossy publication")
        result[key] = value
    return result


def _historical_evidence_root(path: Path, data: object) -> bool:
    name = path.name.lower()
    if not isinstance(data, dict):
        return False
    if name in {"publication-manifest.json", "reproduction.json"} or str(
        data.get("publication_scope", "")
    ).startswith("post_sanitization"):
        return False
    if "installation" in name or any(x in name for x in ("freeze", "lock", "hash", "digest", "validation")):
        return True
    # Add scope only to roots that actually carry recorded integrity metadata.
    stack = [data]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            if any(k.lower() in {"sha256", "sha_256", "digest", "byte_size", "size_bytes", "source_hash", "artifact_hash"} for k in value):
                return True
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
        elif isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value):
            return True
    return False


def sanitize(root: Path) -> int:
    root = root.resolve()
    aliases: dict[str, str] = {}
    changed_files = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() not in {".md", ".json", ".txt", ".py", ".diff", ".toml"}:
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        parsed = None
        metadata_changed = False
        if path.suffix.lower() == ".json":
            try:
                parsed = json.loads(text, object_pairs_hook=_unique_object)
            except json.JSONDecodeError:
                # Preserve intentionally invalid pilot artifacts and their failure.
                parsed = None
            if parsed is not None:
                metadata_changed = _remove_private_logs(parsed)
                if _historical_evidence_root(path, parsed):
                    parsed["publication_scope"] = "historical_pre_publication"
                    parsed["publication_note"] = (
                        "Recorded hashes, byte sizes, and outcomes are historical claims; "
                        "they do not validate these rewritten public artifacts."
                    )
                    metadata_changed = True
                transformed = _sanitize_json_strings(parsed, aliases)
                if metadata_changed or transformed != parsed:
                    text = json.dumps(transformed, ensure_ascii=False, indent=2) + "\n"
            else:
                text = _sanitize_text(text, aliases)
        else:
            text = _sanitize_text(text, aliases)
        if text != original:
            mode = stat.S_IMODE(path.stat().st_mode)
            try:
                if not mode & stat.S_IWUSR:
                    path.chmod(mode | stat.S_IWUSR)
                path.write_text(text, encoding="utf-8", newline="")
            finally:
                path.chmod(mode)
            changed_files += 1
    return changed_files


def inventory(root: Path, manifest_rel: str) -> dict[str, str]:
    root = root.resolve(strict=True)
    manifest = _safe_relative(manifest_rel)
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in publication inventory: {path.relative_to(root)}")
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        _safe_relative(rel)
        if rel == manifest:
            continue
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _repository_root(root: Path) -> Path:
    return root.resolve(strict=True).parent


def _checked_recipe_path(repo: Path, rel: str) -> Path:
    safe = _safe_relative(rel)
    if safe not in REPOSITORY_RECIPES:
        raise ValueError(f"repository recipe path is not allowlisted: {safe}")
    path = repo / safe
    cursor = repo
    for part in PurePosixPath(safe).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"repository recipe path crosses symlink: {safe}")
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(repo.resolve(strict=True)) or not resolved.is_file():
        raise ValueError(f"repository recipe path escapes or is not a file: {safe}")
    return resolved


def _recipe_inventory(root: Path) -> dict[str, str]:
    """Hash the fixed public recipe allowlist when running in the source repo."""
    repo = _repository_root(root)
    present = [repo / rel for rel in REPOSITORY_RECIPES if (repo / rel).exists()]
    if not present:
        return {}
    if len(present) != len(REPOSITORY_RECIPES):
        missing = sorted(rel for rel in REPOSITORY_RECIPES if not (repo / rel).is_file())
        raise ValueError(f"required repository recipes are missing: {missing}")
    result: dict[str, str] = {}
    for rel in REPOSITORY_RECIPES:
        safe = _safe_relative(rel)
        path = _checked_recipe_path(repo, safe)
        result[safe] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _safe_relative(value: str) -> str:
    if "\\" in value:
        raise ValueError(f"manifest path must use POSIX separators: {value!r}")
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"unsafe publication path: {value!r}")
    return p.as_posix()


def seal(root: Path, manifest_rel: str = "publication-manifest.json") -> None:
    manifest_rel = _safe_relative(manifest_rel)
    payload = {
        "schema_version": 1,
        "scope": "post_sanitization_current_verification_and_repository_recipe_bytes; integrity only, not authenticity or timing",
        "excluded": [manifest_rel],
        "files": inventory(root, manifest_rel),
        "repository_recipes": _recipe_inventory(root),
    }
    target = root.resolve() / manifest_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify(root: Path, manifest_rel: str = "publication-manifest.json") -> dict[str, int]:
    manifest_rel = _safe_relative(manifest_rel)
    root = root.resolve(strict=True)
    target = root / manifest_rel
    if target.is_symlink() or not target.is_file():
        raise ValueError("publication manifest is missing or is a symlink")
    data = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("excluded") != [manifest_rel]:
        raise ValueError("unsupported publication manifest scope/schema")
    expected = data.get("files")
    if not isinstance(expected, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v) for k, v in expected.items()):
        raise ValueError("malformed publication inventory")
    for rel in expected:
        _safe_relative(rel)
    actual = inventory(root, manifest_rel)
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = sorted(k for k in set(actual) & set(expected) if actual[k] != expected[k])
    if missing or added or changed:
        raise ValueError(f"publication inventory mismatch: missing={missing}, unexpected={added}, mutated={changed}")
    expected_recipes = data.get("repository_recipes", {})
    if not isinstance(expected_recipes, dict) or any(
        not isinstance(k, str) or k not in REPOSITORY_RECIPES
        or not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
        for k, v in expected_recipes.items()
    ):
        raise ValueError("malformed or non-allowlisted repository recipe inventory")
    repo = _repository_root(root)
    present = [repo / rel for rel in REPOSITORY_RECIPES if (repo / rel).exists()]
    if present and set(expected_recipes) != set(REPOSITORY_RECIPES):
        raise ValueError("repository recipe inventory must include the complete fixed allowlist")
    recipe_actual: dict[str, str] = {}
    for rel in expected_recipes:
        safe = _safe_relative(rel)
        path = _checked_recipe_path(repo, safe)
        recipe_actual[safe] = hashlib.sha256(path.read_bytes()).hexdigest()
    recipe_changed = sorted(k for k in expected_recipes if recipe_actual[k] != expected_recipes[k])
    if recipe_changed:
        raise ValueError(f"repository recipe mutation: {recipe_changed}")
    return {"files": len(actual), "repository_recipes": len(recipe_actual)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("sanitize", "seal", "verify", "check"), help="operation")
    p.add_argument("--root", type=Path, required=True, help="verification directory")
    p.add_argument("--manifest", default="publication-manifest.json", help="manifest path relative to root")
    args = p.parse_args(argv)
    try:
        if args.action == "sanitize":
            print(f"sanitized files: {sanitize(args.root)}")
        elif args.action == "seal":
            seal(args.root, args.manifest)
            print(f"sealed {args.manifest}")
        else:
            summary = verify(args.root, args.manifest)
            print(f"publication inventory verified: {summary['files']} files")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"publication check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
