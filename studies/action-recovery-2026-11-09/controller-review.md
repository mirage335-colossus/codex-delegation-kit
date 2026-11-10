# Independent review of contradictory-completion recovery

Verdict: **no blocking source findings** in the reviewed controller/supervisor
change. This is a focused independent source and test review, not a new live-model
exercise or a rerun of the implementation owner's test suite.

## What was checked

- `controller.helper_event` first replays the proposed event through the existing
  reducer. Schema, original check partition, stage legality, actor independence
  and history checks must succeed before normalization is considered. The second
  replay validates the effective incomplete event before it is retained.
- The observed-ingress route requires a completed backend result and released
  execution, preserves holds and stopped runs, and checks the run deadline and
  global active-service limit. Engineering ingress also requires valid patch
  ownership, dependency identity and an observed command completion. A reported
  blocked operation takes the existing hold path before this conversion.
- A contradiction changes only effective status to `needs_decision`, and an
  accepting review's effective verdict to `substantive_reject`. The actual check
  arrays and remaining conditions are preserved. The raw backend report remains
  on the attempt; `helper_disposition` identifies the original/effective labels,
  assignment, event and reason. Subsequent prompts expose this disposition.
- Worker/reviewer contradictions use the existing owner path. A contradictory
  owner retains its audited patch as the producing attempt and current workspace
  identity. It does not reset repair history, deadlines, service accounting or
  continuation allowances, and does not automatically obtain a second owner turn.
- Historical reducer replay is unchanged. New manual/advisory ingress rejects
  contradictory success; it cannot obtain observed-ingress normalization by
  supplying a result string. No permissions, model settings or ownership scope
  are expanded.

The added tests cover worker/reviewer recovery, owner patch lineage and bounded
continuation, raw versus effective results, malformed/held/expired/stopped/
service-exhausted reports, valid incomplete handoffs, manual rejection and legacy
replay. Existing claim-time checks continue to enforce paused/draining modes,
reserved capacity and the cumulative per-assignment active budget. Those were
inspected without rerunning unrelated tests.

## Scope precision

Normalization can record an incomplete result and queue the existing continuation
while a run is paused; `Controller.claim` refuses dispatch until the run is
running. Likewise, the cumulative per-assignment active budget is checked at
claim time. These are not resumes or budget resets. Documentation should describe
preservation of those controls rather than claim that normalization itself checks
every admission condition.

The correction detects explicit structured contradictions. It cannot discover an
omitted objective, determine that a remaining condition is genuinely substantive,
or establish that the owner executes the right next action. Live end-to-end
exercises remain distinct evidence. A contradictory exhausted owner still needs
the existing explicit continuation decision; no unlimited retry is introduced.

## Reviewed source identity

Source base: `b080ac85eeaeb5480ec9f99f1f4381a1fe5ef401`, with the ongoing dirty
task changes preserved. SHA-256 at review:

| File | SHA-256 |
| --- | --- |
| `controller.py` | `074829ba3fba6def3e931308ace45245ea7379dfd271bee335f68c9b8bbd5e40` |
| `supervisor.py` | `ad35509b7643921a3a4fa05cebc0cc31919b71e5510569eac9a22edf4fc76a52` |
| `tests/test_engineering_controller.py` | `752fa7c21903eb2aca8dac0bb7a9661748beff87fcef5cc287a2d1358ac5993d` |
| `tests/test_supervisor.py` | `88e90b3068feee5fc85cc356706740917333ea0992dabc61a6d2251845f1466e` |

Only this review document was written. No implementation, participant output,
runtime configuration, installed kit or original failure evidence was changed.
