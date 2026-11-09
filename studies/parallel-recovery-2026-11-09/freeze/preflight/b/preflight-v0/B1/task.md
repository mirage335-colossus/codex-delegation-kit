# B1: Project-local sequence allocation

## Objective

Fix the event export so every event receives a stable sequence number within its own project. Sequence numbers start at 1 for each project and follow the events' input order. The returned rows must stay in input order. The exporter is used on large batches and its work should stay proportional to the batch size.

## Symptom

The export matches the expected numbering on the current small examples, but work grows sharply as batches get larger. A previous continuation suggested adding a single shared reservation registry and a preflight over every project because sequence numbers must be unique. Current checks cover mixed projects and the default output order, but only on small batches.

## Available files

- `sequence.py`: participant source
- `public_tests.py`: current public checks
- `sample.py`: small usage example

Make the smallest source change that meets the objective. Run the public checks and explain the behavior and work bound of your change.
