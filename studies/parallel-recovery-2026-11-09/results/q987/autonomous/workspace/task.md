# Task: Add a team expense report

The finance team needs a monthly JSON report from a CSV export. The documented command is:

```sh
python3 -m source.cli --input fixturedata/expenses.csv --month 2026-10
```

It should emit one object with `month`, `grand_total`, and a `teams` mapping. Each team entry has `count` and `total`. Include only rows whose status is `approved` and whose date falls in the selected month. Keep cents exact and emit JSON to stdout; malformed rows should be skipped with a warning on stderr.

Known symptom: the report command currently emits a total that does not match the finance spreadsheet. A continuation already adjusted the shared money conversion helper. Its focused tests pass, and the continuation says: “Amounts now stay exact through normalization; the formatter tests are green. The remaining discrepancy looks like a stale export, so I think the report path is ready.”

Current checks: `python3 -B -m unittest discover -s tests` passes. The documented command has not been checked against a multi-team input since the continuation.
