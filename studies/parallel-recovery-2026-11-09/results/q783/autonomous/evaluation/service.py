"""Public entry point and response serialization for event exports."""
from exporter import export_page


def get_export_page(events, cursor, limit, project_state, inspect=None):
    """Build one API page while preserving the caller's state ownership."""
    return export_page(events, cursor, limit, project_state, inspect=inspect)


def response_body(page):
    """Convert the typed page to the stable JSON-compatible response shape."""
    return {
        "rows": [
            {
                "event_id": row.event_id,
                "project_id": row.project_id,
                "sequence": row.sequence,
                "payload": row.payload,
            }
            for row in page.rows
        ],
        "next_cursor": page.next_cursor,
        "has_more": page.has_more,
    }
