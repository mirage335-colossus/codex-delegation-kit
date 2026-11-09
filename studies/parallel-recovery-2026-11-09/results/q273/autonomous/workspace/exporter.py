"""Assemble pages for the event export endpoint."""
from models import ExportPage, ExportRow
from pagination import page_bounds


def export_page(events, cursor, limit, state, inspect=None):
    """Return a page of the accepted event batch.

    `state` is retained by the caller and advanced for rows returned on this
    page. `inspect` is an optional deterministic counter for rows examined.
    """
    start, end = page_bounds(len(events), cursor, limit)
    selected = events[start:end]
    rows = []
    for event in selected:
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
