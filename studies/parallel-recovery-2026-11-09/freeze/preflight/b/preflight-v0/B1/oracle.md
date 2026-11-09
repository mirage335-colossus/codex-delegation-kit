# Private oracle: B1

The requested behavior partitions naturally by project: a single pass can retain the next count for each project and append each result immediately, preserving input order. The baseline's prefix recount is correct on small inputs but performs quadratic inspections; the evaluator's stable limit is 3N. A witness patch is to replace the per-row prefix recount with a dictionary of per-project counts updated as each input row is visited. This must retain the same tuple format and callback work accounting.

Frozen user intervention: “Could each project's counter advance independently as its events are visited, since sequence uniqueness only applies within one project?”
