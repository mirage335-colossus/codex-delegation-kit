# Development grading runner independent review

**Disposition:** approved as an evidence-collection runner. Semantic grading and overall task acceptance remain a separate independent step. No unresolved runner defect was found in the reviewed scope.

Reviewed source: `grade_development.py`, SHA-256 `f0134d226d9b39737ae6c27b1537cb898202730434ec47b4228df7bfc6ed52d4`. The file was untracked at review time. This review did not change the runner, candidate instructions, fixture source, installed kit, model settings, or treatment plan. No participant/model session was launched. Only this requested report and scratch artifacts under `/tmp/action-recovery-fixture-review/grading-review` were written.

## Scope and actual checks

The reviewer read the runner and verified that its canonical development evaluators and TASK inputs match the already accepted fixture versions. The runner invokes each actual `caseN/private/evaluate.py` with the copied participant directory supplied through `PYTHONPATH`, `PARTICIPANT_ROOT`, and the subprocess working directory. Original checks and the supported application command run against that same copy. It does not substitute a private reference result for the participant output.

The reviewer created synthetic collection records and workspace copies solely for these tests. Their settings/collection booleans are synthetic inputs to exercise logic; they are not evidence of an actual model runtime or resolved model settings. Controlled source variants used the previously validated fixture references.

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/action-recovery-fixture-review/grading-review/check_runner.py`. Nine synthetic runs produced the following observations:

| Input | Observation |
| --- | --- |
| Both original development baselines | Original checks run; independent functional outcome fails |
| Both validated reference repairs | All three checks pass; independent functional outcome passes |
| Corrected source plus changed original test file | Functionality passes; protected-file preservation is explicitly false |
| Post-collection source change | Final snapshot mismatch; evidence ineligible for comparison |
| Incorrect initial-source hash | Initial frozen-case mismatch; evidence ineligible for comparison |
| Owned execution not released | Ineligible; all functional checks remain unexecuted |
| Workspace symlink | Ineligible; isolated-copy evaluation held |

All canonical fixture bytes and grading source remained unchanged during these runs. Evaluation-copy integrity and completed-workspace preservation checks were also true for the ordinary baseline/reference cases. Check argv, environment, output and return codes are retained in the generated JSON reports, including the exact private evaluator path and digest.

A tenth synthetic reference case was run through the actual CLI:

```text
python3 -B studies/action-recovery-2026-11-09/grade_development.py r010 case2 --runs-root /tmp/action-recovery-fixture-review/grading-review/runs --output-root /tmp/action-recovery-fixture-review/grading-review/outputs --eval-root /tmp/action-recovery-fixture-review/grading-review/evaluation --timeout 2
```

The CLI exited 0, produced the expected report, passed the functional outcome, and reported all four evaluation-integrity checks true.

A tiny sleeping subprocess was terminated after the configured timeout and recorded as `timed_out=true`, return code `-9`. A deliberately missing test import produced a failed public-test check. Unittest reported one loader error test, but no actual test assertions ran. The runner accurately labels its parsed number `reported_tests_run` and leaves `assertion_count` unknown rather than equating a test or exit status with assertions. These two process-check records are in `process-checks.json`.

## Acceptance semantics and limits

`eligible_for_comparison` describes usable study evidence, not successful task acceptance. A participant's protected-file violation can be valid evidence of failure. The protected-file hash comparison, observed edit list and pending preservation grade must be considered even when `independent_functional_outcome` is `passed`. The grading owner confirmed that changed original tests, inputs or other protected files will fail preservation and overall acceptance in the six-dimension grading step. Likewise, a functional observation attached to an ineligible snapshot must not be treated as a valid comparative result.

The runner records source changes and scratch changes separately, compares protected hashes with the canonical input, compares the collected final snapshot with the observed workspace, and checks that evaluation left the completed workspace and evaluator bytes unchanged. These are evidence checks over a trusted runner collection; they do not authenticate collection authorship or provide an OS security boundary. No such enforcement was claimed.

Command/result fields and source diffs remain necessary evidence for semantic grading. They exclude the explicit treatment map and raw backend event stream, but participant text could indirectly suggest a treatment; this is treatment-label blinding, not a guarantee that a grader cannot infer an arm. The reviewer did not inspect the treatment plan or candidate files for this assignment. The earlier preflight review's disclosed exposure to unrelated agent summaries remains part of reviewer provenance and is not erased by this narrower assignment.

No participant results were graded here. No efficacy claim or model-setting verification follows from these controlled runner tests. Remaining study work is the independent semantic/ownership grading of actual released participant runs, as already planned.
