# Public usage telemetry

`usage-records.jsonl` contains 1,112 per-response numeric usage records from two
historical cohorts. Each record identifies its cohort, role, observed model,
study-local participant, attempt, and response ordinal. Response and participant
identifiers are aliases; source conversation identifiers and paths are omitted.

Run the standard-library calculator with Python 3.11 or newer:

```sh
python3 -B examples/recompute_verification_usage.py
```

It prints JSON totals grouped by cohort, role, and model, plus combined model
totals, participant and attempt counts, and Luna token shares. To use a relocated
copy of the data or save the result, pass `--input PATH` or `--output PATH`.
Luna shares are reported both across all records and across delegated records;
the latter excludes main-chat usage from its denominator.
Cached input is a subset of input, and reasoning output is a subset of output;
neither is added again to total tokens. The calculator performs arithmetic only
and makes no API-dollar or weekly-allowance conversion.

These are historical reported numeric records. They support arithmetic
recomputation and duplicate detection over the published dataset. They do not
independently authenticate provider identity or source-log completeness, and
they cannot recreate past model outcomes, quality, or elapsed time.
