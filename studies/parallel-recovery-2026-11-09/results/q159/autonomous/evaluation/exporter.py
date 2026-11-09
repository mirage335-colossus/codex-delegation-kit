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
    for event in selected:
        if inspect is not None:
            inspect(event)
    rows = tuple(
        ExportRow(
            event.event_id,
            event.project_id,
            state.next_for(event.project_id),
            event.payload,
        )
        for event in selected
    )
    return ExportPage(rows=rows, next_cursor=end, has_more=end < len(events))
