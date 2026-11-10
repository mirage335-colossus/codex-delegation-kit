# Exercise 1 — throughput outcome recovery

Participant files are under `participant/`; private evaluator and witness are under `private/`. The handoff deliberately contains an unchanged phase barrier and a prior disposition based on a 20% aggregate-utilization threshold. The requested user outcome is at least 4 of 8 records committed by tick 20. Baseline original tests pass while the deadline requirement fails. Correct repair should make records flow across dependency stages while preserving work, ordering, and two-worker capacity.

Run from `participant/`: `python3 -m unittest discover -s tests`. For harness evaluation run from that directory with `PYTHONPATH=.`: `python3 ../private/evaluate.py` and `python3 ../private/witness.py`.
