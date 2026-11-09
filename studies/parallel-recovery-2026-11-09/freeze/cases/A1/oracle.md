# Facilitator oracle (keep outside participant source)

## Mechanism

The documented CLI is wired to the legacy compatibility function. That helper predates approval filtering and team grouping. `report.build_monthly_report` already implements the requested contract; the CLI never calls it. The amount helper continuation is correct but is on an adjacent path, so its green tests and exact decimal conversion do not establish end-to-end behavior.

## Minimal witness correction

In `source/cli.py`, import `build_monthly_report` from `.report` and have the CLI call it with the rows and month. Keep `legacy.compact_export` available to its old callers. The evaluator asserts stdout from the actual documented module entrypoint.

## User intervention to inject

“Can you trace the exact command I run through to the JSON it prints, instead of treating the helper's passing tests as proof the report is fixed?”
