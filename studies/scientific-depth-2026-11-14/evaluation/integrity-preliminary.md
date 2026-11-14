# Preliminary study integrity inventory

Inventory: 678 files, 4594862 regular-file bytes. The JSON report contains per-file sizes and SHA-256 hashes.

## Prose classification

Current canonical scientific chapters, ledgers, and synthesis are classified separately from explicitly named first-pass/correction records, continuation prose, evaluator Markdown, and other Markdown. The JSON lists per-file word counts only; no cross-category aggregate is given.

File counts by class: current-scientific-prose: 22, evaluator: 63, historical-first-pass-or-correction: 7, other-study-markdown: 20, supplemental-continuation-prose: 6. Individual per-file word counts are in JSON; these are separate measures.

## Integrity checks

- Markdown links: 225 local paths checked; 18 missing; 27 outside-scope or symlink paths skipped.
- Meter: 363 listed receipts, statuses {'reserved': 1, 'returned': 362}; 1 unfinished; 0 missing and 0 unlisted receipt files.
- Meter operation totals: 1173 in receipts vs 1173 in meter; total cap 1600, within cap: True. Per-run details are in JSON.
- Timestamp/late-recording fields found: 0; timing reconstructable: False. No trusted receipt/call timestamps are present; lateness cannot be independently inferred from this meter.
- Manual/timing caveat: Receipts cover cooperative wrapped operations only. Boundary-incident reports manual source-call uncertainty and a late groundwave reservation; neither can be certified or cleared by aggregate receipt consistency. Relevant incident sections: Reviewer source-call accounting uncertainty, Late groundwave web reservation, EME source-call continuation uncertainty, Lead continuation count correction.
- Prospective and uptake frozen hashes match: True.
- Comparator kit/pump source IDs are reproduced from corpus-inventory.json, not independently validated. Pump source and appraisal files were not opened.
- Missing links include 0 from active research/review sources and 18 from first-pass/interim snapshots. Historical text is left intact; any active missing paths should be repaired before final freeze.

## Artifact handling

See the JSON for largest files, cache/temporary candidates, suffix counts, and Git tracking status. Review untracked source/evidence for intended durable inclusion; retain reproducibility-critical receipts and logs, and classify scratch/tmp outputs, compiled binaries, and bytecode caches before staging or excluding them. The inventory deletes nothing.

## Limits

The cooperative meter observes wrapped web operations only. These checks cannot prove manual/unwrapped calls, timely receipt creation, source-reading depth, participant compliance, or scientific acceptance. The historical pump dirty-state string contains paths in restricted comparator locations; it is treated as recorded metadata only.
