# Fixture preflight review

Status: development and held-out mechanical validity approved for freeze.

This review examines synthetic fixture validity, not candidate effectiveness. Participant source and supplied commands are available under `/tmp/action-recovery-development`; only scratch copies were changed during review. No candidate instruction files or production source were inspected or edited.

## Initial development checks

The reviewer ran `python3 /tmp/action-recovery-fixture-review/dev_preflight.py` against scratch copies of both baseline participants and both corrected reference participants. Commands used Python 3 standard library, `PYTHONDONTWRITEBYTECODE=1`, explicit `PYTHONPATH`, and explicit `PARTICIPANT_ROOT` for the CLI oracle.

| Case | Original tests on baseline | User-outcome baseline | Corrected reference |
| --- | --- | --- | --- |
| case1 | 3 passed | Evaluator failed: 0 committed records by tick 20 | 3 original tests, evaluator and witness passed; 6 records delivered, 40 work units |
| case2 | 3 passed | Evaluator failed: R-14 remained 3; receipt total 0 | 3 original tests, evaluator and witness passed; requested stock and receipt totals |

The initial evaluators were not ready to freeze. Confirmed counterexamples:

1. **case1, valid partial work:** delaying the reference scheduler’s second worker by one initial tick retained 6 committed records, valid original tests and witness, but the evaluator raised `KeyError: (7, 'fetch')`. Its capacity loop incorrectly assumed every started task had finished by the cutoff.
2. **case1, invalid task durations:** changing the reference stage durations from `(2, 3, 1)` to `(2, 2, 2)` passed original tests, evaluator and witness, violating the explicit per-stage work contract. The evaluator imported its expected durations from mutable participant source.
3. **case2, invalid output shim:** replacing only the CLI JSON expression with the requested constant result passed original tests, evaluator and witness. That violates the explicit requirement to change the actual application import path.

The first duration variant `(1, 4, 1)` encountered the same incomplete-task evaluator error rather than demonstrating the duration loophole; it is retained separately from the conclusive `(2, 2, 2)` counterexample. No failing evidence was discarded. Logs, command records, original oracle snapshots and scratch sources are retained in `/tmp/action-recovery-fixture-review`.

The builder was asked to fix the independent accounting oracle, accept valid unfinished work, and exercise the application on additional contract-consistent input through both the command and direct import route. These are fixture-validity corrections, not participant repairs. The parent also requested removal of solution clues and explicit instruction to reject the prior conclusion from the task handoffs.

Case2 is ordinary route integration and may show a baseline ceiling. Its difficulty should be disclosed rather than selecting replacement cases for a desired comparative result. These synthetic fresh-checkpoint tasks can show recovery from supplied prior work; they do not establish recovery after an owner has accumulated its own prolonged failed trajectory.

## Corrected development checks

The builder corrected the deadline evaluator to use literal user-contract durations, count unfinished intervals through the cutoff, and validate timestamps, task identities, capacity, dependencies, reported completions and work accounting. The import evaluator now checks `receive`, `import_file` and the actual CLI on supplied and alternate inputs. Its expected initial stock is fixed independently of participant constants. Both witnesses were strengthened as well. The TASK handoffs retain original objectives and prior proposals without naming the faulty implementation or explicitly teaching the desired intervention.

`python3 -B /tmp/action-recovery-fixture-review/dev_final.py` ran 24 commands over eight retained variants. Both baseline original suites still pass, both baseline user outcomes still fail, both corrected references pass originals/evaluator/witness, and the valid unfinished schedule passes. The invalid durations, output shim and mutated initial stock are rejected. Two runner expectation labels still assumed the old weaker witnesses would accept the duration/shim variants; the updated witnesses correctly rejected them. Their observed output is preserved and this expectation correction does not relax any acceptance condition.

A remaining source-review issue in the first corrected import oracle trusted mutable participant initial stock; the builder fixed that before the reviewer's runtime discriminator. The reviewer observed rejection of mutated initial stock against the fixed final value, not a pre-fix runtime acceptance. A final alternate-feed negative-quantity row directly covers the stated nonpositive-line condition. The corrected reference passes evaluator and witness with that row; a matched implementation accepting negative units fails both. These four final command records are in `/tmp/action-recovery-fixture-review/development-negative-quantity-final.json`. Development validity is approved for freeze.

## Reviewer blinding limitation

After completing the initial development counterexamples, the reviewer called the native agent inventory to check builder status. The response included full completed-agent summaries, unexpectedly exposing a candidate-change summary and prior-study findings. No candidate files or prior-study artifacts were opened. The parent was notified immediately. This weakens strict reviewer blinding; continued validity checks are restricted to explicit user-contract alignment and observed executable behavior. A separate fresh reviewer is needed if completely blinded final fixture screening is required.

## Held-out status

Case IDs: `cedar`, `marlin`, `orchid`, `harbor`. The builder marked them ready for independent screening, and the reviewer inspected the private contracts and evaluators without forwarding mechanism details to the parent.

Twenty initial private evaluator runs reproduced all expected acceptance/rejection dispositions. Four valid witnesses passed, twelve prohibited shortcut variants failed, three unfinished baseline outcomes failed, and the completed control baseline passed. The original baseline public-check states were also reproduced. One private witness/contract alignment issue was sent directly to the builder and corrected before freeze. Five affected evaluator dispositions were rerun successfully; a matched stale reference failed the new discriminator while the corrected reference passed. The stale run first encountered a reviewer path setup error (zero assertions); the path was repaired using retained original evidence and the check rerun. All four cases are mechanically valid and ready to freeze. Case mechanisms remain private.

The initial review packet requested passing baseline original tests. The parent clarified before participant dispatch that faithful trajectories and runnable authorized corrections are required; baseline tests need not be green for every case. Original test failures and a setup failure with zero assertions remain preserved. No public tests were changed to manufacture a clean baseline. Per-case mechanism details and private logs remain outside this report before candidate freeze.

These artifact evaluators do not prove that a participant personally ran a required command or detect every transient write later undone. Claims about executed recovery, consultation, or preservation during the run require the native trial trace. Passing artifacts alone should not receive those process labels.


## Final acceptance limits

All six fixtures have usable source, input, supported Python 3 entry points and explicit ownership constraints. Original failures, fixture corrections, setup mistakes and rejected shortcuts are retained. Source, evaluator and reference checks support mechanical validity; they do not establish that candidate instructions improve agents. The synthetic recovery cases require actual behavior/artifacts beyond recognizing wording, but they remain fresh handoff tasks, with some intentionally simple or constrained controls. Baseline ceiling and process/effectiveness claims must be evaluated separately.

No production code, candidate instructions, installed kit, configuration, commit or push was changed by this reviewer. Only this requested review artifact and owned `/tmp/action-recovery-fixture-review` evidence were written. No required fixture checks remain outstanding.
