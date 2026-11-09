"""Caller-owned incremental project sequence state."""


class ProjectSequenceState:
    def __init__(self):
        self._last = {}

    def next_for(self, project_id):
        """Advance and return this project's next 1-based sequence."""
        value = self._last.get(project_id, 0) + 1
        self._last[project_id] = value
        return value

    def last_for(self, project_id):
        """Return the last assigned sequence, or zero before first use."""
        return self._last.get(project_id, 0)

    def snapshot(self):
        """Return a copy suitable for storing with a caller's export session."""
        return dict(self._last)

    @classmethod
    def from_snapshot(cls, snapshot):
        state = cls()
        state._last.update(snapshot)
        return state
