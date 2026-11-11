# Autonomous practical numerical engineering — November 11, 2026

**Four prospectively frozen owner → independent reviewer → owner repair workflows
passed both numerical acceptance review and frozen product checks, across two
new native application families, without corrective user intervention.** The
coordinator supplied generic packets and relayed the reviewers' full findings;
it gave no case-specific engineering advice or source repairs in these workflows.
These were executable C++ implementations, not answers choosing supplied timings.

| Fresh workflow | Independent finding and owner repair | Repair rounds | Final result |
| --- | --- | ---: | --- |
| Curve processing, w11 | Removed unnecessary cutoff recalculation; corrected live-array and reserved-table reports | 2 | Review + product checks passed |
| Curve processing, w21 | Used FP32 squared-value products with justified FP64 totals | 1 | Review + product checks passed |
| Rational resampling, w12 | Used FP32 sample scaling and interpolation; retained exact integer phase and FP64 audit | 1 | Review + product checks passed; scope exception |
| Rational resampling, w22 | Independently found and repaired the same local scaling issue | 1 | Review + product checks passed; scope exception |

The strongest supported result is **autonomous multi-agent development**, not
flawless one-shot prompting or universal correctness. All four initial proposals
already passed product checks, but all four required numerical or evidence
repairs. Earlier prompt revisions were exercised in **29 initial implementation
runs**, with misses retained below. Two final owners listed repository filenames
outside their assignments; one also attempted prohibited Git inspection. Numerical
acceptance does not erase those scope violations.

Reusable deliverables: [owner guidance](prompt-v6.txt), [generic reviewer packet](review-packet-v1.txt),
[frozen workflow](workflow-protocol-v1.md), and [results with stage evidence](workflow-outcomes.json).
The complete refinement history follows; earlier waves are not the final endpoint.

This follows the request: “Please do exercises to refine this to the point of
actually demonstrating generic correct behavior without user intervention.”
The [earlier study](../practical-precision-2026-11-11/README.md) remains unchanged.
Its cued comparison and post hoc selector diagnostic did not establish this
implementation result.

## Refinement from an observed failure mode

The existing delivered [compact reminder](prompt-v1.txt) was first exercised on
three development applications. All three passed their frozen product gates.
However, the burst worker, d01, rebuilt exact reference-valued inputs inside
each batch row to restore discarded rounding digits. It achieved a smaller
memory footprint, but paid repeatedly for preparation and FP64-equivalent
agreement beyond the application's output requirement.

The [revised reminder](prompt-v2.txt) adds a general rule:

> If a compact path misses a quality requirement, isolate the failing operations
> and try local widening first. Use the available resource budget to reuse
> preparation and maximize useful default-path capacity. Compare the default end
> to end on a demanding workload, including preparation and conversions. Require
> a practical benefit before paying for tighter reference agreement or reducing
> resource use at the expense of capacity.

A fresh worker, d04, received the same starter and revised reminder, without the
previous answer or a task-specific hint. It used compact inputs, a wider local
accumulator, reusable preparation and bounded chunks. Both d01 and d04 passed
all nine frozen product checks; the throughput comparison is a separately
identified development diagnostic, not a retroactive failure of d01's checks.

Four serialized, interleaved repetitions of the actual automatic/default route
used identical compilation flags and the same 5×5,000,000 workload. Whole-process
time includes preparation, allocation, processing and output:

| Implementation | Median total time | Measured live heap | Quality |
| --- | ---: | ---: | --- |
| d01, original reminder | 0.6606 s | 8,388,648 B | Passed |
| d04, revised reminder | 0.1446 s | 40,000,040 B | Passed |
| Independently prepared witness | 0.1381 s | 40,000,040 B | Passed |

d04 was **4.57× faster than d01** at this shape while staying within the 64 MiB
buffer budget and the same output tolerance. This directly exercises using
available memory for useful processing instead of buying unnecessary reference
agreement. It does not establish a general causal prompt-effect estimate from
one pair. The witness's full-buffer implementation has a narrower memory-valid
range than d04's chunks; no universal witness dominance is claimed.

[Raw matched measurements](burst-comparison.json), [comparison code](compare_burst.py),
and each development run's submitted source, patch, evaluator result and available
native history are retained under `runs/d01` through `runs/d04`.

## Frozen transfer results

After development, the candidate was frozen. Three independent fixture authors
had prepared the six transfer families; their correctness and feasibility were
reviewed before participant dispatch. Two new workers per family received only
an ordinary product task, the exact revised reminder, source and public tools.
They did not receive witness implementations, private checks, another worker's
answer, benchmark rankings or corrective messages.

| Family | Runs | Frozen product result | Source-confirmed behavior |
| --- | --- | --- | --- |
| Heat-field simulation | f15, f21 | 2/2 | FP32 bulk fields; full-output checks and actual heap below 5 MiB |
| Multichannel filtering | f12, f24 | 2/2 | Compact storage, wider products/accumulation, preserved double audit override |
| Repeated material trials | f11, f22 | 2/2 | Reused shared affine recurrence; retained all trial/step contributions and uint64 seed behavior |
| Coordinate measurement | f14, f25 | 2/2 | Frame-local evaluation, no large absolute-coordinate array, exact integer tick moments before rendering |
| Scripted scene processing | f16, f23 | 2/2 | First heavy frame and transitions under the memory cap; all frame outputs and diagnostic overrides retained |
| CPU feature processing | f13, f26 | 2/2 | Reachable guarded AVX2 FP32 computation, scalar tails, FP64 totals, truthful format/backend reporting and portable fallback |

The six families cover several mechanisms, not six wholly independent statistical
samples: heat and filtering share a compact-storage pattern. The scene solutions
differed legitimately. f16 fused FP64 rendering and reduction and left an unused
reserved FP32 buffer; it is not evidence of FP32 image computation. f23 used
FP32 pixel arithmetic and FP64 frame totals. Its extra runtime versus an uncapped
double route is not a failed product gate: that double route exceeds the required
buffer cap. No general scene-speed claim is made.

Every final patch passed a fresh, serialized evaluator compile and execution
after worker activity completed, including all protected-file audits. All twelve
changed actual production source. A Sol reviewer inspected the critical code
and initially accepted the implementations against the product contracts. The
completion review narrowed that acceptance after the FIR discriminator below.
[Outcomes](outcomes.json)
and the [frozen plan](final-plan.json) retain the original denominator and scope
status. Each `runs/<id>/evaluation.json` contains commands, output and failures;
`submitted/core.cpp` and `patch.diff` preserve the actual submission.

## Evidence strength and limitations

The [protocol](protocol.md) was set before participants. Fixtures were preflighted
against failing starters and passing witnesses. Private checks use varied shapes,
full-output aggregates or complete output comparisons, extreme coordinates,
large integer seeds, overrides, first-heavy/transition workloads, odd SIMD tails
and a production-sized denied-feature fallback. Output and timing gates derive
from public fixture contracts; those tolerances are not general engineering rules.

Memory is cross-checked independently through injected C++ allocation probes or
fresh process RSS measurement, not accepted from a worker's printed byte count.
Understated-memory, omitted-tail/detail, zero-output and reduced-work controls
were rejected for the intended reasons. Instruction inspection supports a
reachable guarded CPU path; a whole-binary mnemonic search alone is diagnostic.
The deny mask tests fallback on this host, not physical qualification of another
CPU. No GPU execution is claimed.

The host was the available Ryzen 5 PRO 5650U with GCC. Native role requests pinned
Luna/high, but effective model/effort and token/allowance telemetry were not
independently observed. Each run had at most 30 allowed tool invocations and
15 minutes; retained command/patch events and turn durations are in `outcomes.json`.
There were no corrective coordinator replies or user tuning interventions.
Progress messages to the coordinator did not receive implementation advice.
Compiler/public-test errors and autonomous repairs remain in the histories.

The exact compact reminder was manually supplied once alongside the existing
installed role, which lacked it. Surrounding role/app instructions may also
influence results. This is an absolute autonomous transfer demonstration on the
tested applications, not a clean old-policy causal comparison, universal
correctness proof, production modem benchmark or cross-model reliability study.
Task-level read scopes and separate directories were not OS-enforced blinding.
The native history capture retains available non-reasoning events, bounded to
20,000 characters per item; source and grader outputs are separately archived.

## Scope and setup exceptions remain visible

The original protocol sought an entirely clean execution matrix. That broader
endpoint was not met, although all frozen product checks passed.
Do not quietly substitute a smaller denominator or label every run compliant.

- The scene/dispatch task examples explicitly supplied absolute `/tmp` build
  paths, while the common packet restricted new scratch files to the assigned
  directory. f16, f23 and f26 used such paths; this is a fixture instruction
  conflict. Fresh grader recompiles establish the code's result independently
  of any worker-side binary collision. f13 used an in-directory build.
- f24 created two out-of-directory scratch executables and attempted the
  explicitly prohibited, non-mutating `git diff`; there was no corresponding
  task example authorizing these actions. This is a worker protocol deviation.
  It does not erase its passing numerical result or imply perfect workflow
  compliance. The original command evidence and self-report are retained.
- Several workers repaired ordinary setup/check errors autonomously, including
  unavailable Boost headers and `/usr/bin/time`, a non-executable script invoked
  correctly through Python, and mistakes in their own comparison scripts.
  Zero-assertion setup attempts are not reported as passing checks.

Independent review found no numerical prompt revision indicated by those
scope-only events. The separate arithmetic-choice miss did require refinement.
A claim of clean workflow compliance would need
consistent build instructions and fresh prospective exercises. That is distinct
from the requested numerical tradeoff behavior demonstrated here.

Fixture authoring also had pre-participant defects: fixed samples insufficient
to detect omitted work, trusted memory metadata, weak override tests and
incorrect arithmetic labels. Review corrected them before affected scored runs;
earlier preflight files and `private/pre-review` snapshots are retained. The
current failing-start/passing-witness and deliberate-control records are in
each frozen case's private directory. These repairs are not participant success.

## Completion review exposed a second numerical failure

f12 and f24 retained FP64 products and accumulation without testing a credible
narrower implementation. f12's stated reason was retaining precision. This was
not sufficient for the user's objective even though the product gates passed.

The coordinator's [post-holdout FIR discriminator](fir-diagnostic/results.json)
compared the exact submitted sources with FP32 products/wide sums and FP32
products/sums. All six variants passed the unchanged quality, memory and double
override checks. Seven serialized interleaved repetitions of the production shape
gave O2 medians of 31.55 to 28.99 ms for f12 and 30.94 to 28.91 ms for f24 when
narrowing hot arithmetic. Under native O3, FP32 products with FP64 sums were
fastest. This is a useful build-dependent choice, not a universal dtype ranking.

Both original runs are therefore **product passes with numerical-objective
misses**. These coordinator tests do not count as autonomous success. The required
next wave uses [prompt v3](prompt-v3.txt) and the [prospective v3 protocol](protocol-v3.md):
a fresh FIR development regression and two fresh workers on each of three new
families, with numerical decision behavior reviewed separately from output gates.

## The third reminder exposed unnecessary numerical machinery

d05, a fresh FIR regression, implemented FP32 products and sums and passed the
production quality, storage and strict double-override checks. It did not measure
runtime, so this establishes the specific arithmetic correction rather than a
speed ranking. The reviewed result is in [development-v3.json](development-v3.json).

The v3 transfer wave stopped after two of six planned runs. Both metrology
implementations passed their product gates, but g12 introduced compensated FP64
reductions without showing a need and repeated an invariant cycle for every
block. g22 independently computed the cycle once and accounted for all blocks.
The remaining four workers were never dispatched; their fixture families stayed
untouched. [v3 outcomes](outcomes-v3.json) preserve the planned denominator and
the one behavioral miss.

A [separate diagnostic](metrology-diagnostic/results.json) found all four versions
qualified against the same frozen output/memory requirements. Seven interleaved
production measurements gave 40.92 ms for g12, 24.25 ms for plain wide sums,
25.79 ms for narrower products with wide sums, and 1.60 ms for g22's reused cycle.
Here, narrower multiplication did not win: removing unnecessary compensation and
repeated work mattered more. These coordinator measurements do not count as
autonomous actions by g12.

[Prompt v4](prompt-v4.txt) adds one general closing rule: inspect dominant work and
justify added numerical machinery against the simplest sufficient computation.
A fresh regression, d06, independently removed the repeated cycle, retained only
small local wide reductions and passed all eight frozen product checks. The
[v4 protocol](protocol-v4.md) freezes three decisions—sufficient arithmetic,
necessary work and a qualified useful default—and expressly excludes a demand
for every conceivable micro-optimization. The [v4 plan](final-plan-v4.json)
preserves the intended new transfer denominator.

Four of the six planned v4 workers ran; [all four passed the frozen product
checks](outcomes-v4.json). Both pixel agents fused the full pipeline and used
FP32 scoring with a preserved double audit. h13 implemented and qualified FP32
FFT arithmetic. h23 implemented a much faster FP64 FFT but did not qualify its
replacement algorithm's arithmetic width. h11 also made a prohibited read-only
Git inspection, retained as a separate scope deviation.

The [matched spectral diagnostic](spectral-diagnostic/results.json) qualified
both h23's submitted implementation and an otherwise matching FP32 transform.
The first eleven alternating measurements were noisy. One [bounded clarification](spectral-diagnostic/clarification.json)
used 25 balanced paired groups of three cold requests per type, with stable full
output hashes across all 75 requests per type. FP32's whole-request mean was
25.476 ms versus 26.096 ms, winning 19 groups; paired mean difference was 0.620 ms
with 1.305 ms sample standard deviation. The internal timer slightly favored
FP64 (5.027 versus 5.089 ms). The mechanism of the small end-to-end advantage is
not established, and no general arithmetic speed ranking follows.

Completion review nevertheless classified h23 as a numerical-objective miss:
its large algorithmic improvement did not justify the unexamined precision of
its replacement main computation, no output need required the extra digits, and
the whole-request advantage could not be dismissed solely because it was small
or outside the internal timer. The diagnostic remains coordinator evidence.

[Prompt v5](prompt-v5.txt) clarifies that replacement algorithms also need an
arithmetic choice, with narrower arithmetic preferred for qualified ties. The
[v5 protocol](protocol-v5.md) preserves the same bounded three-decision rubric.
Spectral-bank becomes development regression d07. The two event workers were
never dispatched under v4; final targeted transfer uses that untouched family
and a genuinely new area-inspection family, with two fresh workers per family.

The four v5 proposals all passed product gates. Both event implementations used
exact integer class progressions to account for every event without storing or
processing the full capture; j12 used FP32 final scaling, while j22 performed
only eight local FP64 score calculations. j11 rejected an inaccurate FP32 global
summed-area attempt, then qualified stable FP32 local rolling arithmetic. j21
qualified FP32 vertical rolling state but retained implicit FP64 horizontal
products and updates. The initial Sol assessment accepted all four under the
bounded rubric; completion review challenged j21's actual expressions.

The [horizontal discriminator](horizontal-diagnostic/results.json) changed only
three operand declarations, preserving audit, final scoring and all other code.
Both versions passed the unchanged gates. Across nine alternating whole-request
measurements, the narrower variant won seven; medians were 64.087 ms and 56.457 ms.
j21 also reported 14,745,600 bulk bytes while omitting two arrays, for an actual
24,576,000 bytes. There was no area-memory gate; that reporting defect was not
used to invent one. [v5 outcomes](outcomes-v5.json) therefore retain four product
passes but three final numerical-behavior passes, plus the original acceptance
and subsequent rejection. None of the diagnostic variants counts as its repair.

## Autonomous review and owner repair

The user's requirement is no user steering; a single unreviewed completion was
an experimental choice. The final [frozen workflow](workflow-protocol-v1.md)
uses the kit's existing proposed-result, read-only independent review and owner
repair pattern. [Prompt v6](prompt-v6.txt) arranges that review; the [generic review
packet](review-packet-v1.txt) traces actual arithmetic and checks practical
justification, required work, default qualification and observable reporting.
The reviewer gets ordinary task/source/public evidence, without the coordinator's
case-specific findings or private tests. The coordinator relays findings unchanged.
This phase is autonomous multi-agent development, not retroactive one-shot success.

Development used a new retained copy of j21, with a separately declared budget
and a fresh reviewer who independently found implicit wider arithmetic and the
omitted arrays. The original owner repaired from that review; re-review and
frozen product checks passed. [wd01 evidence](workflows/wd01/outcome.json) is a
development result and does not change the original j21 outcome.

The packets and [four-workflow plan](workflow-final-plan.json) were then frozen
before two owners per new family were dispatched. Independent fixture authors
preflighted failing starters, feasible witnesses, and bad controls. Curve processing
tests nonlinear calibration, complete-output buckets, a demanding no-argument
default, and a strict audit mode. Rational resampling tests complete two-channel
streams, exact timeline/count boundaries, a 9 MiB default cap, and a strict audit
override. Before dispatch its rejection check was relaxed from exactly status 2
to any nonzero status, matching the public contract; a status-1 control passed.
Earlier fixture setup defects and superseded measurements remain in preflights.

All four fresh reviewers discovered concrete findings using only the generic
packet, task, source and public evidence. w11 qualified removal of cutoff guards;
the reviewer's submitted-versus-scratch nine-pair medians were 56.315 ms and
50.926 ms, not an exact final-revision speedup claim. Both curve reviewers tested
naïve narrower totals and observed output failures, supporting local FP64
accumulation for the chosen reductions. w21 also qualified blocked FP32 totals
without establishing a precision-specific speedup; FP64 is not universally
necessary. Its owner narrowed the products feeding the existing totals. Both resampler
reviewers independently traced FP64 sample scaling before conversion into float
interpolation; qualified FP32 scaling tied the wider alternative in bounded
end-to-end comparisons, so they selected the narrower arithmetic without claiming
a measured speedup. Exact rational integer state and double audit remained intact.

Owners made the repairs, and the same reviewers checked the resulting source.
w11 needed a second repair for process-reserved static table accounting in audit;
reserved bytes were explicitly distinguished from resident pages. w21 reports
output-plus-table allocations, not whole-process memory. Reviewer source hashes
match the preceding owner submissions at every review. Protected inputs stayed
unchanged. Only after workflow completion, serialized private evaluators compiled
and passed both the four original proposals and the four accepted revisions.

[Workflow outcomes](workflow-outcomes.json) preserve initial findings, each repair,
review acceptance, product grades and budgets separately. The four workflows used
23–36 visible command/file-change/coordination events each, with active stages
under their limits and 17.5–24.3 minutes from preparation to acceptance snapshot,
within the 90-tool/45-minute aggregate caps. Native event counts are not resolved
backend tool telemetry. There were no corrective user messages. Read scopes were
instructions rather than OS-enforced isolation. w22 initially ran `pwd`, `ls` and
`rg --files` in the repository, then a prohibited Git command that failed at the
`/tmp` boundary. Retained commands show filename listing/search, not content reads
from those listed paths or repository edits. Its corrected disclosure is retained;
w12 likewise ran `pwd` and `rg --files` from repository cwd, discovered by the
independent post-workflow audit. Its later commands do not show content reads
from the outside paths. w21 attempted a relative source read from the wrong cwd;
that command failed before returning source content. These are retained as
scope/setup exceptions; this is not a claim of perfect instruction compliance.

This small prospective transfer demonstrates the generic workflow on tested
inputs and this CPU/build. It does not prove every input, hardware target, model
or numerical optimization. Owners requested Luna/high; reviewers inherited the
primary without overrides. Effective runtime model/effort and usage telemetry
were unobserved. Prompt delivery was manual alongside existing installed roles;
no global installation or end-to-end activation claim follows. No new runtime
mechanism, role, registry or installer file was introduced.

## Reproduction and delivery

```sh
python3 -B studies/practical-precision-generalization-2026-11-11/frozen/c/dispatch/private/evaluate.py studies/practical-precision-generalization-2026-11-11/runs/f13/submitted
python3 -B studies/practical-precision-generalization-2026-11-11/compare_burst.py d01 d04 --output new-burst-comparison.json
python3 -B studies/practical-precision-generalization-2026-11-11/frozen/i/curve-processing/private/evaluate.py studies/practical-precision-generalization-2026-11-11/workflows/w11/accepted/submitted
python3 -B studies/practical-precision-generalization-2026-11-11/frozen/j/timeline-resampler/private/evaluate.py studies/practical-precision-generalization-2026-11-11/workflows/w12/accepted/submitted
```

Use a new output file for additional timing observations. The packaging/grading
helper refuses to replace original run outcomes. Input manifests and case freeze
hashes identify the exact source, prompt and protected files. The source baseline
was clean at `ee1978341e502d03514344603d8f141bc2c2cd35`.

The tested addition is now in the canonical policy, nine native role reminders
and controller common instructions. Role pins, the initial Astra role and the
23-file installer inventory remain unchanged. Existing backend, installer and
distribution tests passed (26 + 74 + 4). These verify source wiring and bundle
preservation, not model behavior. No global installation, pumpModem edit, commit
or push was performed.

The final [source audit](source-checks-v6.json) records exact prompt matching,
unchanged role pins and installer inventory, all sixteen frozen case hashes and
the frozen workflow packets. Earlier source audits remain as historical records.

The [independent workflow audit](workflow-independent-audit.md) and the current
[mandatory completion review](completion-review-v6.md) accepted this bounded
numerical demonstration, with the scope exceptions and delivery limits above.
