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
    # Repeatedly dispatch the earliest job currently ready. Rescanning after
    # each completion allows chains to run in one invocation while unrelated
    # jobs with missing inputs or incomplete dependencies remain pending.
    while True:
        job = next((job for job in jobs
                    if job["id"] not in completed
                    and all(dep in completed for dep in job["deps"])
                    and all((root / name).is_file() for name in job["inputs"])), None)
        if job is None:
            break
        materialize(job, root, state)
        completed.add(job["id"])
        with events_path.open("a") as handle:
            handle.write(json.dumps({"job": job["id"], "kind": job["kind"]}, sort_keys=True) + "\n")
    result = {"completed": [job["id"] for job in jobs if job["id"] in completed],
              "pending": [job["id"] for job in jobs if job["id"] not in completed],
              "status": "ok"}
    (state / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
