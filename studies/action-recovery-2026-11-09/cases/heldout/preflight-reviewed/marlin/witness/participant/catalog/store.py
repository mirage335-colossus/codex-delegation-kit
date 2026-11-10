import hashlib
from pathlib import Path
import sqlite3


def open_index(index, source):
    index, source = Path(index), Path(source)
    if not index.is_file():
        raise FileNotFoundError("catalog index is missing; see OPERATIONS.md")
    connection = sqlite3.connect(index.as_uri() + "?mode=ro", uri=True)
    try:
        meta = dict(connection.execute("SELECT key, value FROM meta"))
        if meta.get("schema") != "1" or meta.get("source_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError("catalog index is stale; rebuild using OPERATIONS.md")
    except BaseException:
        connection.close()
        raise
    return connection
