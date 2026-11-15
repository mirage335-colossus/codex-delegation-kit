> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Research-process mechanisms considered after author lock

Coordinator research on 2026-11-15, while independent domain assessments were
running. This informs a possible later prompting treatment; it is not evidence
available to Operation02's authors and cannot repair their result. No candidate
change is selected here. These systems differ from the pinned Codex roles and
the modem task; their results motivate tests, not a transfer guarantee.

## Source-supported observations

**STORM (NAACL 2024).** The method develops perspectives from related articles,
asks questions through source-grounded conversations, then constructs an outline
before drafting. Its equal-question-count ablation favors reading-dependent
conversation over generating all questions upfront. The human evaluation covers
20 article pairs and 10 Wikipedia editors: the reported coverage improvement has
p=0.084, while organization has p=0.005; verifiability does not improve in that
comparison. The authors identify improper inference, inaccurate paraphrase and
source bias. This supports testing an evolving discovery process, with limited
evidence for any particular scientific-depth gain. Inspected §§3, 5.2, 6 and
limitations, including Tables5–6. [Primary paper](https://aclanthology.org/2024.naacl-long.347.pdf).

**AutoSurvey (NeurIPS 2024).** The pipeline retrieves for an initial outline, then
retrieves and drafts each subsection separately before integration and evaluation.
Its ablation shows a large citation-quality loss without retrieval and only a
small average content-quality change without reflection. Evaluation relies partly
on model judges; the reported mixture-versus-human ranking correlation is 0.5429.
The analysis of 100 unsupported claims finds overgeneralization, source mismatch
and misinterpretation. Therefore section ownership and direct source retention
are more defensible hypotheses than assuming another review pass is sufficient.
Inspected §2 algorithm and subsection stages, §3 ablation and §5 limitations.
[Primary paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/d07a9fc7da2e2ec0574c38d5f504d105-Paper-Conference.pdf).

**OpenScholar (Nature, 2026-02-04).** The method retrieves scientific passages,
drafts, generates feedback and new queries for missing information, revises with
additional passages, and checks citations. The published work explicitly does
not claim fully automated scientific synthesis. It notes small expert datasets,
possible rubric-style inflation, unsupported information and evaluator preference
for writing qualities without exhaustive factual checking. Its task is primarily
scientific question answering, not a whole engineering research campaign. The
mechanism suggests attaching new retrieval to unresolved explanatory questions;
it does not establish that internal approval measures completeness. Inspected
Methods' iterative generation and citation-verification sections and limitations.
[Published full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12935541/).

**Agentic AutoSurvey (arXiv v1, 2025-09-23; preprint).** The proposed search,
clustering, writing and evaluation roles are tested on six LLM topics. The authors
report a substantial failure case: 1,334 retrieved papers compressed into one
drafting pass yielded only 80 cited works. They identify hierarchical writing as
a future remedy and acknowledge domain specificity and subjective evaluation.
Citation fraction alone is not scientific coverage, and this observation is not
a causal test of hierarchical drafting. It nevertheless warns against treating
retrieval volume or a polished integrated summary as proof that detailed source
knowledge survives. Inspected §§2 and4; no independent reproduction.
[Primary preprint](https://arxiv.org/html/2509.18661v1).

## Candidate mechanism, not a selected treatment

The useful common idea is sustained, source-driven scientific authorship:
discover explanatory distinctions, develop substantial branch accounts with
their own source inspection and comparisons, preserve those accounts, then
integrate them without replacing them with a short engineering summary. Authors
would derive the branches from the ordinary problem and literature, not receive
the evaluator's domain map. A research task mode could make scholarly explanation
the immediate product while retaining a separate compact engineering handoff.

This differs from simply adding more criticism or telling the same agent to be
thorough. Current V6 already requests two independent accounts, broad discovery,
follow-through and scientific review. Any next experiment must identify what
actually changes in delivered responsibility, sustained authoring and closure;
adding synonyms to those existing requirements is a weak treatment.

No paper justifies compulsory source, word or time quotas, unlimited research,
new model permissions, or success based on internal evaluator agreement. Keep
the finite envelope, independent post-lock science assessment, current source
mapping and ordinary-task uptake checks. Retain each study's measured limitation
when transferring a mechanism.

## Access record

Five coordinator web calls contained24 request items:3 searches,14 opens and7
finds. A Nature landing-page request failed through an inaccessible identity
redirect; the published PMC full text supplied the accessible primary article.
A guessed AutoSurvey arXiv v3 HTML URL returned404; its conference PDF supplied
the primary text. No browser, shell-network, installation or product execution.
These are coordinator design-research costs, separate from the closed author
episode and its fixed400-item scientific evaluator pool.
