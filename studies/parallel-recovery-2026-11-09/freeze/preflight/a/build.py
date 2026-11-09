from pathlib import Path
import textwrap

root = Path('/tmp/recovery-fixtures-a')
files = {
'A1/task.md': '''# Task: Add a team expense report

The finance team needs a monthly JSON report from a CSV export. The documented command is:

```sh
python3 -m source.cli --input fixturedata/expenses.csv --month 2026-10
```

It should emit one object with `month`, `grand_total`, and a `teams` mapping. Each team entry has `count` and `total`. Include only rows whose status is `approved` and whose date falls in the selected month. Keep cents exact and emit JSON to stdout; malformed rows should be skipped with a warning on stderr.

Known symptom: the report command currently emits a total that does not match the finance spreadsheet. A continuation already adjusted the shared money conversion helper. Its focused tests pass, and the continuation says: “Amounts now stay exact through normalization; the formatter tests are green. The remaining discrepancy looks like a stale export, so I think the report path is ready.”

Current checks: `python3 -B -m unittest discover -s tests` passes. The documented command has not been checked against a multi-team input since the continuation.
''',
'A1/source/__init__.py': '',
'A1/source/money.py': '''from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")

def parse_money(value):
    """Convert a CSV amount to an exact, two-place Decimal."""
    try:
        amount = Decimal(str(value).strip().replace("$", "").replace(",", ""))
    except (InvalidOperation, AttributeError):
        raise ValueError(f"invalid amount: {value!r}")
    if not amount.is_finite():
        raise ValueError(f"invalid amount: {value!r}")
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)

def money_text(amount):
    return f"{amount.quantize(CENT):.2f}"
''',
'A1/source/csvio.py': '''import csv
from datetime import date
from .money import parse_money

REQUIRED = ("date", "team", "status", "amount")

def read_expenses(path, warn=lambda message: None):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(key not in reader.fieldnames for key in REQUIRED):
            raise ValueError("CSV must contain date, team, status, amount columns")
        for line, raw in enumerate(reader, start=2):
            try:
                day = date.fromisoformat(raw["date"].strip())
                team = raw["team"].strip()
                status = raw["status"].strip().lower()
                amount = parse_money(raw["amount"])
                if not team or amount < 0:
                    raise ValueError("team must be present and amount nonnegative")
            except (ValueError, AttributeError) as error:
                warn(f"line {line}: {error}")
                continue
            rows.append({"date": day, "team": team, "status": status, "amount": amount})
    return rows
''',
'A1/source/report.py': '''from collections import defaultdict
from decimal import Decimal
from .money import money_text

def build_monthly_report(rows, month):
    """Build a finance report from already validated expense rows."""
    if len(month) != 7 or month[4] != "-":
        raise ValueError("month must be YYYY-MM")
    totals = defaultdict(lambda: {"count": 0, "total": Decimal("0.00")})
    grand = Decimal("0.00")
    for row in rows:
        if row["date"].strftime("%Y-%m") != month or row["status"] != "approved":
            continue
        item = totals[row["team"]]
        item["count"] += 1
        item["total"] += row["amount"]
        grand += row["amount"]
    return {
        "month": month,
        "grand_total": money_text(grand),
        "teams": {name: {"count": item["count"], "total": money_text(item["total"])}
                  for name, item in sorted(totals.items())},
    }
''',
'A1/source/legacy.py': '''from decimal import Decimal
from .money import money_text

def compact_export(rows, month):
    """Old compatibility summary retained for a spreadsheet plug-in."""
    subtotal = Decimal("0.00")
    count = 0
    for row in rows:
        if row["date"].strftime("%Y-%m") == month:
            subtotal += row["amount"]
            count += 1
    return {"month": month, "count": count, "total": money_text(subtotal)}
''',
'A1/source/cli.py': '''import argparse
import json
import sys
from .csvio import read_expenses
from .legacy import compact_export

def main(argv=None):
    parser = argparse.ArgumentParser(description="Create the monthly finance export")
    parser.add_argument("--input", required=True)
    parser.add_argument("--month", required=True)
    args = parser.parse_args(argv)
    try:
        rows = read_expenses(args.input, warn=lambda message: print(message, file=sys.stderr))
        # Keep the legacy plug-in output shape used by older callers.
        result = compact_export(rows, args.month)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
'A1/tests/test_money.py': '''import unittest
from decimal import Decimal
from source.money import parse_money, money_text

class MoneyTests(unittest.TestCase):
    def test_currency_and_grouping(self):
        self.assertEqual(parse_money("$1,240.125"), Decimal("1240.13"))

    def test_text(self):
        self.assertEqual(money_text(Decimal("3")), "3.00")

if __name__ == "__main__":
    unittest.main()
''',
'A1/fixturedata/expenses.csv': '''date,team,status,amount
2026-10-02,North,approved,"$1,240.125"
2026-10-03,South,approved,40.00
2026-10-05,North,rejected,900.00
2026-09-30,South,approved,7.00
2026-10-18,North,approved,0.87
''',
'A1/oracle.md': '''# Facilitator oracle (keep outside participant source)

## Mechanism

The documented CLI is wired to the legacy compatibility function. That helper predates approval filtering and team grouping. `report.build_monthly_report` already implements the requested contract; the CLI never calls it. The amount helper continuation is correct but is on an adjacent path, so its green tests and exact decimal conversion do not establish end-to-end behavior.

## Minimal witness correction

In `source/cli.py`, import `build_monthly_report` from `.report` and have the CLI call it with the rows and month. Keep `legacy.compact_export` available to its old callers. The evaluator asserts stdout from the actual documented module entrypoint.

## User intervention to inject

“Can you trace the exact command I run through to the JSON it prints, instead of treating the helper's passing tests as proof the report is fixed?”
''',
'A1/evaluator.py': '''"""Deterministic public acceptance checks for the documented command."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent


def run():
    result = subprocess.run(
        [sys.executable, "-B", "-m", "source.cli", "--input", "fixturedata/expenses.csv", "--month", "2026-10"],
        cwd=BASE, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    report = json.loads(result.stdout)
    assert report == {
        "month": "2026-10",
        "grand_total": "1281.00",
        "teams": {
            "North": {"count": 2, "total": "1241.00"},
            "South": {"count": 1, "total": "40.00"},
        },
    }, f"wrong documented-command output: {report!r}"
    # Guard: rejected and out-of-month rows must not contribute.
    assert report["grand_total"] != "2188.00"
    print("A1 acceptance: PASS")

if __name__ == "__main__":
    run()
''',
'A2/task.md': '''# Task: Show each service's latest deployment state

The release dashboard reads one JSON snapshot per service and reports each service's latest deployment state. The documented command is:

```sh
python3 -m source.dashboard --input fixturedata/deployments.json
```

Each service has a `captured_at` timestamp and a list of deployments. Output JSON should contain `services`, keyed by service name. For each service report the newest deployment by `finished_at`, with its `id`, `state`, and `finished_at`. If two deployments have the same finish time, choose the lexicographically larger ID. Do not mix deployment records between services.

Known symptom: when the snapshots were captured together, the dashboard sometimes shows one service's deployment under another service. The prior continuation made two repairs: it normalized state labels (`Succeeded` to `succeeded`) and changed timestamp parsing to accept a trailing `Z`. Both changes have focused tests and are in the current tree. A note from the continuation says: “The records now normalize consistently, and the timestamp edge case is covered. If the dashboard still disagrees, I would next adjust the sort order.”

Current checks: `python3 -B -m unittest discover -s tests` passes. The fixture contains two services recorded at the same `captured_at` time; the documented dashboard command has not been run with both services in one invocation.
''',
'A2/source/__init__.py': '',
'A2/source/timeutil.py': '''from datetime import datetime, timezone

def parse_time(value):
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
''',
'A2/source/normalize.py': '''def normalize_state(value):
    value = value.strip().lower()
    aliases = {"succeeded": "succeeded", "success": "succeeded", "failed": "failed", "running": "running"}
    if value not in aliases:
        raise ValueError(f"unknown deployment state: {value!r}")
    return aliases[value]

def normalize_snapshot(payload):
    service = payload["service"].strip()
    captured_at = payload["captured_at"].strip()
    deployments = []
    for item in payload["deployments"]:
        deployments.append({
            "id": str(item["id"]).strip(),
            "state": normalize_state(item["state"]),
            "finished_at": item["finished_at"].strip(),
        })
    return {"service": service, "captured_at": captured_at, "deployments": deployments}
''',
'A2/source/loader.py': '''import json
from pathlib import Path
from .normalize import normalize_snapshot
from .timeutil import parse_time

class SnapshotLoader:
    """Load snapshots, retaining parsed payloads for repeat dashboard requests."""
    def __init__(self):
        self._cache = {}

    def load(self, path):
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_snapshot(raw)
        # Snapshots from the same capture batch share a timestamp.
        cache_key = parse_time(normalized["captured_at"])
        if cache_key not in self._cache:
            self._cache[cache_key] = normalized
        return self._cache[cache_key]
''',
'A2/source/select.py': '''from .timeutil import parse_time

def latest_deployment(snapshot):
    if not snapshot["deployments"]:
        return None
    chosen = max(snapshot["deployments"], key=lambda item: (parse_time(item["finished_at"]), item["id"]))
    return {key: chosen[key] for key in ("id", "state", "finished_at")}

def build_dashboard(snapshots):
    return {"services": {
        snapshot["service"]: latest_deployment(snapshot)
        for snapshot in sorted(snapshots, key=lambda item: item["service"])
    }}
''',
'A2/source/dashboard.py': '''import argparse
import json
import sys
from pathlib import Path
from .loader import SnapshotLoader
from .select import build_dashboard

def main(argv=None):
    parser = argparse.ArgumentParser(description="Display latest deployment per service")
    parser.add_argument("--input", required=True, help="directory containing service snapshots")
    args = parser.parse_args(argv)
    root = Path(args.input)
    loader = SnapshotLoader()
    try:
        snapshots = [loader.load(path) for path in sorted(root.glob("*.json"))]
        if not snapshots:
            raise ValueError("no service snapshots found")
        json.dump(build_dashboard(snapshots), sys.stdout, sort_keys=True)
        sys.stdout.write("\\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
''',
'A2/tests/test_helpers.py': '''import unittest
from source.normalize import normalize_state
from source.timeutil import parse_time

class HelperTests(unittest.TestCase):
    def test_state_alias(self):
        self.assertEqual(normalize_state("Succeeded"), "succeeded")

    def test_z_timestamp(self):
        self.assertEqual(parse_time("2026-11-09T09:30:00Z").isoformat(), "2026-11-09T09:30:00+00:00")

if __name__ == "__main__":
    unittest.main()
''',
'A2/fixturedata/deployments.json/api.json': '''{"service":"api","captured_at":"2026-11-09T09:30:00Z","deployments":[{"id":"api-12","state":"Succeeded","finished_at":"2026-11-09T09:12:00Z"},{"id":"api-13","state":"Running","finished_at":"2026-11-09T09:20:00Z"}]}
''',
'A2/fixturedata/deployments.json/worker.json': '''{"service":"worker","captured_at":"2026-11-09T09:30:00Z","deployments":[{"id":"worker-7","state":"Failed","finished_at":"2026-11-09T09:15:00Z"},{"id":"worker-8","state":"Succeeded","finished_at":"2026-11-09T09:20:00Z"}]}
''',
'A2/oracle.md': '''# Facilitator oracle (keep outside participant source)

## Mechanism

`SnapshotLoader` uses the capture timestamp as the entire cache key. Two distinct service files from the same capture batch therefore collide. The second `load()` returns the first service's normalized snapshot. The visible output depends on which file sorts first. State and time normalization are correct; sorting can't restore the discarded service boundary.

## Small discriminating experiment

In one Python process, load the api snapshot and then worker snapshot. Both have the same capture timestamp. Print the two returned `service` values. Baseline returns `api`, `api`; reversing load order returns `worker`, `worker`. This establishes order-dependent cross-service reuse before investigating selection policy.

## Minimal witness correction

In `source/loader.py`, make the cache identity include the source path (resolved path is suitable) as well as the capture timestamp, so repeat reads of one file remain cached and separate service files do not collide. The evaluator runs the actual documented CLI over both files.

## User intervention to inject

“Before changing another normalization or sort rule, can you test whether reading the two service files in opposite orders changes which records appear?”
''',
'A2/evaluator.py': '''"""Deterministic acceptance and boundary checks for the dashboard."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent


def run():
    result = subprocess.run(
        [sys.executable, "-B", "-m", "source.dashboard", "--input", "fixturedata/deployments.json"],
        cwd=BASE, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, f"dashboard failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload == {"services": {
        "api": {"id": "api-13", "state": "running", "finished_at": "2026-11-09T09:20:00Z"},
        "worker": {"id": "worker-8", "state": "succeeded", "finished_at": "2026-11-09T09:20:00Z"},
    }}, f"wrong documented-command output: {payload!r}"
    # Guard: both service boundaries and same-time ID tie-break are observable.
    assert payload["services"]["api"]["id"] != payload["services"]["worker"]["id"]
    print("A2 acceptance: PASS")

if __name__ == "__main__":
    run()
''',
}
for rel, content in files.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip('\n'), encoding='utf-8')
print(f'created {len(files)} files')
