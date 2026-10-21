"""Bounded repository snapshots for engineering attempts, not an OS sandbox.

Git-visible files and explicit file/directory audit scopes are captured.
Ignored artifacts outside those scopes and Git metadata are not fully audited.
Callers own persistence, scheduling, and decisions about incomplete evidence.
"""
from __future__ import annotations

import difflib
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile

MAX_FILES = 20000
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_TEXT_BYTES = 128 * 1024
MAX_CONTENT_BYTES = 2 * 1024 * 1024
MAX_PATCH_BYTES = 2 * 1024 * 1024


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _relative(value):
    if not isinstance(value, str) or not value or "\0" in value or "\\" in value:
        raise ValueError("scope/path must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) == "." or ".git" in path.parts:
        raise ValueError("scope/path escapes the repository or includes Git metadata")
    return path.as_posix()


def _root(cwd):
    root = Path(cwd).absolute()
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise ValueError("repository root must not traverse symlinks")
    root = root.resolve()
    if not root.is_dir() or not (root / ".git").is_dir() or (root / ".git").is_symlink():
        raise ValueError("engineering requires a standalone Git repository root; linked worktrees are unsupported")
    return root


def validate_scope(cwd, scope):
    """Normalize owned files/directories; existing symlink paths are refused.

    A trailing slash declares a directory that does not yet exist. Existing
    directories gain the slash automatically. Owning a directory owns its
    subtree, never a similarly prefixed sibling. The repository root and .git
    cannot be owned through this interface.
    """
    root = _root(cwd)
    if not isinstance(scope, (list, tuple)):
        raise ValueError("write_scope must be a list of relative files/directories")
    result = set()
    for value in scope:
        name = _relative(value)
        path = root
        for part in PurePosixPath(name).parts:
            path = path / part
            if path.is_symlink():
                raise ValueError("write_scope must not traverse or name a symlink")
        if value.endswith("/") or path.is_dir():
            name += "/"
        result.add(name)
    return sorted(result)


def owns(path, scope):
    """Test normalized relative file/directory scope without filesystem reads."""
    name = _relative(path)
    return any(name == item.rstrip("/") or (item.endswith("/") and name.startswith(item))
               for item in scope)


def _git(root, *args, optional=False, input=None):
    # Do not let an inherited GIT_DIR/WORK_TREE point this read at another repo.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
             "-C", str(root), *args], capture_output=True, timeout=5, env=env, input=input)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"repository inspection could not complete: {error}") from error
    if optional and result.returncode == 1:
        return None
    if result.returncode:
        raise ValueError("repository inspection failed: " + result.stderr.decode("utf-8", "replace")[:2000])
    if len(result.stdout) > 8 * 1024 * 1024:
        raise ValueError("repository file inventory exceeds 8 MiB")
    return result.stdout


def _read_entry(root_fd, name):
    """Open each parent with O_NOFOLLOW; never read through a replaced symlink."""
    parts = PurePosixPath(name).parts
    parent = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            except FileNotFoundError:
                return None, None, None
            os.close(parent)
            parent = child
        try:
            info = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return None, None, None
        if stat.S_ISLNK(info.st_mode):
            raise ValueError(f"symlink repository entries are unsupported: {name}")
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"unsupported repository entry (submodule/nested repository or special file): {name}")
        if info.st_size > MAX_FILE_BYTES:
            raise ValueError(f"repository file exceeds {MAX_FILE_BYTES} bytes: {name}")
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            data = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        signature = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if len(data) > MAX_FILE_BYTES or signature(info) != signature(before) or signature(before) != signature(after):
            raise ValueError(f"repository file changed while capturing evidence: {name}")
        return _hash(data), stat.S_IMODE(info.st_mode), data
    except OSError as error:
        raise ValueError(f"cannot safely inspect repository entry {name}: {error}") from error
    finally:
        os.close(parent)


def _inventory(root, scope, root_fd):
    """Include ignored descendants of explicit audit directories, without links."""
    names = {_relative(name.decode("utf-8")) for name in
             _git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if name}
    names.update(name for name in scope if not name.endswith("/"))
    entries = 0

    def visit(descriptor, prefix, depth=0):
        nonlocal entries
        if depth > 128:
            raise ValueError("explicit audit directory nesting exceeds 128 levels")
        with os.scandir(descriptor) as children:
            for entry in children:
                name = _relative(prefix + entry.name)
                entries += 1
                if entries > MAX_FILES:
                    raise ValueError(f"explicit audit directories exceed {MAX_FILES} entries")
                info = os.stat(entry.name, dir_fd=descriptor, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                    try:
                        visit(child, name + "/", depth + 1)
                    finally:
                        os.close(child)
                elif stat.S_ISREG(info.st_mode):
                    names.add(name)
                    if len(names) > MAX_FILES:
                        raise ValueError(f"repository exceeds {MAX_FILES} audited files")
                else:
                    raise ValueError(f"explicit audit scope contains symlink or special entry: {name}")

    previous = []
    for directory in sorted(name for name in scope if name.endswith("/")):
        if any(directory.startswith(parent) for parent in previous):
            continue
        previous.append(directory)
        descriptor = os.dup(root_fd)
        try:
            missing = False
            for part in PurePosixPath(directory).parts:
                try:
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                except FileNotFoundError:
                    missing = True
                    break  # A declared scratch directory may not exist yet.
                os.close(descriptor)
                descriptor = child
            if not missing:
                visit(descriptor, directory)
        except OSError as error:
            raise ValueError(f"cannot safely inventory explicit audit scope {directory}: {error}") from error
        finally:
            os.close(descriptor)
    if len(names) > MAX_FILES:
        raise ValueError(f"repository exceeds {MAX_FILES} audited files")
    return names


def snapshot(cwd, write_scope=()):
    """Capture current bytes, including dirty files, without changing the repo.

    Hashes cover up to 20,000 files, 8 MiB per file and 128 MiB total. Text
    retained for audited paths is capped independently; omissions remain explicit.
    The second argument is an audit scope, not permission to write. Reviewers
    must retain the producer's scope to bind ignored wrappers and build outputs.
    Explicit directory walks also cap their file/directory entries at 20,000.
    A snapshot is not atomic against external writers. Controller ownership must
    exclude competing writes during capture and checks.
    """
    root = _root(cwd)
    scope = validate_scope(root, write_scope)
    actual_root = Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if actual_root != root:
        raise ValueError("cwd must be the actual Git repository root")
    revision = _git(root, "rev-parse", "--verify", "--quiet", "HEAD", optional=True)
    files, modes, contents, omitted = {}, {}, {}, {}
    total_bytes = content_bytes = 0
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        names = _inventory(root, scope, root_fd)
        for name in sorted(names):
            identity, mode, data = _read_entry(root_fd, name)
            files[name], modes[name] = identity, mode
            total_bytes += len(data) if data is not None else 0
            if total_bytes > MAX_TOTAL_BYTES:
                raise ValueError(f"repository exceeds {MAX_TOTAL_BYTES} audited bytes")
            if data is None or not owns(name, scope):
                continue
            if len(data) > MAX_TEXT_BYTES or content_bytes + len(data) > MAX_CONTENT_BYTES:
                omitted[name] = "owned text capture limit"
                continue
            try:
                contents[name] = data.decode("utf-8")
                content_bytes += len(data)
            except UnicodeDecodeError:
                omitted[name] = "non-UTF-8 content"
    finally:
        os.close(root_fd)
    result = {"root": str(root), "revision": revision.decode().strip() if revision else None,
              "files": files, "modes": modes, "contents": contents, "content_omissions": omitted}
    # An explicitly scoped absent new file remains visible in files as None,
    # but must not make a read-only snapshot of these same bytes a new identity.
    identity = {"revision": result["revision"],
                "files": {name: value for name, value in files.items() if value is not None},
                "modes": {name: value for name, value in modes.items() if value is not None}}
    result["digest"] = _hash(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode())
    return result


def copy_repository(source, destination, write_scope=()):
    """Prepare an independent, uncommitted private repository from current bytes.

    Source metadata and undeclared ignored caches are never copied. Every file has
    an independent inode; Git's fresh index makes originally tracked ignored
    files visible without invoking clean filters. The source must remain stable
    through both snapshots. Publication uses Linux no-replace rename so an
    existing destination can never be replaced, even after the initial check.
    """
    before = snapshot(source, write_scope)
    root = Path(before["root"])
    target = Path(destination).absolute()
    if any(path.is_symlink() for path in (target, *target.parents)):
        raise ValueError("private repository destination must not traverse symlinks")
    target = target.resolve()
    if target.is_relative_to(root) or root.is_relative_to(target):
        raise ValueError("private repository destination must be outside and not contain the source")
    if target.exists():
        raise ValueError("private repository destination already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    if any(path.is_symlink() for path in (target.parent, *target.parent.parents)):
        raise ValueError("private repository destination parent changed to a symlink")
    stage = Path(tempfile.mkdtemp(prefix=".engineering-copy-", dir=target.parent))
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        names = []
        for name, expected in before["files"].items():
            identity, mode, data = _read_entry(root_fd, name)
            if identity != expected or mode != before["modes"][name]:
                raise ValueError(f"source changed while copying private repository: {name}")
            if data is None:
                continue
            copied = stage / name
            copied.parent.mkdir(parents=True, exist_ok=True)
            with copied.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                os.fchmod(stream.fileno(), mode)
            names.append(name)
        _git(stage, "init", "--quiet", "--template=")
        for start in range(0, len(names), 64):
            batch = names[start:start + 64]
            object_ids = _git(stage, "hash-object", "--no-filters", "-w", "--", *batch).splitlines()
            if len(object_ids) != len(batch):
                raise ValueError("private repository object creation returned an incomplete inventory")
            records = b"".join((b"100755" if before["modes"][name] & 0o111 else b"100644")
                               + b" " + object_id + b"\t" + name.encode("utf-8") + b"\0"
                               for name, object_id in zip(batch, object_ids))
            _git(stage, "update-index", "-z", "--index-info", input=records)
        copied = snapshot(stage, write_scope)
        existing = lambda values: {name: value for name, value in values.items() if value is not None}
        if existing(copied["files"]) != existing(before["files"]) or existing(copied["modes"]) != existing(before["modes"]):
            raise ValueError("private repository does not match the captured source bytes and modes")
        after = snapshot(root, write_scope)
        if after["digest"] != before["digest"]:
            raise ValueError("source changed while preparing private repository")
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise ValueError("atomic no-replace private repository publication requires Linux renameat2")
        if rename(-100, os.fsencode(stage), -100, os.fsencode(target), 1) != 0:  # RENAME_NOREPLACE
            error = ctypes.get_errno()
            raise ValueError(f"private repository publication failed without overwriting destination: {os.strerror(error)}")
        parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
        return before
    finally:
        os.close(root_fd)
        if stage.exists():
            shutil.rmtree(stage)


def compare(before, after, write_scope):
    """Describe actual attempt changes relative to its captured dirty baseline."""
    if before.get("root") != after.get("root"):
        raise ValueError("cannot compare different repository workspaces")
    scope = [_relative(item) + ("/" if item.endswith("/") else "") for item in write_scope]
    changed = sorted(name for name in before["files"].keys() | after["files"].keys()
                     if before["files"].get(name) != after["files"].get(name)
                     or before.get("modes", {}).get(name) != after.get("modes", {}).get(name))
    violations = [name for name in changed if not owns(name, scope)]
    if before.get("revision") != after.get("revision"):
        violations.append(".git/HEAD")
    chunks, omissions, size = [], [], 0
    for name in changed:
        old_mode = before.get("modes", {}).get(name)
        new_mode = after.get("modes", {}).get(name)
        if old_mode is not None and new_mode is not None and old_mode != new_mode:
            # Unified text diffs do not encode permission changes. Retain their
            # hashes/modes but do not claim this text patch is complete.
            omissions.append(name)
        old, new = before.get("contents", {}).get(name), after.get("contents", {}).get(name)
        if before["files"].get(name) is None:
            old = ""
        if after["files"].get(name) is None:
            new = ""
        if old is None or new is None:
            omissions.append(name)
            continue
        lines = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                     fromfile=f"before/{name}", tofile=f"after/{name}")
        patch = "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines)
        if size + len(patch.encode()) > MAX_PATCH_BYTES:
            omissions.append(name)
            continue
        chunks.append(patch)
        size += len(patch.encode())
    return {"changed_paths": changed, "violations": violations, "patch": "".join(chunks),
            "patch_omissions": sorted(set(omissions)), "patch_complete": not omissions,
            "before_digest": before["digest"], "after_digest": after["digest"]}
