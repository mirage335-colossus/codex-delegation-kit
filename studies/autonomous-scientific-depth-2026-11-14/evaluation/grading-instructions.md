> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Independent scientific adjudication

Resolve `protocol.md` and `baseline/` relative to the directory containing this
file (`evaluation/`), not the study root. Your assignment identifies the exact
locked submission, domain map, output and acquisition paths. Use those positive
paths directly; do not recursively search the study root or other episodes to
locate a missing input. Ask for its exact path if needed.

Use only a locked submission, the frozen comparison materials, the applicable
ordinary task and the assigned domain. Do not contact the authors, read other
case outputs, or repair the submission. The separate coordinator audit handles
initiation, interventions, exposure, timing and resources. Judge science first
without assuming that a plausible implementation plan, an internal approval or
the authors' confidence establishes comparable literature depth.

The original `acceptance.md`, `coverage-matrix.json` and domain map define the
scientific comparison. Apply the newer protocol's scoped interpretations for
noise and conditional rows. Named historical papers/models are comparator aids,
not required answer strings. Accept materially equivalent evidence that settles
the same engineering decision and conditions at comparable depth. Do not change
the standard based on how much work a submission contains.

Inspect linked evidence throughout the locked submission where relevant, not
only the nominal chapter. Distinguish reused canonical documentation from fresh
primary-source discovery or verification. Verify decisive source passages and
definitions, rerun inspectable decisive calculations, and check an adverse or
boundary example in the domain. Inspect scripts before executing them; run only
authorized bounded standalone research checks. Do not build/run pumpModem or
claim product/hardware qualification. Resolve absolute original packet paths to
the locked archive supplied in your assignment; never substitute the live
author workspace for a missing archived result.

Evaluate every assigned matrix row and each of the six domain-depth checks.
Record inspected participant locators, original-source/calculation verification,
the substantive comparison, and the exact remaining work where relevant. Use
these exact dispositions:

- `Supported`
- `Supported boundary`
- `Partial`
- `Unsupported`
- `Outside declared conditions` (conditional matrix rows only)

A supported boundary requires inspected evidence for the limitation, meaningful
available discriminators already performed, and a justified conditional decision
or concrete missing input. Calling a choice deferred, saying hardware is not
qualified or proposing a feasible desk check does not by itself meet this bar.
Likewise, do not demand field calibration or a particular inaccessible source
when another performed discriminator addresses the actual scoped decision.

An evaluator may reproduce a supplied result. An evaluator's new source,
calculation, missing context or observation cannot fill the author's coverage
gap. Report a materially useful but incomplete research dossier as such. Preserve
disagreements and source-access limits; do not silently change a disposition to
make the overall result pass.

Output `review.md` and `dispositions.json` in your assigned evaluator directory.
The JSON structure is:

```json
{
  "domain_id": "ASSIGNED_DOMAIN",
  "overall": "Partial",
  "rows": [{
    "id": "EXACT_MATRIX_ID",
    "disposition": "Partial",
    "participant_evidence": ["locked relative path:line or heading"],
    "independent_checks": ["source locator / command / actual result and limit"],
    "reason": "Substantive comparison to the frozen question",
    "remaining_action": "Concrete material gap, or null"
  }],
  "depth_checks": [{
    "number": 1,
    "disposition": "Supported boundary",
    "evidence": ["locators and independent check"],
    "reason": "Why the original depth requirement is or is not met"
  }],
  "source_access_limits": [],
  "executed_checks": [],
  "unexecuted_checks": [],
  "resource_notes": []
}
```

Use the actual domain/row IDs, all six numbered depth checks, and actual outcomes.
Keep the JSON concise; reusable technical explanation belongs in `review.md`.
Every essential and applicable conditional row and all six depth checks must
meet their standards for a domain pass. No arithmetic average or strong branch
compensates for a missing material question. Return a compact native verdict and
artifact pointers. Do not issue a main-chat completion judgment or recursively
request review gates.
