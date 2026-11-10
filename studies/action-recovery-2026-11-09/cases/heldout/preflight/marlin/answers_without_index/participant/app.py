import argparse
import json
from pathlib import Path
from catalog.store import open_index
from catalog.matching import match_requests

parser = argparse.ArgumentParser()
parser.add_argument("--requests", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
connection = open_index(root / "cache/catalog.sqlite", root / "data/products.csv")
try:
    matches = match_requests(connection, json.loads((root / args.requests).read_text()))
finally:
    connection.close()
output = root / args.output
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(matches, indent=2) + "\n")
print(json.dumps({"requests": len(matches), "output": args.output}, sort_keys=True))
