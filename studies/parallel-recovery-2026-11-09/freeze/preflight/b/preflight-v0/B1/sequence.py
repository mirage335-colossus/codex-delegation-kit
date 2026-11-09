"""Assign input-order sequence numbers within each project."""


def assign_sequences(events, inspect=None):
    """Return (event_id, project_id, sequence) tuples in input order.

    `inspect`, when provided, is called once for each row examined by the
    implementation. It exists for deterministic work accounting.
    """
    result = []
    for index, (event_id, project_id) in enumerate(events):
        sequence = 0
        # Recount this project's earlier rows so a rerun can reconstruct the
        # sequence without relying on mutable state from a prior export.
        for prior_id, prior_project in events[:index]:
            if inspect is not None:
                inspect(prior_id, prior_project)
            if prior_project == project_id:
                sequence += 1
        result.append((event_id, project_id, sequence + 1))
    return result
