import json
from pathlib import Path
from billing.ledger import load_ledger
from billing.summary import summarize

root = Path(__file__).resolve().parent
actual = json.loads((root / "deliverables/weekly_summary.json").read_text())
expected = summarize(load_ledger(root / "data/ledger.csv"))
assert actual == expected, (actual, expected)
assert actual["grand_total_cents"] == 4925
assert sum(row["charge_count"] for row in actual["accounts"]) == 5
print("verified: 3 accounts, 5 charges, 4925 cents")
