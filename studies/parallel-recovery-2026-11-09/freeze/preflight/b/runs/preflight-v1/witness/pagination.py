"""Cursor helpers for accepted-order event pages."""
DEFAULT_PAGE_SIZE = 64


def page_bounds(total, cursor, limit=None):
    if cursor < 0:
        raise ValueError("cursor must be non-negative")
    if limit is None:
        limit = DEFAULT_PAGE_SIZE
    if limit < 0:
        raise ValueError("limit must be non-negative")
    start = min(cursor, total)
    end = min(start + limit, total)
    return start, end
