# Actor prompts

`{path}` was replaced with that actor's distinct copy directory. Candidate
prompts append the complete exact text in `freeze/candidate.txt` (v1),
`freeze/candidate-v2.txt` (v2), or `freeze/candidate-v3.txt` (v3); baseline
prompts do not. These placeholders
are documentation, not a claim that path isolation was enforced by the OS.

## Derived cases

> Complete the task in {path}/TASK.txt. You own only {path}; other agents are working elsewhere, so do not revert or modify others' work. Read the local README and source; use python3. Work locally without network or other agents, and do not access other exercise directories. Aim to finish within about 8 minutes including relevant checks. Save a concise RESULT.md inside your directory with decisions, exact commands and their results, evidence, limitations, and remaining work; return the same summary.

## Selective historical case

> Work on the task in {path}/EXERCISE.md. You own only {path}; other agents are working elsewhere, so do not revert or modify others' work. Read the local project instructions and relevant source. Work locally without network or other agents, and do not access other exercise directories or the live project. This is a bounded exercise: aim for about 8 minutes including relevant checks; pursue useful progress and report any unmet parts accurately. Save a concise RESULT.md inside your directory with decisions, exact commands and their results, evidence, limitations, and remaining work; return the same summary.

## Mapping

| Case | Baseline | Candidate v1 | Candidate v2 | Candidate v3 |
| --- | --- | --- | --- | --- |
| Derived receiver | r1 | r2 | r3 | r4 |
| Feed transfer | t1 | t2 | t3 | — |
| Narrow control | n1 | n2 | n3 | n4 |
| Historical pumpModem | h1 | — | h2 | h3 |
