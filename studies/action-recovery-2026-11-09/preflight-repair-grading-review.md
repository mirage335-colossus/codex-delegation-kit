# Repair grading runner independent review

**Disposition: approved.** The legacy CLI false pass and multi-stage ancestor identity defect are corrected and independently rechecked. This approves the grading runner, not any actual participant patch or model-run outcome.

Initial reviewed `grade_development.py` SHA-256: `e8a5df447b98c7050d9127954a2d4139af9249716c60c942eae11dc3c064a222`. This extends the earlier runner review without discarding it. Only requested review documents and owned scratch artifacts were written. No candidate files, treatment mapping, actual participant results, or model sessions were inspected or launched.

## Preserved counterexample

The reviewer built synthetic trusted-collection records around unchanged frozen case2 files and a named completed/released failed parent. A frozen repair template adds only immutable synthetic review evidence. Two repair workspaces contain the same source/input lineage; only their `import_file` adaptation differs. The actual reviewed grader code ran against these controlled path fixtures. Synthetic collection flags do not prove any real model settings or runtime.

The inadequate repair changes `return receive(rows)` to `return receive(normalize_vendor_feed(rows))`, preserving the canonical-only `receive` helper. It passes the original tests, requested supplier CLI output, direct legacy matrix and nine supplier CLI cases. The reviewed grader assigns `user_contract_checked_grade=passed`. But the supported CLI on the previously valid CSV `sku,quantity\nR-14,4\n` returns R-14 stock 3 and received units 0, rather than the original 7 and 4. The adapter requires reference metadata, whereas the original application accepts canonical receipts without it. Direct helper preservation therefore does not establish application-path preservation.

A matched correct import-layer adaptation retains canonical row handling while normalizing supplier rows. It passes the same checked contract and returns 7/4 on the canonical CLI input. Both adaptations keep raw-vendor `receive` diagnostics separate: allowing an import-layer implementation does not require broadening that internal helper's API.

Evidence: `/tmp/action-recovery-fixture-review/repair-grading-review/initial-results.json`, the retained grader snapshot, synthetic collections and `initial-outputs/`. This was an observed grader false pass, not merely a hypothetical input gap. The owner was asked to add matched frozen-original versus repair CLI checks for the existing canonical receipt matrix and include them in checked user-contract acceptance.

## Lineage checks already passed

Six controlled guards all execute zero checks: omitted repair flag, missing parent, missing template, template argument without a parent argument, a parent with different retained source, and modified protected review evidence. Correct explicit `--repair-template` with a distinct repair run ID is accepted. Successful repair evidence is labeled adaptive and excluded from the initial comparison. The parent collection, first-failure semantic evidence, source hashes and review-evidence hashes remain linked in the report.

Command evidence is retained in `check_initial.py`, `check_guards.py`, `guard-results.json` and their generated reports under the same scratch directory. Canonical fixture bytes and original failures were preserved.

## Scope consistency

The original TASK requires the supported application output and preservation of valid receipt behavior, not direct `receive(raw vendor rows)` support. Retaining the frozen evaluator result separately from checked TASK acceptance is correct. This boundary applies to initial runs as well as repairs. Initial raw evaluator scores should remain intact, but the final semantic comparison must not selectively treat the stronger internal-API condition as a user requirement for only the initial runs. The parent and grading owner have been notified.

Both the legacy CLI correction and subsequent multi-stage ancestry identity correction are verified below. Earlier failures remain retained rather than overwritten.


## Targeted correction recheck

Reviewed corrected source SHA-256 `6711b40c6add5ff244057aea2b42cbd5dd399ebcd4f4c63e11a8d5cd2e6143cd`. The grader now checks matched original/current canonical CSV receipts through `receive`, `import_file` and the actual CLI. The matrix includes no-reference receipts, four blank optional fields, three populated alternate fields and repeated references. The preserved bad import-layer repair now fails the checked user contract; the matched valid import-layer repair passes. Both frozen raw-vendor scores remain failed, accurately separated from the user boundary. The same bad/good distinction was observed with initial-run collections, so the task boundary is no longer repair-only.

A valid `strong-recovery` continuation retained the immediate failed repair and original failed parent, their exact report hashes, source lineage and protected evidence, and passed the functional checks. The new ancestry walker nevertheless accepted a mismatched ancestor identity: a synthetic file loaded as `parent1.semantic.json` contained `run_id="different_identity"`, while the immediate parent lacked the optional inherited root path/hash. The actual `repair_lineage` helper returned no errors. Every loaded report must match the ID used to locate it, in addition to the existing case and failed-acceptance checks. This is a narrow defect in the newly added multi-stage lineage path, and was sent to the grading owner for correction.

The wrong-identity experiment changed only reviewer-owned synthetic evidence and restored it afterward. Actual participant reports and ancestors were untouched. Evidence is retained in `check_corrected.py`, `corrected-results.json`, `corrected-outputs/`, and the corrected source snapshot.


## Final bounded acceptance

Accepted grader SHA-256: `a1ee79f597306cdc650dc0237e5300e49e3a4250c5e89a57a0e1791be71bff67`. The final source delta from the functionally rechecked version contains only tracking the expected ancestor ID and rejecting a loaded semantic report whose `run_id` differs. The preserved wrong-identity discriminator now returns the exact error `Ancestor failure report identity does not match the requested lineage ID/path.` Valid strong-family ancestry still returns no errors and retains the immediate failed repair and original failed parent. Synthetic ancestor evidence was restored byte-for-byte after the check.

Final evidence is in `accepted-identity-check.json` and `grade_development_accepted.py`. Earlier six lineage guards and bad/good application checks retain their coverage; the small final change does not alter those application probes or legacy acceptance logic. No unrelated checks, inference sessions or actual participant results were added to this review.

No required grader checks remain outstanding in the assigned scope. The checked TASK boundary now applies to initial and repair case2 assessments, with frozen private-oracle results retained separately. Additional repair/review evidence stays labeled adaptive, the selected template family is validated, and root failure identity/history remain explicit. Final semantic reporting, ownership acceptance and any actual participant patch acceptance remain the assigned grading/review owners' work.
