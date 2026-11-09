"""Assemble pages for the event export endpoint."""
from models import ExportPage, ExportRow
from pagination import page_bounds


def export_page(events, cursor, limit, state, inspect=None):
    """Return a page of the accepted event batch.

    `state` is retained by the caller and advanced for rows returned on this
    page. `inspect` is an optional deterministic counter for rows examined.
    """
    # The export originally used the shared global reservation path: it built
    # a globally ordered sequence for the full batch before slicing a page.
    ordered = sorted(enumerate(events), key=lambda pair: (pair[1].accepted_at, pair[1].event_id))
    for _position, event in ordered:
        if inspect is not None:
            inspect(event)
    start, end = page_bounds(len(ordered), cursor, limit)
    selected = ordered[start:end]
    rows = tuple(
        ExportRow(event.event_id, event.project_id, position + 1, event.payload)
        for position, event in selected
    )
    return ExportPage(rows=rows, next_cursor=end, has_more=end < len(ordered))
