"""A tiny line-oriented feed importer."""
import json
import sqlite3


def validate(record):
    return (isinstance(record, dict)
            and isinstance(record.get("id"), int)
            and isinstance(record.get("value"), str)
            and bool(record["value"]))


def connect(path):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
    return db


def import_lines(lines, db):
    """Parse, validate, and persist a batch of JSON lines."""
    accepted = 0
    for line in lines:
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not validate(record):
            continue
        db.execute("INSERT OR REPLACE INTO records (id, value) VALUES (?, ?)",
                   (record["id"], record["value"]))
        accepted += 1
    db.commit()
    return accepted

