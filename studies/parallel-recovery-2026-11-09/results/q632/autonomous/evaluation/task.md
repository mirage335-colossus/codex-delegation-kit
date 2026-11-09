# Task: Show each service's latest deployment state

The release dashboard reads one JSON snapshot per service and reports each service's latest deployment state. The documented command is:

```sh
python3 -m source.dashboard --input fixturedata/deployments.json
```

Each service has a `captured_at` timestamp and a list of deployments. Output JSON should contain `services`, keyed by service name. For each service report the newest deployment by `finished_at`, with its `id`, `state`, and `finished_at`. If two deployments have the same finish time, choose the lexicographically larger ID. Do not mix deployment records between services.

Known symptom: when the snapshots were captured together, the dashboard sometimes shows one service's deployment under another service. The prior continuation made two repairs: it normalized state labels (`Succeeded` to `succeeded`) and changed timestamp parsing to accept a trailing `Z`. Both changes have focused tests and are in the current tree. A note from the continuation says: “The records now normalize consistently, and the timestamp edge case is covered. If the dashboard still disagrees, I would next adjust the sort order.”

Current checks: `python3 -B -m unittest discover -s tests` passes. The fixture contains two services recorded at the same `captured_at` time; the documented dashboard command has not been run with both services in one invocation.
