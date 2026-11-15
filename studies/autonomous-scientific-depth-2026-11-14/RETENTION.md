# Retention for future research-feature improvement

The user explicitly rejected historical exercise reproduction as a preservation
goal and requested replacement of the latest commit. This directory therefore
retains learning material, not byte-complete experiment archives.

Retained material consists of authored study designs and prompt proposals,
evaluation criteria, outcome and critique reports, failed approaches, runtime
diagnoses, and a deduplicated history of the kit's own prompt variants. These
records explain what was tried, what the evaluators found, and which interpretations
remain unsupported. They can inform future improvements without another campaign
to rediscover the same failures.

Removed material includes downloaded articles and standards, page images,
recordings, spectrum arrays, numerical replay outputs, copied external source
trees, copied pumpModem reference/appraisal/project snapshots, raw web responses,
raw event streams and repeated thread/diff snapshots, acquisition caches,
reproduction directories, old hash inventories, and redundant kit source trees.
No third-party payload is preserved inside a compressed or encoded archive.
Scientific facts, citations and authored evaluations are retained as analysis;
they are not copies of the cited publications or their datasets.

Historical reports have an explicit retention qualification. Links to omitted
artifacts become labelled historical locators. Their past claims of complete
preservation, hash matches and passed checks describe the original exercise;
they are not new assertions about this reduced checkout. The original scientific
grades and their limitations are not upgraded by this cleanup. URLs and source
identities are provenance, not a guarantee that original source bytes remain
available. Exact reproduction and independent re-audit of every old judgment
are deliberately no longer supported.

The [prompt history](prompt-history/versions.json) maps each frozen candidate to
deduplicated records in [prompts.jsonl](prompt-history/prompts.jsonl). These are
only the kit's own policy and role files, not model-session transcripts or
third-party tool results. Their SHA-256 identifiers describe the embedded prompt
text. Final installed behavior remains defined by the current repository source.

The small helpers under `tools/` and their self-contained synthetic tests remain
usable. The more elaborate native harness and fixture-dependent tests are kept
as plain-text implementation references under [harness-reference](harness-reference/README.md).
They are not executable historical tests in this checkout. Keeping this code
preserves hard-won implementation knowledge without keeping its acquired inputs.

This cleanup is restricted to the study introduced by the replaced commit.
It does not audit or remove material in earlier commits or other studies, and
does not establish a repository-wide redistribution clearance. It changes no
runtime implementation, role setting, global installation, or remote repository.
