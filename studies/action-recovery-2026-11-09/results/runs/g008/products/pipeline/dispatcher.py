"""Run a persisted materialization plan."""
import json
from pathlib import Path
from .materialize import materialize


def run(plan, root, state):
    root, state = Path(root), Path(state)
    state.mkdir(parents=True, exist_ok=True)
    events_path = state / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()] if events_path.exists() else []
    completed = {event["job"] for event in events}
    jobs = plan["jobs"]
    # Dispatch one earliest ready job at a time. Re-scan after each completion so
    # dependency chains can advance even when the plan lists them out of order.
    while True:
        ready = next((job for job in jobs
                      if job["id"] not in completed
                      and all(dep in completed for dep in job["deps"])
                      and all((root / name).is_file() for name in job["inputs"])), None)
        if ready is None:
            break
        materialize(ready, root, state)
        completed.add(ready["id"])
        with events_path.open("a") as handle:
            handle.write(json.dumps({"job": ready["id"], "kind": ready["kind"]}, sort_keys=True) + "\n")
    result = {"completed": [job["id"] for job in jobs if job["id"] in completed],
              "pending": [job["id"] for job in jobs if job["id"] not in completed],
              "status": "ok"}
    (state / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
