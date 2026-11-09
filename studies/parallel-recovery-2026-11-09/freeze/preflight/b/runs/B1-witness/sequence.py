"""Assign input-order sequence numbers within each project."""


def assign_sequences(events, inspect=None):
    """Return (event_id, project_id, sequence) tuples in input order.

    `inspect`, when provided, is called once for each row examined by the
    implementation. It exists for deterministic work accounting.
    """
    result = []
    counts = {}
    for event_id, project_id in events:
        if inspect is not None:
            inspect(event_id, project_id)
        sequence = counts.get(project_id, 0) + 1
        counts[project_id] = sequence
        result.append((event_id, project_id, sequence))
    return result
