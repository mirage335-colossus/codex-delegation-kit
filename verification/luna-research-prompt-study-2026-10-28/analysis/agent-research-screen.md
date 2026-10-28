# Label-blinded research screen

Six opaque cases; no winner selected. Qualified counts are per case, not statistical samples. Full-content scores are distinct from strict-budget scores; independent verifier checks do not retroactively establish researcher access. Expert stage: all findings not individually assessed.

| Case | Original | Strict lower / unresolved / upper | Full-content lower / unresolved / upper |
| --- | ---: | --- | --- |
| r693 | 4 | 4 / 0 / 4 | 4 / 0 / 4 |
| r801 | 4 | 3 / 1 / 4 | 4 / 0 / 4 |
| r318 | 4 | 3 / 1 / 4 | 4 / 0 / 4 |
| r139 | 4 | 4 / 0 / 4 | 4 / 0 / 4 |
| r612 | 4 | 3 / 1 / 4 | 4 / 0 / 4 |
| r654 | 5 | 5 / 0 / 5 | 5 / 0 / 5 |

Strict case scores sum to 22–25; full-content scores sum to 25. These are descriptive totals, not arm means; arm grouping is deliberately unavailable. For r801 f2, the independent verifier checked the abstract, but the only logged original STORM open is operation 17. For r318 F2, search 9 specifically targets OpenScholar, while search 7 may already have discovered it; attribution is unresolved. R612 f4 is supported in full after the cutoff but its validity clause was first surfaced at operation 17.

The original agent-2.md says r612 exceeded the 8-query limit. Correction: its logged eight searches meet that limit; its 18 total operations exceed 16. R318 logged 10 searches against eight; r801 logged 17 total against 16.

## r693

Decision: test staged research with concise evidence, alternatives and falsifiers under direct expert access and independent acceptance. Agentless FSE §1, §5 supplies issue-repair pipeline and clue sensitivity; CoVe ACL abstract supplies verification questions; NLP ideation preprint §5, §7.1, Appendix F supplies novelty/feasibility and self-ranker caution. These sources do not test this workflow. Candidate approaches: bounded localization-to-discriminator; separately check claims; generate distinct alternatives and have an expert evaluate them. Clue-rich tasks may inflate apparent benefit. Cheapest falsifier: matched clue-rich and ambiguous repository tasks, compare missed alternatives and reviewer reconstruction. Unresolved: whether any benefit transfers and whether source boundaries resist injection. Rejected SWE-agent abstract as redundant; peer-review status unknown, no full-paper claim. Retain original four IDs as distinct stages, verification, alternative evaluation, and benchmark caveat.

Terra stage: staged-research = retained; independent-verification = retained; alternatives-and-rankers = retained; benchmarks-and-scope = retained. Expert: none individually assessed.

Sources: [agentless](https://lingming.cs.illinois.edu/publications/fse2025.pdf) (§1, pp. 2–4 (three-stage localization/repair/validation and problems with agentic planning); §4–5 (evaluation and benchmark caveats); §8, p. 20.); [cove](https://aclanthology.org/2024.findings-acl.212/) (Abstract and ACL proceedings metadata; paper §2–3 describes draft, independent verification questions/answers, and revised response.); [idea_study](https://arxiv.org/abs/2409.04109) (Abstract; §5 main results; §7.1 limitations; Appendix F, collaborative reasoning prompt and evaluator.).

## r801

Decision: compare selective scoped exploration, perspective-led questions and short evidence-responsive challenge against broader agent consultation. Ansible preprint §§5.5, 6.3–6.4 records forced consultation's higher calls and tokens and lower point estimates; paired significance differs by gold definition. STORM abstract supports diverse perspectives; its full-text open was operation 17, outside the eligible prefix. Debate drift and Flip-Test abstracts show conditional failure; GAVEL and Agent-Blame abstracts motivate atomic provenance and synthesis checks. Limits: localization, public writing and QA are not architecture research; documentation co-evolution wording remains unverified. Cheapest falsifier: matched selective versus forced consultation with relevance, missed dependencies, reviewer effort and drift recorded. Unresolved: original eligible evidence for STORM-specific claims, provenance completeness and target transfer. Rejected forced universal consultation, unrestricted debate and drop-in STORM; bounded responsive critique remains viable.

Terra stage: f1 = retained; f2 = unresolved; f3 = retained; f4 = retained. Expert: none individually assessed.

Sources: [storm](https://aclanthology.org/2024.naacl-long.347/) (PDF pp. 1–2 (abstract, introduction, perspective-guided questions); p. 9 and Limitations (neutrality/verifiability)); [repo-exploration](https://arxiv.org/abs/2606.11976) (§§4.3, 5.5, 6.3–6.4, 7; lines 175–180, 301–304, 374–387, 405); [drift](https://aclanthology.org/2026.findings-eacl.268/) (ACL Anthology abstract; study covers 10 tasks and human analysis of 170 drifting debates); [flip-test](https://aclanthology.org/2026.insights-1.8/) (ACL Anthology abstract; 2,417 MuSiQue examples with Llama 3.1 8B and Ministral 3 8B); [gavel](https://aclanthology.org/2026.findings-acl.1789/) (ACL Anthology abstract; Evidence Contract, Mechanized Chain of Scrutiny, FEVEROUS/HOVER results and ablations); [agent-blame](https://aclanthology.org/2026.emnlp-main.1681/) (ACL Anthology abstract; per-invocation faithfulness audit, four error classes, orchestrator and citation-recall findings).

## r318

Decision: test a strong single-agent baseline, independent citation/factuality/coverage audit, handoff audit and separate injection-risk evaluation. ACL discussion paper abstract supports a conditional single-agent baseline; OpenScholar full article supports multidimensional synthesis assessment; repository QA preprint abstract identifies handoff failure; EMNLP injection benchmark abstract identifies vulnerability, not an effective defense. These are task- and model-specific. Cheapest falsifier: matched direct retrieval versus scout handoff, audit actual source passages and record missed decision evidence; evaluate injection boundary separately. Unresolved: effect on the target workflow and whether excess searches contributed to OpenScholar discovery. Ten searches exceed the eight-search cap. Rejected ICML debate claim because its content was not retained in the opened excerpt; Agentless and broader papers were not developed as findings.

Terra stage: F1 = retained; F2 = unresolved; F3 = retained; F4 = retained. Expert: none individually assessed.

Sources: [S1](https://aclanthology.org/2024.acl-long.331/) (Abstract on ACL Anthology page; page reports strong prompted single-agent performance nearly matching the best discussion approach, with discussion outperforming single-agent only when prompts lacked demonstrations.); [S2](https://www.nature.com/articles/s41586-025-10072-4) (ScholarQABench evaluation discussion; article lines 107 onward describes citation accuracy plus human rubric assessment of coverage, coherence, writing quality and factual correctness.); [S3](https://lingming.cs.illinois.edu/publications/fse2025.pdf) (p. 10, lines 616-629: distinguishes agentless RAG baseline and reports resolved rate, inference cost, token use and location accuracy as evaluation metrics.); [S4](https://arxiv.org/abs/2608.01507) (Abstract: on SWE-QA, semantic search answered 65.2% versus deep agentic search 46.2% and cost less than half; 41.8% of deep-search failures involved silent planner/sub-agent handoffs.); [S5](https://aclanthology.org/2024.emnlp-main.33/) (Abstract, lines 59-60: benchmark evaluates instruction following under prompt injection and reports significant vulnerabilities in tested models.).

## r139

Decision: compare bounded alternative search and repository-grounded claims against a simple baseline; evaluate outcomes rather than confidence or length. Tree of Thoughts full paper supports branching and backtracking on narrow benchmark tasks; CodeAgent and RepoCod abstracts support artifact and repository-context questions; MIPRO abstract supports metric-based prompt optimization; RCI abstract supports critique experiments, not source verification. None validates architecture scouting. Cheapest falsifier: matched existing-repository decisions scored for distinct viable alternatives, source correctness, omissions and reviewer time. Unresolved: transfer and whether self-critique adds value after direct checks. Rejected debate and OPRO material behind access challenges and a cache-missed source; preserve independent acceptance and untrusted-source boundaries as task constraints.

Terra stage: bounded-branching = retained; repo-grounding = retained; evaluate-prompt = retained; critique-is-not-proof = retained. Expert: none individually assessed.

Sources: [tot](https://proceedings.neurips.cc/paper/2023/hash/271db9922b8d1f4dd7aaef84ed5ac703-Abstract.html) (Sections 1 and 3, lines 92-108 and 165-187; Appendix B.2-B.3, lines 954-984 (PDF line locators).); [codeagent](https://aclanthology.org/2024.acl-long.737/) (ACL Anthology abstract and proceedings metadata, lines 58-60 and 115-126; PDF title/abstract at pages 0-1.); [repocod](https://aclanthology.org/2025.acl-long.1204/) (ACL Anthology abstract, lines 58-61; proceedings and venue metadata, lines 62-93.); [mipro](https://aclanthology.org/2024.emnlp-main.525/) (ACL Anthology abstract, lines 58-61; conference metadata, lines 62-95.); [rci](https://proceedings.neurips.cc/paper_files/paper/2023/hash/7cc1005ec73cfbaac9fa21192b622507-Abstract-Conference.html) (Official NeurIPS abstract, lines 0-9; Recursive Criticizes and Improves (RCI) claim is abstract-level.).

## r612

Decision: compare research idea generation with bounded external critique against a simpler route. ResearchAgent abstract describes research/idea/review pipeline; ICML debate abstract reports no dependable advantage over simpler baselines; ACL self-bias abstract supports caution about model self-review. Agentless full paper opened at operation 12 supports a simple repair pipeline and benchmark result; its validity-limits find at operation 17 exceeds the 16-operation limit. Cheapest falsifier: compare matched tasks with one evidence-specific challenge and direct source assessment; track lost alternatives, errors and expert effort. Unresolved: Agentless f4 validity clause under strict budget and all cross-domain transfer. Reject default open-ended debate, self-review as independent validation and direct transfer of benchmark wins. Eight searches meet the search cap; 18 total operations exceed the total cap.

Terra stage: f1 = retained; f2 = retained; f3 = retained; f4 = unresolved. Expert: none individually assessed.

Sources: [researchagent](https://aclanthology.org/2025.naacl-long.342/) (Abstract, lines 57–61; publication metadata, lines 62–93); [mad](https://proceedings.mlr.press/v235/smit24a.html) (Abstract, lines 22–24); [selfbias](https://aclanthology.org/2024.acl-long.826/) (Abstract, lines 58–59; venue and bibliographic record, lines 61–92); [agentless](https://lingming.cs.illinois.edu/publications/fse2025.pdf) (§6.1–6.3, PDF pp. 15–19, lines 1046–1156 and 1227–1276; §8, lines 1277–1283).

## r654

Decision: evaluate targeted retrieval and citation/coverage audit, optional specialized roles, and lean repository context against simple baselines. ICML debate abstract cautions against default debate; OpenScholar full article reports specialized scholarly retrieval and synthesis; LiRA abstract reports specialized literature roles; ContextBench and AGENTS.md preprints report context-selection and cost limits. ContextBench concerns issue resolution and AGENTS.md findings distinguish generated and developer context; do not remove required instructions. Cheapest falsifier: compare relevant context used, missed alternatives, errors, reviewer effort and cost on matched tasks; compare optional role splits separately. Unresolved: target transfer, unpublished review status for both preprints and role-split benefit. Rejected SWE-bench abstract as nondiscriminating and generic debate studies as redundant; retain conditional positive debate evidence.

Terra stage: f1 = retained; f2 = retained; f3 = retained; f4 = retained; f5 = retained. Expert: none individually assessed.

Sources: [s1](https://proceedings.mlr.press/v235/smit24a.html) (Abstract, lines 13–16 and 22–25); [s2](https://www.nature.com/articles/s41586-025-10072-4) (Abstract; Introduction; evaluation and citation-accuracy discussion, especially lines 91–111); [s3](https://ojs.aaai.org/index.php/AAAI/article/view/41489) (Abstract and publication/citation metadata, lines 32–45); [s4](https://arxiv.org/abs/2602.05892) (Abstract, lines 3–4; context retrieval cost at line 160); [s5](https://arxiv.org/abs/2602.11988) (Abstract lines 16–18; study conditions and results in paper sections summarized at alphaXiv lines 27–43).

## Cross-case mechanism union

- staged bounded investigation and selective dispatch: r693:staged-research, r801:f1, r612:f4
- alternative generation and perspective questions: r693:alternatives-and-rankers, r801:f2, r139:bounded-branching
- claim verification and provenance: r693:independent-verification, r801:f4, r139:critique-is-not-proof, r612:f3
- benchmark scope and local evaluation: r693:benchmarks-and-scope, r139:evaluate-prompt, r612:f4
- debate limits and simple baseline: r801:f3, r318:F1, r612:f2, r654:f1
- synthesis evaluation and cited retrieval: r318:F2, r654:f2
- repository handoff and context quality: r318:F3, r139:repo-grounding, r654:f4, r654:f5
- separate prompt injection risk: r318:F4
- specialized research or synthesis roles: r612:f1, r654:f3

The union retains all original finding IDs; mechanism grouping is not an arm comparison. Each original is credited only to its own case. Source claims and detailed verifier dispositions, rejected candidates, source access and publication evidence are preserved in the JSON and original verification records. Publication unknown is not a negative finding. No reviewed source demonstrates the target mixed-model architecture workflow or validates an injection defense. No local campaign was run. Direct expert source access, timely review and independent acceptance remain requirements. Telemetry and expert reconstruction burden remain unmeasured.
