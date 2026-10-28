# Optional research frontier

1. **Does bounded alternative search improve useful source-backed alternatives enough to justify its extra work on repository research?** Basis: bounded-branching / tot https://proceedings.neurips.cc/paper/2023/hash/271db9922b8d1f4dd7aaef84ed5ac703-Abstract.html; narrow benchmark and reported token-cost limits. Decision: Whether to evaluate the alternative-search prompt for this workflow.

2. **Do source-grounded reports reduce missed contrary evidence and expert reconstruction on actual investigations?** Basis: repo-grounding / codeagent https://aclanthology.org/2024.acl-long.737/ and repocod https://aclanthology.org/2025.acl-long.1204/; code-generation benchmark transfer unresolved. Decision: Whether grounding requirements improve the handoff.

3. **Does a critique step add independently supported counterevidence or reduce reviewer correction?** Basis: critique-is-not-proof / rci https://proceedings.neurips.cc/paper_files/paper/2023/hash/7cc1005ec73cfbaac9fa21192b622507-Abstract-Conference.html; abstract-only computer-task results. Decision: Whether to include critique in a matched prompt comparison.

The branching source is full text; CodeAgent access was limited to opening pages, and RepoCod and RCI were abstract-only. Benchmark results do not validate this workflow. Independent acceptance and untrusted-source boundaries remain task constraints.
