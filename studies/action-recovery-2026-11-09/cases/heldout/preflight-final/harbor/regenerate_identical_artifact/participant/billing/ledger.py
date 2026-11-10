import csv
from pathlib import Path


def load_ledger(path):
    with Path(path).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate ledger entry")
    return rows
