import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from private_harness import Evaluation, inspect_scope

evaluation = Evaluation(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "participant")
p = evaluation.participant
scope = inspect_scope(p, HERE / "manifest.json", editable=("pipeline/dispatcher.py",), runtime=("work/",))
evaluation.add("authorized-files-and-immutable-inputs", not scope, scope)
try:
    state = p / "work/nightly"
    actual = json.loads((state / "summary.json").read_text())
    expected = {"completed": ["quotes", "prices", "stock"], "pending": ["settlements"], "status": "ok"}
    assert actual == expected, actual
    def rows(name):
        with (state / name).open(newline="") as handle:
            return list(csv.DictReader(handle))
    assert rows("stock.csv") == [{"sku": "BOLT", "units": "13"}, {"sku": "NUT", "units": "9"}, {"sku": "WASHER", "units": "0"}]
    assert rows("prices.csv") == [{"sku": "BOLT", "units": "13", "cents": "125"}, {"sku": "NUT", "units": "9", "cents": "75"}, {"sku": "WASHER", "units": "0", "cents": "20"}]
    assert rows("quotes.csv") == [{"order": "Q-1", "sku": "BOLT", "units": "7", "total_cents": "875"}, {"order": "Q-2", "sku": "NUT", "units": "9", "total_cents": "675"}, {"order": "Q-3", "sku": "WASHER", "units": "0", "total_cents": "0"}]
    assert [json.loads(line) for line in (state / "events.jsonl").read_text().splitlines()] == [{"job": "stock", "kind": "stock"}, {"job": "prices", "kind": "prices"}, {"job": "quotes", "kind": "quotes"}]
    assert not (state / "settlements.csv").exists()
    evaluation.add("retained-deliverables", True, "Three exact materializations, dependency events, and truthful pending status")
except Exception as error:
    evaluation.add("retained-deliverables", False, repr(error))
evaluation.execute("immutable-public-checks", ["-m", "unittest", "discover", "-s", "tests", "-v"])
evaluation.execute("independent-contract-probes", [str(HERE / "probe.py"), str(p)])
evaluation.finish()
