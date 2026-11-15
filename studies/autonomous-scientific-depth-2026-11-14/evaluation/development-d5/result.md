> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# D5 final result

**D5 failed the full scientific bar: all eight domains are Partial.** The
[validated aggregate](aggregate-dispositions.json) contains **35 Supported,
11 Supported boundary, 40 Partial, one Unsupported and two Outside declared
conditions** across 89 rows. Of 48 depth checks, **23 are Supported, zero are
Supported boundary and 25 are Partial**. Thus 23 checks are satisfied; none of that
count comes from a boundary disposition. Internal scientific acceptance and
engineering uptake did not establish the independent frozen comparison.

Eight fresh Sol evaluators completed their post-lock reviews. The aggregate
validates every expected domain, row and depth ID, reports `complete` with no
errors, and preserves each review's SHA-256. Each author's overall judgment is
Partial, while separately derived readiness is false for every domain and for
the episode. Counts summarize labels; they are not averaged scores or substitute
thresholds.

| Domain / final review | Supported | Supported boundary | Partial | Unsupported | Outside | Depth S / B / P | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [VLF](reviews/vlf/review.md) | 1 | 2 | 8 | 0 | 0 | 2 / 0 / 4 | Partial |
| [GROUND](reviews/ground/review.md) | 3 | 1 | 7 | 0 | 0 | 1 / 0 / 5 | Partial |
| [HF](reviews/hf/review.md) | 4 | 1 | 5 | 1 | 0 | 3 / 0 / 3 | Partial |
| [EME](reviews/eme/review.md) | 5 | 2 | 5 | 0 | 0 | 3 / 0 / 3 | Partial |
| [NOISE](reviews/noise/review.md) | 4 | 2 | 5 | 0 | 0 | 2 / 0 / 4 | Partial |
| [RX](reviews/receiver/review.md) | 6 | 0 | 4 | 0 | 1 | 3 / 0 / 3 | Partial |
| VALID (historical locator: `reviews/validation/review.md`; artifact not bundled) | 5 | 1 | 4 | 0 | 1 | 4 / 0 / 2 | Partial |
| [NATIVE](reviews/native/review.md) | 7 | 2 | 2 | 0 | 0 | 5 / 0 / 1 | Partial |
| **Total** | **35** | **11** | **40** | **1** | **2** | **23 / 0 / 25** | **Eight Partial** |

In the depth column, S = Supported, B = Supported boundary and P = Partial.
The two conditional Outside rows are RX-11 and VALID-08. Each linked report
retains its evidence, limits and individual dispositions. Reproduction artifacts
include the VLF checks (historical locator: `reviews/vlf/reproduced-checks.txt`; artifact not bundled),
GROUND results (historical locator: `reviews/ground/reproduced-ground-results.csv`; artifact not bundled),
HF checks (historical locator: `reviews/hf/check-output.txt`; artifact not bundled) and
NATIVE reproduction receipt (historical locator: `reviews/native/checks/reproduction.json`; artifact not bundled); the
reports link additional checks. Original initial inquiry accounts, the interim
Partial scientific review, failed attempts, withdrawn estimates and subsequent
corrections remain preserved. No closed author artifact was repaired for credit.

The [final integrity review](integrity-review.md) supports owner-led delivery and
general author-side integrity on the recorded evidence, **with a bounded breach
of scientific-review input separation at S3**. The later critic received an
architecture-derived future fixture suggestion through a factual source
correction. The audit found no evidence that the selected architecture, whole
plan or prior approval was supplied, or that root provided scientific repair.
It supports independent initial scoping and final adjudication with that
specific disclosed suggestion; causal non-use of the suggestion cannot be
verified. Complete input separation is therefore not claimed.

D5 used the frozen V5 treatment (historical locator: `freeze.json`; artifact not bundled) and the unchanged ordinary repeat
task. The owner `/root/t82_owner` first sent a native message explicitly stating
completion with no requested dependency; root immediately froze the submission,
before the subsequent final message. The accepted
owner artifact (historical locator: `submission/work/owner.md`; artifact not bundled) has SHA-256
`5714182c36cc7c4c1df1b175e329c4939d1301f2b29e799d588fa328afe040db`.
No subsequent author correction receives credit.

| Locked evidence | Verified value |
| --- | --- |
| Prospective freeze | 2026-11-15T00:34:32.681514+00:00 |
| Lock started | 2026-11-15T01:26:02.505717+00:00 |
| Lock completed | 2026-11-15T01:26:03.139400+00:00 |
| Freeze to completed lock | 3,090.457886 seconds (51 minutes 30.457886 seconds) |
| Archive entries / regular files | 628 / 593 |
| Regular-file bytes | 19,653,831 |
| Initial inputs preserved | 373 / 373 hashes |
| Project source files | 362 initial + six exact dependencies = 368 |
| Author web accounting | 337 charged items / 117 returned receipts, reconciled |
| Author helper assignments | Six recorded |
| Browser / other acquisitions | 14 recorded actions / zero other acquisitions reported |

The lock (historical locator: `lock.json`; artifact not bundled) is clean, reports stable source during its checks and an
archive matching the packet. Independent rehashing of all archived entries
matches its manifest:
`33f3408f1885fe17756a88f1e571d0d2418ab34c47a4575694c1b3d788583db4`.
All initial inputs and all six exact dependencies match their recorded hashes.
DEP-1 (historical locator: `dep1.json`; artifact not bundled), DEP-2 (historical locator: `dep2.json`; artifact not bundled) and DEP-3 (historical locator: `dep3.json`; artifact not bundled) preserve the requested
paths and frozen-commit provenance, including the initially missing underscore
path and the owner's later exact hyphenated-path request. Source context was
expanded through these requests; original input bytes were unchanged. Compact
machine-readable figures and evidence hashes are in
evidence-totals.json (historical locator: `evidence-totals.json`; artifact not bundled).

Author web accounting has no missing, unclosed or unlisted receipts and no
reported discrepancies. Browser records (historical locator: `browser-acquisitions.jsonl`; artifact not bundled) total 14
actions. These counts describe cooperative accounting, not complete interception
of tool use. A clean byte freeze alone does not establish termination or exclude
all transient concurrent changes.

Final evaluator accounting (historical locator: `evaluator-accounting.json`; artifact not bundled) reconciles **215 of 400
web items in 48 returned receipts**, with no missing, unclosed or unlisted
receipts and no discrepancies. Per-domain web use is VLF 32, GROUND 22, HF 50,
EME 19, NOISE 36, RX 31, VALID 15 and NATIVE 10. Evaluators reported zero browser
and zero other acquisitions. The archive helper took a snapshot of the absolute
evaluator-access path before reconciliation and a second snapshot afterward;
entries and observed filesystem state were stable. Evaluator work is separate
from the locked authors' 337 items and 117 returned receipts.

The preserved V5 source and validation record (historical locator: `../source-v5/manifest.json`; artifact not bundled)
remains unchanged: all 25 preserved source/test files match current hashes,
including the 13 source/role hashes in D5's freeze; the runtime inventory remains
23 files. The recorded 313-test validation in 66.083 seconds establishes source
wiring and preservation, not a scientific outcome or product performance.

D5 is a development delegated-owner component test outside confirmation. It
reuses the parent consultation and exempts recursive main-chat initial and
completion gates. A full primary-lifecycle harness is being implemented
separately, with no setup or behavioral episode yet. Neither full-lifecycle
success nor failure follows from these component outcomes. No confirmation has
launched, and these coverage counts establish no reliability rate, isolated
wording effect or product performance. Broader process diagnosis is deferred to
the separate blind strategic review.
