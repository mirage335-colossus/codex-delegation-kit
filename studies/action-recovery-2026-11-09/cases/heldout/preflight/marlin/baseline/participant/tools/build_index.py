import argparse
import csv
import hashlib
from pathlib import Path
import sqlite3


def build(source, output):
    source, output = Path(source), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".building")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript(
            "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);"
            "CREATE TABLE products (sku TEXT PRIMARY KEY, region TEXT NOT NULL, price_cents INTEGER NOT NULL, active INTEGER NOT NULL);"
            "CREATE TABLE aliases (alias TEXT NOT NULL, sku TEXT NOT NULL, PRIMARY KEY(alias,sku));"
            "CREATE INDEX aliases_lookup ON aliases(alias);"
        )
        connection.executemany("INSERT INTO meta VALUES (?,?)", [("schema", "1"), ("source_sha256", hashlib.sha256(source.read_bytes()).hexdigest())])
        with source.open(newline="") as handle:
            for row in csv.DictReader(handle):
                connection.execute("INSERT INTO products VALUES (?,?,?,?)",
                                   (row["sku"], row["region"], int(row["price_cents"]), int(row["active"])))
                aliases = {part.strip().casefold() for part in [row["sku"], *row["aliases"].split("|")] if part.strip()}
                connection.executemany("INSERT INTO aliases VALUES (?,?)", [(alias, row["sku"]) for alias in sorted(aliases)])
        connection.commit()
    finally:
        connection.close()
    temporary.replace(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    build(args.source, args.output)
    print("catalog index ready:", args.output)
