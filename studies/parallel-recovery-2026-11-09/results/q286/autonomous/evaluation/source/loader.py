import json
from pathlib import Path
from .normalize import normalize_snapshot

class SnapshotLoader:
    """Load snapshots, retaining parsed payloads for repeat dashboard requests."""
    def __init__(self):
        self._cache = {}

    def load(self, path):
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_snapshot(raw)
        # A capture timestamp identifies a batch, not a service snapshot.
        # Cache each source file independently so simultaneous snapshots do
        # not overwrite one another in the dashboard.
        cache_key = path.resolve()
        if cache_key not in self._cache:
            self._cache[cache_key] = normalized
        return self._cache[cache_key]
