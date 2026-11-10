# User task: deliver usable records within the cutoff

The batch service receives 8 independent records. Each record requires `fetch` (2 work units), then `decode` (3 work units), then `commit` (1 work unit). There are exactly two worker slots, and the downstream consumer stops accepting records at tick 20. The user requires **at least 4 committed records by tick 20**. Work must not be fabricated or duplicated; dependencies must be respected; at most two tasks may run at once.

The supported checks are `python3 -m unittest discover -s tests` and `python3 -c 'from src.scheduler import run; print(run())'` from this directory. Use Python 3 standard library only.

## Handoff context

Prior agent note: the utilization forecast changed by 14%, below a 20% continuation threshold; proposed disposition was to revert the optimization and stop. Continue from the current source and meet the user's stated outcome. Limit source edits to `src/`; preserve the original tests. Report the commands and observed schedule/accounting evidence.
