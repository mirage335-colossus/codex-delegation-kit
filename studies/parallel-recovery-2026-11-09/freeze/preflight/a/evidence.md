# Fixture verification record

## Participant trees and private evidence

Participant-safe copies are `/tmp/recovery-fixtures-a/A1/participant/` and `/tmp/recovery-fixtures-a/A2/participant/`. They contain only `task.md`, `source/`, `tests/`, and `fixturedata/`. Do not include `evaluator.py` or `oracle.md` in participant trees. The original single-input evaluators are preserved outside participant trees under `preflight/`. Full evaluators and oracle notes are adjacent to each `participant/` folder. `validation/` contains separate witness copies with minimal patches.

For an owner candidate tree, copy the participant-safe tree, then copy the fixture's `evaluator.py` into that disposable candidate root and run `python3 -B evaluator.py`. This works because the evaluator uses `Path(__file__).parent` as candidate root.

## A1 — finance CLI path

- Baseline tests from candidate root: `python3 -B -m unittest discover -s tests` — 5 passed.
- Baseline evaluator on disposable copy — exit 1 on fixture and generated independent input. The CLI emitted legacy summary shapes; fixture total was `2181.00` (includes a rejected row), generated November total was `10.45` (includes wrong-month rows and wrong legacy shape).
- Witness patch: `validation/A1/source/cli.py` switches the documented CLI to `report.build_monthly_report`, retaining the legacy helper for compatibility callers.
- Witness evaluator from `validation/A1/`: `python3 -B evaluator.py` — passed fixture and generated input.
- Witness tests from `validation/A1/`: `python3 -B -m unittest discover -s tests` — 5 passed.
- Independent generated input checks month filtering, approved/rejected rows, cent rounding, and malformed-row warning output.

## A2 — snapshot cache boundary

- Baseline tests from candidate root: `python3 -B -m unittest discover -s tests` — 4 passed.
- Baseline evaluator on disposable copy — exit 1 on fixture and generated independent input; a service sharing another service's capture timestamp is missing.
- Discriminating baseline experiment: load api then worker -> `api api`; reverse -> `worker worker`.
- Witness patch: `validation/A2/source/loader.py` includes resolved source path with capture timestamp in the cache identity.
- Witness evaluator from `validation/A2/`: `python3 -B evaluator.py` — passed fixture and generated input.
- Witness tests from `validation/A2/`: `python3 -B -m unittest discover -s tests` — 4 passed.
- Independent generated input checks two services sharing capture time, another at a different capture time, and equal-finish-time ID tie-breaking.

Baseline evaluator stdout/stderr remains at `A1/baseline.out` and `A2/baseline.out`; fresh disposable participant-copy logs are at `check/A1/evaluator.out` and `check/A2/evaluator.out`.

An initial unittest discovery attempt from the collection root failed before importing tests because the fixture package was not on that working directory's import path. Reruns from each fixture root and witness root passed; zero assertions ran in the initial setup attempt.
