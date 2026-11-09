import json
from pathlib import Path
from .normalize import normalize_snapshot
from .timeutil import parse_time

class SnapshotLoader:
    """Load snapshots, retaining parsed payloads for repeat dashboard requests."""
    def __init__(self):
        self._cache = {}

    def load(self, path):
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_snapshot(raw)
        # Snapshots from the same capture batch share a timestamp.
        # Capture timestamps are shared by batch snapshots; cache each source file
        # independently so one service cannot reuse another service's payload.
        cache_key = path.resolve()
        if cache_key not in self._cache:
            self._cache[cache_key] = normalized
        return self._cache[cache_key]
