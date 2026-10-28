# Agent 2 verification

Verified only reports r139, r612 and r654 against their cited primary sources. The source checkout was `947ed25d4058e405ecf45d6956671f6fecb12026`, with unrelated work already present. I used 16 logical web operations (4 searches, 12 opens), within the group limit; the shared MAD source was opened once and reused. Full operation and source records are in [agent-2.json](agent-2.json).

| Case | Original findings | Qualified lower bound | Unresolved | Upper bound |
|---|---:|---:|---:|---:|
| r139 | 4 | 4 | 0 | 4 |
| r612 | 4 | 3 | 1 | 4 |
| r654 | 5 | 5 | 0 | 5 |

Across the three cases, 12 of 13 findings qualify on the evidence checked; one remains unresolved, so the upper bound is 13. There are 13 distinct cited primary sources: 11 peer-reviewed papers and 2 arXiv preprints with peer-review status unknown. MAD is a shared discovery in r612 and r654; the union catalog keeps both original finding IDs.

R612's original report logged 18 operations (8 searches, 7 opens, 3 finds), exceeding its 16-operation total and 8-query limits. Its f4 core pipeline and benchmark claims were in a full-paper open before the cutoff, but its external-validity support was first surfaced by operation 17. I retained f4 as unresolved, excluded post-cutoff support from its lower-bound credit, and preserved its upper-bound credit.

No paper directly evaluates a smaller-model repository scout finding architecture alternatives for a stronger mixed-model decision maker. None validates prompt-injection handling, direct expert access to decisive sources, timely consequential review, or independent patch acceptance. Proposed matched evaluations remain unrun. No winner selected; Terra and expert stages are outstanding.
