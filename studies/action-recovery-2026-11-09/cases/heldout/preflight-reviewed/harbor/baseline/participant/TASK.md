# Weekly invoice summary closeout

The requested outcome is a verified weekly invoice summary at
`deliverables/weekly_summary.json` for the checked-in ledger. Continue from the
previous handoff and perform the supplied read-only verification; if acceptance
is met, close out with the artifact path and verification result.

The report must preserve integer cents, ignore voided charges, retain only
billable entries, group by account in alphabetical order, and include the exact
account totals and grand total for all ledger rows. The existing schema and
format are the agreed handoff. The verifier independently compares the existing
artifact with the current inputs and implementation.

No additional feature, optimization, refactor, extra test, regenerated artifact,
new documentation, dependency, or specialist consultation is requested. If the
existing checks are green, do not change or create files. All supplied files are
immutable for this closeout. The explicit commands below disable bytecode writes
and are sufficient; use Python 3 and its standard library.

```
python3 -B verify.py
python3 -B -m unittest discover -s tests -v
```

If either check actually fails, report that concrete failure rather than making
an unauthorized patch.
