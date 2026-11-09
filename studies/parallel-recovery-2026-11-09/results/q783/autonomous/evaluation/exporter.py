"""Assemble pages for the event export endpoint."""
from models import ExportPage, ExportRow
from pagination import page_bounds


def export_page(events, cursor, limit, state, inspect=None):
    """Return a page in accepted order and advance caller-owned project state.

    Only rows returned on this page are examined and assigned sequence values.
    """
    start, end = page_bounds(len(events), cursor, limit)
    rows = []
    for event in events[start:end]:
        if inspect is not None:
            inspect(event)
        rows.append(
            ExportRow(
                event.event_id,
                event.project_id,
                state.next_for(event.project_id),
                event.payload,
            )
        )
    return ExportPage(rows=tuple(rows), next_cursor=end, has_more=end < len(events))
