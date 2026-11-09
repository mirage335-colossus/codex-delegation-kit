"""Stable data shapes used by the event export API."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Event:
    event_id: str
    project_id: str
    accepted_at: int
    payload: Any


@dataclass(frozen=True)
class ExportRow:
    event_id: str
    project_id: str
    sequence: int
    payload: Any


@dataclass(frozen=True)
class ExportPage:
    rows: tuple[ExportRow, ...]
    next_cursor: int
    has_more: bool
