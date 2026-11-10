# Setup and smoke run history

## Setup-only attempts

Runs `d001` through `d008` completed and were collected, but made no source
changes. Each collection reports an empty patch (SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). Their
worker results are `blocked`: the command scope allowed acceptance commands,
but did not allow reading `TASK.md`, workspace notes, or source, so the task
objective and acceptance conditions could not be established. Some runs report
acceptance commands passing; those results do not establish task acceptance.

The prior coordinator summary classifies these eight runs as setup failures and
notes that some attempts incorrectly re-entered the Astra initial-review step.
The lifecycle records do not identify which individual IDs had that review
issue. These runs are retained for audit and excluded from behavioral failure
and success counts.

Raw run IDs: `d001`, `d002`, `d003`, `d004`, `d005`, `d006`, `d007`, `d008`.
Per-run lifecycle records are in `results/d00N-lifecycle.json`; the safely
filtered evidence is in `results/runs/<run-id>/`.

## Runtime smoke

`smoke-runtime-03` is the completed runtime smoke. The initial permitted test
failed because `answer.answer()` returned 41 instead of 42. The run changed
only `answer.py`; the same permitted unittest command then passed. The collected
result records one changed file and a 93-byte patch. Independent patch review
was still pending when the run was collected, so this is a smoke result rather
than an independently reviewed acceptance result. Its raw ID and filtered
artifacts are preserved in `results/runs/smoke-runtime-03/`.

`HARNESS.md` describes the harness and its earlier setup constraints. This
file records the observed run history; it does not treat successful setup
commands as evidence that a behavioral objective was met.

## App-server response deadline batch

The completed runs `d101`, `d104`, `d103`, and `d106` were collected with a
hold: the app-server response deadline expired, settings were not verified,
and the actual patch was empty. These are setup/handshake outcomes, not model
quality failures or successes. Their requested configuration records Luna at
high effort, but `settings_verified: false` means those settings were not
confirmed as effective for these runs.

The completed runs `d102` and `d107` report completed model turns with settings
verified. Their patches and collected actions are preserved in their run
archives. Both collection records say controller validation is still required;
their completion does not by itself establish acceptance.

| Run ID | Collection | Settings verified | Actual patch SHA-256 |
| --- | --- | --- | --- |
| `d101` | hold; app-server response deadline expired | false | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `d104` | hold; app-server response deadline expired | false | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `d103` | hold; app-server response deadline expired | false | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `d106` | hold; app-server response deadline expired | false | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `d102` | completed; controller validation required | true | `92d6c7770e2f0b04ce791970f50846bc713ab2f8a76c0b0f557822a807c29267` |
| `d107` | completed; controller validation required | true | `12f6215b5a5b910315a739103ca7264053d6a7587019a366d2e98b17cf67924f` |

The no-turn handshake probe is preserved as `results/handshake-probe-01.json`.
It reports initialize at 15.618 seconds, config read at 0.010 seconds, and
thread start at 0.672 seconds; the sequence is marked verified, the process was
reaped, and no model turn started. Its source is `d101b`. The probe supports a
startup-contention hypothesis, but does not locate the earlier response
timeouts definitively.

The coordinator reports that `run_batch.py` now permits at most two concurrent
turns and serializes only the handshake with `setup_lock`; model, settings,
deadline, and frozen v2 source were not changed. At the time of that update,
`d101b`, `d104b`, `d105`, and `d108` were still running. `d101b` and `d104b`
were replacement pre-turn runs. They completed later and are archived under
their run IDs.

The filtered archives for the six completed runs are in
`results/runs/d101/`, `d104/`, `d103/`, `d106/`, `d102/`, and `d107/`.

## Corrected eight-run development batch

All eight valid development runs have now completed and their filtered
archives are preserved under `results/runs/`: `d101b`, `d102`, `d103b`,
`d104b`, `d105`, `d106b`, `d107`, and `d108`. The `b` runs replace planned
runs `d101`, `d103`, `d104`, and `d106` after those runs hit pre-turn setup
timeouts. Across the eight valid runs, settings were verified and the frozen
primary public/private evaluations passed. These counts do not subsume the
separate semantic judgments or supplemental contract checks recorded in
`blind-grades/development-eight-blind-summary.json` and
`blind-grades/all-case2-classification-boundaries.json`.

All eight valid runs achieved primary objective recovery (4/4 per condition).
The distinct full assignment acceptance assessment is 5/8: v2 2/4 and baseline
3/4. All four case2 runs met the frozen primary outcome. The matched
post-review boundary check finds that v2 patches `d101b`
and `d103b` regress some previously valid rows with blank optional metadata;
baseline patch `d104b` preserves all compared variants. The baseline patch
`d106b` also fails the blank-field variants. These supplemental failures are
kept distinct from the frozen primary evaluator passes; they are not recast as
held-out outcomes. The small development sample supports no causal comparison.

At the coordinator update when this section was first written, adaptive
parallel reviews `r001` and `r002` were still pending and the fresh cases were
prepared but unlaunched. That was a historical status, later superseded below.

## Review, repair, and arbitration updates

Adaptive reviewers `r001` and `r002` received the task, source and candidate patch
without the grader's known counterexample. They independently generated regression
evidence; their reports and examples were then supplied to the p-stage repair actors.
The reviews are not counted as repair attempts. All three p-stage actors fixed
the reported examples but failed additional nonblank-metadata probes.

The first bounded repair stage used v2 in `p001`, `p002`, and `p003`. All three
fixed the reported blank-value examples, then failed probes for nonblank but
unused metadata. The next matched stage used v3: one of three runs met the full
user contract (`q001`); `q002` and `q003` failed. No new
counterexamples were provided during the q stage. Per-run safe artifacts are
preserved under `results/runs/`; probe summaries are under `blind-grades/`.

Helper runs `c001` and `c002` were sealed before current-patch exposure, as
recorded in `contract-helper-seal.json`. `c001` and branch check `z001` missed
the residual branch. The sealed-original-source `c002` probe did not find the
nonblank-metadata case. After reveal, `z002` independently executed the new
nonblank-metadata counterexample. Astra's arbitration in
`strong-arbitration.txt` validated canonical-first handling: preserve a row's
canonical interpretation whenever the existing canonical validator accepts
it, regardless of unrelated metadata; otherwise route it through the vendor
adapter and its validation. Canonical key presence alone is not enough to
classify vendor rows.

The current v3 source snapshot adds a generic underlying-rule/contract and
materially-different-counterexample instruction, and fixes the controller
dead-end where explicit contradictory completion was terminally invalid.
`versions/v3/manifest.json` is the current common source cue; the coordinator
reports no further backend changes planned. A focused independent review found
no controller blockers. The current controller test receipt reports 313 tests
passing and `git diff --check` passing; its recorded file is a transcription
of the quiet command result, not raw saved stdout. Queued dispatch remains
limited.

At the time of the earlier update, strong-ownership runs `x001` and `x002` and
the 16 fresh runs had not completed; that status is superseded by the final
run-status section below. The private frozen oracle's raw-vendor-receive
requirement is stronger than `TASK.md`; its score stays separate from the
user-visible contract, which is applied consistently to initial and repair
runs. None of these updates is a final workflow freeze or held-out result.

## Final run and release status update

The updates above preserve the state at the time they were recorded. Subsequent
work completed strong-ownership runs `x001` and `x002`; both received full
semantic acceptance. The full v4 fresh batch `g001`–`g016` is also complete and
archived. The sealed fresh summary records 16/16 functional/control,
priority/action, and scope/original-check passes; required action recovery was
8/8, hard-boundary controls 4/4, and already-satisfied controls 4/4. First-pass
owner handoffs were complete in 13/16. `g003`, `g004`, and `g015` omitted the
explicit artifact path. After sealing, the coordinator completed ordinary
handoff from verified paths and hashes, with no additional model calls or
actor-workspace writes. Those initial omissions remain in the record.

Raw fresh evaluators exited nonzero only because the pre-existing runtime
scratch lock was empty. The declared isolated-copy normalization removed that
empty lock; all 16 normalized evaluations passed, with no other observed scope
violations. The actual whitelisted task products are archived with file hashes
and source mtimes. Initial replay records used evaluator arguments pointing to
the original grader workspace and are retained only as preliminary rechecks,
not replay proof. A fresh replay from frozen participant snapshots and archived
products is being independently validated; see
`results/archive-replay-validation.json` when available.

Correction to the earlier helper summary: `c001` and `z001` missed the residual
branch. The sealed-original-source `c002` probe did not discover the
nonblank-metadata case. After reveal, `z002` independently executed the new
nonblank-metadata counterexample. This distinction is also in the current
report and run archive.

The controller's transcribed full test receipt records 313 tests and
`git diff --check` passing. A concrete global install preview was prepared, but
automatic approval review rejected the apply operation before process start:
explicit authorization is required for persistent global installation.
Configuration and gateway remained unchanged, and no alternate path was
attempted. Source validation and [Astra completion review](completion-review.md)
are complete. Global installation remains pending explicit authorization.
The `h/f` predecessor plans for the same four fresh cases were never launched;
the final `g` plan supplied the 16 executed fresh runs.


## Durable archive replay validation

The independent archive reconstruction in `results/archive-replay-validation.json`
passed 16/16. Each replay copied its base from the durable frozen
`cases/heldout/CASE/participant` fixture, verified all frozen base hashes and
mtimes, and overlaid only the manifest-listed archived task products after
hash, size, and mtime checks. Evaluator arguments targeted the new workspace;
no original actor workspace or prior grader workspace was used. The evaluator
accepted each reconstructed workspace, and fixture/product bytes and mtimes
were unchanged after evaluation. This validates retained product replay for
functional/control checks; it does not reproduce actor inference or the
original owner-handoff reporting step. Earlier per-run replay records remain
marked preliminary because their arguments pointed into an original grader
workspace.
