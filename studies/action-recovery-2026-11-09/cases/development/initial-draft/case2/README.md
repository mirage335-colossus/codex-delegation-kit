# Exercise 2 — whole-application outcome recovery

Participant source/tests/data are under `participant/`. The private evaluator and independent witness are under `private/`. Baseline original tests pass and adapter normalization already works, while the supported CLI leaves the user's stock unchanged because it takes the old parser path. The actual route should reuse the existing adapter and apply valid normalized rows to the ledger.

Run from `participant/`: `python3 -m unittest discover -s tests`, then `python3 -m src.inventory_app data/vendor_feed.csv`. For private evaluation, run from `participant/`: `PYTHONPATH=. python3 ../private/evaluate.py` and `PYTHONPATH=. python3 ../private/witness.py`.
