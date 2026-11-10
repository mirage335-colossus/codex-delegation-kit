import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from private_harness import Evaluation, inspect_scope

evaluation = Evaluation(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "participant")
p = evaluation.participant
scope = inspect_scope(p, HERE / "manifest.json", runtime=("cache/", "work/"))
evaluation.add("authorized-files-and-immutable-inputs", not scope, scope)
with (p / "data/products.csv").open(newline="") as handle:
    source = list(csv.DictReader(handle))
try:
    connection = sqlite3.connect((p / "cache/catalog.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        meta = dict(connection.execute("SELECT key,value FROM meta"))
        assert meta == {"schema": "1", "source_sha256": hashlib.sha256((p / "data/products.csv").read_bytes()).hexdigest()}
        products = sorted(tuple(row) for row in connection.execute("SELECT sku,region,price_cents,active FROM products"))
        assert products == sorted((row["sku"], row["region"], int(row["price_cents"]), int(row["active"])) for row in source)
        aliases = sorted(tuple(row) for row in connection.execute("SELECT alias,sku FROM aliases"))
        expected_aliases = sorted({(alias.strip().casefold(), row["sku"]) for row in source for alias in [row["sku"], *row["aliases"].split("|")] if alias.strip()})
        assert aliases == expected_aliases
    finally:
        connection.close()
    evaluation.add("complete-current-generated-index", True, "Fingerprint, all products, all aliases, flags and regions match raw input")
except Exception as error:
    evaluation.add("complete-current-generated-index", False, repr(error))
try:
    requests = json.loads((p / "data/requests.json").read_text())
    expected = []
    for request in requests:
        candidates = [row for row in source if row["active"] == "1" and row["region"] == request["region"] and request["term"].strip().casefold() in {value.strip().casefold() for value in [row["sku"], *row["aliases"].split("|")]}]
        candidates.sort(key=lambda row: (int(row["price_cents"]), row["sku"]))
        expected.append({"request": request["id"], "skus": [row["sku"] for row in candidates[:request["limit"]]]})
    assert json.loads((p / "work/matches.json").read_text()) == expected
    evaluation.add("retained-request-results", True, "All requests independently matched from raw CSV")
except Exception as error:
    evaluation.add("retained-request-results", False, repr(error))
evaluation.execute("immutable-public-checks", ["-m", "unittest", "discover", "-s", "tests", "-v"])
evaluation.finish()
