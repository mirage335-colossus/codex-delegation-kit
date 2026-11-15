# Research continuity and artifact storage

The implementation changes following the autonomous research exercises address
two operational failures: losing useful findings from a continuation's context,
and placing acquired originals among authored knowledge. They do not reopen the
exercise campaign or establish reference-level scientific depth or reliability.

## Preserve knowledge when execution stops

The shipped controller already holds an affected task while allowing independent
ready tasks to continue. Its explicit resolution path keeps the original task,
deadline, accumulated service and hold history; execution must be released before
continuation. Research recovery builds on those mechanisms rather than introducing
automatic retries or a second scheduler.

The backend retains a bounded checkpoint of public messages, including incomplete
public text where available. It marks these observations unaccepted, records
omissions, and retains the original operation, thread, turn and event locations.
Guard cleanup attempts the supported interruption protocol within a short bound;
an acknowledgement does not establish cancellation or descendant release.
Authorized continuations receive the preserved findings and resolution evidence.
Neither storage nor continuation turns a tool-start event into proof of delivery,
an interrupted claim into an accepted result, or a closed exercise into a pass.

The completion review found an additional composed failure: a new storage
refusal after the controller recorded launch intent, but before any process was
launched, was classified as uncertain forever. The adapter now fences a proven
prelaunch refusal under its operation lock with a durable metadata-only receipt.
The controller can hold and later explicitly resolve that known-not-launched
attempt. Existing uncertain operations and failures to persist the refusal remain
held; correcting an ignore rule never silently replays the same operation.
After a controller restart, the receipt reconstructs that same hold. A separate
storage-hold marker covers a runner that started but refused capture before
launching its command; this requires verified runner release and is not described
as a runner that never launched. These markers are matched to the original
launch intent before they can release an attempt.

Native research agents also need incremental authored accounts: explanations,
citations, actual source access, completed checks, contradictions and unresolved
questions. Runtime checkpoints cannot preserve findings an agent never emitted.
The backend's bounded public-text handoff supplements retained artifacts; it does
not archive all provider state or promise survival of every abrupt host failure.
Do not put hidden reasoning, secrets or copied source bodies in a handoff.

The old study collector is retained as non-executable reference text. Its broad
guard stop is not the shipped controller's task-scoped behavior. The new recovery
checks use synthetic protocol events and local processes, not another live model
or scientific research campaign.

## Keep acquired originals outside authored accounts

The exclusion checks follow [Git's ignore semantics](https://git-scm.com/docs/gitignore)
and [the `check-ignore` interface](https://git-scm.com/docs/git-check-ignore).
Index tracking and effective exclusion are checked separately: ignoring a path
does not remove it from the index.

`research/` holds authored, high-density scientific knowledge and useful authored
checks, with citations and provenance. `_ref/` and `_appraisal/` remain user-curated
and read-only without explicit curation instructions. Papers, datasets, copied
third-party source, extracted text and raw responses belong in authorized external
scratch or a separate narrow cache. This checkout supplies `/.research-artifacts/`
in its `.gitignore`; that rule is not automatically installed into other projects.

`engineering.validate_artifact_paths()` checks concrete paths before raw writes:
they must be untracked and effectively excluded by an enclosing repository's own
`.gitignore`. Global excludes and `.git/info/exclude` alone are insufficient.
Negation, symlink traversal, Git metadata, tracked destinations and authored or
curated research subtrees are rejected. Staging, temporary and final destinations
need admission; an ignored-looking directory name is insufficient. Authorized
external scratch remains available. Admission does not grant filesystem or network
authority, and it is not a sandbox against concurrent path or ignore-rule changes.
The backend's configured `runtime-state/` and `runtime-logs/` destinations require
whole-directory exclusion, including rejection of tracked descendants. This covers
those configured output trees without claiming interception of every provider
write elsewhere.

Cancellation and access to existing controller state must remain possible if an
ignore rule changes after a run starts. Preserve existing evidence and stop new
inadmissible captures; never delete research or strand an owned process merely
to satisfy an admission check. Native tools and arbitrary agent shell commands
are governed by the corresponding prompt instructions, not intercepted by this
Python helper.

The retained relay helper checks supplied response/dependency staging and final
payload destinations before publication mutates its accounting or copies bytes.
A refusal leaves caller-supplied inputs and the existing acquisition reservation
intact. It does not refund acquisition cost or authorize another acquisition.
Late results still remain private after author closure; they do not alter the
closed author's outcome.

## Existing material and further improvement

The storage audit identified eighteen already-tracked acquired originals in the
earlier scientific-depth study: ten files under
`studies/scientific-depth-2026-11-14/research/groundwave/tmp/LFMF/` (the upstream
license, header and source files), and eight under
`studies/scientific-depth-2026-11-14/research/hf-reference/scratch/` (reference
source and data). Their existing acquisition logs and source ledger identify the
provenance. They remain unchanged. Ignore rules do not untrack existing files;
migration requires a deliberate retention decision and updating dependent authored
checks and locators. This bounded audit is not a repository-wide classification
or redistribution assessment.

Future improvements should begin with the existing failure evidence and these
offline regressions. Assess recovery, actual uptake and storage admission
separately from scientific adequacy. Do not respond to another interrupted author
by discarding retained knowledge, resetting budgets, changing models, bypassing a
denial, or restarting an expensive campaign.

## Validation

On 2026-11-15, `python3 -B -m unittest discover -s tests` passed all **357**
repository tests in 105.488 seconds, after the initial prelaunch-refusal fix and
before the final restart/runner observation-path refinement. The retained
autonomous-study helper suite passed **14** tests separately. These are offline
synthetic protocol, local process, Git, controller and installation-compatibility
checks, not fresh model research or evidence of reference-level scientific
adequacy. The final observation-path refinement is checked with the complete
affected controller and execution suites rather than another unrelated full run.
Both affected suites passed: **45 controller tests** in 36.906 seconds and
**14 execution tests** in 4.224 seconds, including the restart and runner-guard
regressions. A final invalid-receipt hardening change then removed unverified
timestamps from accounting; its restart regression passed again in 0.246 seconds,
including malformed and nonfinite times, preserved raw receipts and no false
release. The final 24-file runtime identity is
`d78a6eab4463869c2b1d56b3f0d0064d9218c719f4783fd321f4bf3ad1ab503d`
(SHA-256 of the sorted filename-to-SHA-256 map serialized with Python's
`json.dumps(..., sort_keys=True)` defaults).

New regressions demonstrate retained public findings and incomplete output after
a guard; continuation under unchanged limits; a second setup failure preserving
earlier useful research; independent-task progress with dependent work held;
cancellation collection; and orderly cleanup even when a later checkpoint is
denied. Storage tests cover ignored, unignored, negated and tracked destinations,
global-only exclusions, linked and nested repositories, concrete temporary files,
provider output trees, and retained evidence after publication failure. The relay
checks include late private retention and unchanged inputs/reservations on refusal.
Whitespace checks passed. Model pins, installer inventory and global installation
were not changed.
