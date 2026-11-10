# Development exercise fixtures

Two Python 3 standard-library cases are staged. Participant-facing files are scoped to each `caseN/participant/`. Private evaluators and independent witnesses are in sibling `caseN/private/`; preflight command evidence is under `case1/logs/`. Corrected reference copies are under `validation/` for harness verification only and must not be distributed as participant inputs. Initial drafts are preserved under `initial-draft/`.

## Case names

1. **Deadline batch outcome** — batch processing with a delivery cutoff.
2. **Inventory receiving outcome** — importing supplier delivery data into stock.

Each participant `README.md` gives the runner. All checks use the Python standard library.
