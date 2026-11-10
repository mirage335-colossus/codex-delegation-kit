"""One transactional scheduling authority. No background services or dependencies."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import time

SCHEMA = 2
_HASH_CACHE = {}


def file_identity(path):
    """Cache bytes only while inode/size/mtime/ctime metadata is unchanged."""
    path = Path(path)
    try:
        info = path.stat()
    except FileNotFoundError:
        return None
    key = (str(path), info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    if key not in _HASH_CACHE:
        if len(_HASH_CACHE) >= 4096:
            _HASH_CACHE.clear()
        value = hashlib.sha256(path.read_bytes()).hexdigest()
        after = path.stat()
        if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError(f"input changed while hashing: {path}")
        _HASH_CACHE[key] = value
    return _HASH_CACHE[key]


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def safe_directory(directory):
    directory = Path(directory).absolute()
    if any(p.is_symlink() for p in (directory, *directory.parents)):
        raise ValueError("run directory must not traverse symlinks")
    return directory


class Store:
    """Small inventories use one JSON snapshot plus an append-only event journal.

    SQLite commits snapshot and events together. A transaction is deliberately
    short: never perform execution or model calls while holding it.
    """
    def __init__(self, directory, *, create=False):
        self.directory = safe_directory(directory)
        self.path = self.directory / "state.sqlite3"
        if self.path.is_symlink():
            raise ValueError("state database must not be a symlink")
        if not create and not self.path.is_file():
            raise ValueError("run does not exist; use start")
        if create:
            self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.connection.execute("PRAGMA busy_timeout=10000")
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.execute("PRAGMA journal_mode=WAL")
        with self.connection:
            self.connection.execute("CREATE TABLE IF NOT EXISTS snapshot (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)")
            self.connection.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, time REAL NOT NULL, operation TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL)")

    def close(self):
        self.connection.close()

    def initialize(self, state):
        with self.transaction(optional=True) as (old, emit):
            if old:
                raise ValueError("run already exists; use resume or recover")
            state = dict(state, schema=SCHEMA)
            old.update(state)
            emit("created", {"run": state["id"], "inventory": state["inventory_digest"]})

    @contextmanager
    def transaction(self, *, optional=False):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute("SELECT value FROM snapshot WHERE id=1").fetchone()
            if row is None and not optional:
                raise ValueError("run database has no initialized inventory")
            state = json.loads(row[0]) if row else {}
            before = encoded(state)
            if state:
                version = state.get("schema", 1)
                if version not in (1, SCHEMA):
                    raise ValueError(f"unsupported state schema {version}; preserve database")
                # Additive migration: old event envelopes and task histories stay exact.
                if version == 1:
                    state.setdefault("holds", {})
                    state.setdefault("observations", {})
                    state["schema"] = SCHEMA
            def emit(kind, data, operation=None):
                operation = operation or f"event-{time.time_ns()}"
                previous = self.connection.execute("SELECT kind,data FROM events WHERE operation=?", (operation,)).fetchone()
                payload = encoded(data)
                if previous:
                    if previous != (kind, payload):
                        raise ValueError("operation identity reused with different event")
                    return False
                self.connection.execute("INSERT INTO events(time,operation,kind,data) VALUES(?,?,?,?)", (time.time(), operation, kind, payload))
                return True
            yield state, emit
            after = encoded(state)
            if after != before:
                self.connection.execute("INSERT INTO snapshot(id,value) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET value=excluded.value", (after,))
            self.connection.execute("COMMIT")
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def read(self):
        row = self.connection.execute("SELECT value FROM snapshot WHERE id=1").fetchone()
        if row is None:
            raise ValueError("run database has no initialized inventory")
        state = json.loads(row[0])
        if state.get("schema", 1) not in (1, SCHEMA):
            raise ValueError("unsupported state schema")
        return state

    def events(self, after=0):
        return [{"sequence": row[0], "time": row[1], "operation": row[2],
                 "kind": row[3], "data": json.loads(row[4])}
                for row in self.connection.execute("SELECT seq,time,operation,kind,data FROM events WHERE seq>? ORDER BY seq", (after,))]


def input_identity(workspace, inputs):
    """Narrow declared inputs, including absent outputs; never hash arbitrary trees."""
    workspace = Path(workspace).resolve()
    result = {}
    for name in inputs:
        path = (workspace / name).resolve()
        if not path.is_relative_to(workspace):
            raise ValueError(f"input outside workspace: {name}")
        if path.is_dir():
            raise ValueError(f"inputs must be individual files: {name}")
        result[name] = file_identity(path)
    return result
