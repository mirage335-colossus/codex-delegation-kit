# Swarm role probe

**Result: incomplete; stopped with three backend holds.** The run used the requested `swarm` role and allocated 2 reasoning/process/CPU slots. The parser and reducer tasks were dispatched concurrently. When the parser runner released its slot, the controller automatically dispatched the lower-priority repeatability task; the reducer runner released shortly afterward. This demonstrates scheduling/replenishment, but all three app-server sessions failed before inference.

All three retained stderr logs report `could not create PATH aliases: Read-only file system (os error 30)` followed by `Error: Read-only file system (os error 30)`. Each runner exited 1 with `released=true`; thread IDs and resolved model settings are absent, and no model turn started. No diagnostic command ran: parser output was not observed, reducer wrapper source/bytecode was not created or captured, and the 60-second sleep command did not reach its 25-second cutoff. The slow task is a backend setup hold, not a verified timeout cutoff or an inconclusive experiment.

The run was durably stopped without retry or escalation: 0 active execution, 0/3 original tasks completed, three backend holds preserved. No fixture or kit files were changed. Source hashes before/after match. Cleanup remains unset and private workspaces are retained because the operations are held; no manual deletion occurred.

See `inventory.json` for the compact task inventory, `events.json` and `timings.json` for dispatch/release chronology, `result-swarm-*.json` for normal CLI results, `settings.json` for requested/observed settings and hashes, and `final-status.json` for the stopped controller report. No escalation, X11, retry, alternate backend, or manual diagnostic execution was used.
