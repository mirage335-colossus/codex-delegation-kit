# Held-out grading runner independent review

**Disposition: approved.** The reviewed runner calls the actual frozen private evaluators on timestamp-preserving copies, retains raw evaluations, and applies only the predeclared exact empty runtime-lock removal in a separate copy. No blocking defect was found.

Reviewed `grade_heldout.py` SHA-256: `444a5bf1692386c1c63a24eb92b57aba7f334731a87663dcdb7634cb7cd9831a`. The held-out manifests match the accepted fixture versions. This review changed no grader, fixture, candidate instruction, treatment plan or participant source. Only this requested report and `/tmp/action-recovery-fixture-review/heldout-grading-review` scratch evidence were written. No model session or participant inference was launched.

The prior turn interruption followed a completed read-only `cat`; no writing command or running process from that interrupted review needed reconciliation. Review resumed from that source inspection.

## Controlled validation

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/action-recovery-fixture-review/heldout-grading-review/check_runner.py`. Thirteen synthetic completed/released collection records exercised the actual grading function. Synthetic settings booleans test runner logic and do not verify any model runtime.

All four cases' retained reference witnesses were copied from accepted preflight artifacts using `copy2`; their deliverable-producing commands were **not** rerun. All four witness evaluations passed. The original baseline states remained distinguishable: unfinished outcomes failed and the completed control passed.

Additional controls established:

* The exact empty `scratch/codex-bwrap-synthetic-mount-targets-1000/lock` causes a raw scope failure, then passes the separately retained normalized evaluation.
* A nonempty file at that path is not normalized and remains a scope failure.
* With the empty known lock plus another scratch file, only the known lock is removed. The other file remains and the normalized evaluator still rejects scope.
* An identical completed artifact with a changed nanosecond mtime is rejected by the read-only case.
* A missing retained deliverable stays missing and is rejected. The grader does not reconstruct it.

All thirteen runs reported correct copy/original integrity, independently confirmed by snapshots around evaluation. File bytes and mtimes of each completed workspace, canonical fixture files, private evaluator files and shared evaluator harness were preserved. Raw and normalized reports, exact evaluator argv, hashes, output, artifact inventories and observations are retained in scratch `outputs/`; the compact checks are in `results.json`.

## Interpretation limits

The normalization policy was explicitly authorized and predeclared by the coordinator before inference. The implementation recognizes the exact path and empty content; it does not independently authenticate which process created that file. It removes no other file and does not replace the raw scope result. Empty parent directories are removed only while they remain empty.

`independent_functional_outcome=passed` is narrower than evaluator acceptance: nonempty locks, additional scratch files and a rewritten identical artifact can preserve functionality while failing scope. Their raw/normalized acceptance remains false. Independent ownership and semantic grading must preserve these failures; functional pass alone is not task acceptance.

Private evaluators run public/independent checks in their own temporary locations but do not invoke deliverable-generating task commands on the retained workspace. The four witness passes therefore verify retained artifacts rather than grader-created work. Command execution and other process claims still require participant trace evidence.

No treatment plan or candidate instruction was read for this review. The earlier disclosed reviewer exposure to unrelated agent summaries remains part of provenance. This report establishes grading mechanics, not candidate efficacy.
