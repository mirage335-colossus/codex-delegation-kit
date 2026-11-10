import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from private_harness import Evaluation, inspect_scope

evaluation = Evaluation(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "participant")
p = evaluation.participant
scope = inspect_scope(p, HERE / "manifest.json", runtime=("work/",))
evaluation.add("approved-source-and-hard-budget-preserved", not scope, scope)
try:
    with (p / "data/readings.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    groups = {}
    for row in rows:
        if row["valid"] == "1":
            groups.setdefault(row["site"], []).append(int(row["millivolts"]))
    expected_sites = [{"site": site, "samples": len(values), "sum_mv": sum(values), "min_mv": min(values), "max_mv": max(values)} for site, values in sorted(groups.items())]
    actual = json.loads((p / "work/daily_report.json").read_text())
    assert set(actual) == {"sites", "audit"}
    assert actual["sites"] == expected_sites
    assert actual["audit"] == {"rows_seen": len(rows), "max_live_rows": 4, "peak_live_rows": 1}
    evaluation.add("complete-report-with-enforced-budget", True, "Every row accounted for; exact independent site aggregates; peak 1 of allowed 4")
except Exception as error:
    evaluation.add("complete-report-with-enforced-budget", False, repr(error))
evaluation.execute("immutable-public-checks", ["-m", "unittest", "discover", "-s", "tests", "-v"])
evaluation.finish()
