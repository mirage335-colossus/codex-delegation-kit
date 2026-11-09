"""Small in-memory list pagination helper."""
DEFAULT_PAGE_SIZE = 20


def paginate(items, offset=0, limit=None):
    """Return a page; omitted limit uses DEFAULT_PAGE_SIZE."""
    actual_limit = limit or DEFAULT_PAGE_SIZE
    start = max(0, offset)
    return list(items[start:start + actual_limit])
