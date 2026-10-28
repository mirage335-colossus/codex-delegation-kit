
# Programmatically Enfofcing Parallelism and Ordering

Current cost context (October 28, 2026): the user's unitless Desktop Codex
included-allowance estimates are Luna = 0.1, Terra = 1, Sol approximately 10 and
Astra approximately 20. See [weekly usage cost](policy.md#weekly-usage-cost).
This is separate from API dollars, paid credits and execution-time/resource
costs. It is not implemented scheduler accounting or an amendment to the
historical implementation request below.
Current evidence-discovery and screening guidance is maintained in
[policy.md](policy.md#evidence-discovery-and-terra-screening); it does not
rewrite the historical proposal below.

## WARNING

CAUTION: WARNING: This approach is not tested for production use, and should NOT be made default. Suggest to keep this in a separate git branch.

WARNING: What this is trying to implement may be functionally infeasible, as low parameter count small AI LLMs (eg. GPT-6 Luna), simply may not be able to work through all of the orchestration.


## Prompt

Develop the delegation kit into a complete, practical orchestration system for parallel engineering work.

Implement, validate, document, and install a usable solution that actually dispatches assignments, observes results, replenishes workers, manages owned execution, and recovers after interruption. Deliver working behavior across the complete workflow, with clear acceptance evidence.

The objective is to maximize trustworthy progress toward the user's requested outcome per elapsed time. For large pending-work inventories, discover and complete fast useful work early, park slower work when that enables better progress, advance through the next most promising work, and eventually address the remaining inventory. Respect user priorities, dependencies, correctness requirements, deadlines, and authorization throughout.

SOURCE AND DEVELOPMENT SCOPE

Read the delegation kit's policy and applicable repository instructions. Locate its maintained source checkout using available installation metadata and repository context. Verify the source identity and current dirty state before editing. Treat recorded source paths as hints requiring verification. Preserve unrelated changes and develop in the maintained source, then deploy through its installer.

This request authorizes the implementation, necessary structured scheduling state, execution adapters, tests, examples, documentation, packaging, and installation in the authorized environment. It selects programmatic coordination with persistent state for the new controller mode. Preserve explicitly selected native-only or advisory modes as alternatives, with their capabilities and limitations documented. Do not silently change existing tasks, unrelated configuration, or other active controllers.

Preserve the user's selected primary model, reasoning effort, role settings, service tiers, and applicable concurrency ceilings. Follow the kit's permitted model-routing policy. Support explicit per-run model and effort policies without changing global defaults or assuming that changing responsibility permits changing models.

Use parallel development where it helps, with bounded assignments, clear ownership, compatible interfaces, and independent review. Workers must know they share the codebase and must preserve others' changes. The main chat may perform engineering unless an applicable instruction selects coordinator-only operation.

Use only authorized repositories, execution environments, services, and account capabilities. Developing the kit does not authorize unrelated production workloads, publication, remote writes, or expanded infrastructure access. Focused fixtures, subprocess tests, and a bounded live runtime integration test are part of this implementation's validation scope.

VERIFY THE RUNTIME CONTRACT

Inspect the current kit, available runtime, and current official documentation before choosing integration details. Establish which supported interfaces can create, observe, continue, interrupt, and reconcile workers.

Distinguish native subagents, separately controlled agent threads, and ordinary subprocesses. Do not assume that externally created threads belong to an existing chat's native subagent tree. Do not invent callable APIs or describe hook feedback and suggested actions as autonomous scheduling.

Complete one practical automatic agent backend and a subprocess executor. Use a supported SDK, runtime protocol, or native integration according to actual capabilities. Add hooks where useful and verified. Keep backend-specific behavior behind a small interface; do not require several redundant backends before completing the first working solution.

Propagate project, filesystem, network, tool, approval, model, and budget constraints into every execution path. Changing backends must not broaden authority. Distinguish configured intent from observed effective settings and disclose what cannot be verified. A catalog entry is not proof of model access. Denied execution must not trigger silent substitution of models, accounts, permissions, or backends.

If a required live capability is unavailable, finish independent work and report the precise limitation. Mark the affected acceptance requirement incomplete. Mocked behavior cannot establish live integration.

IMPLEMENT A COMPLETE WORKING PATH EARLY

Build this path first, then extend it:

    ingest -> establish readiness -> claim -> dispatch -> observe
    -> validate evidence -> record outcome -> release resources
    -> replenish -> recover and continue after restart

Keep the design compact: a scheduling authority, an event loop, durable state, execution adapters, and derived reports. Prefer the existing language and modest dependencies. Avoid unnecessary distributed infrastructure, prediction services, dashboards, and competing registries.

Code should handle readiness, claims, ordering, resource accounting, timers, replenishment, and recovery. Agents should handle ambiguity, diagnosis, experimental design, implementation, and review. Agent completion alone must not establish task success, test coverage, or patch acceptance.

AUTHORITATIVE STATE AND EVIDENCE

Use one compact, durable source of scheduling truth, with atomic updates and concurrency protection. Reports must derive from it. Integrate with the existing helper's acceptance and evidence semantics, preserve historical records, and test schema evolution.

Represent:

- Stable run, task, assignment, attempt, and operation identities.
- Source revision and relevant input, configuration, toolchain, and environment identities.
- Narrow dependencies and the evidence required to release them.
- Ownership, output locations, resource requirements, execution identities, and interruption capabilities.
- Duration estimates, uncertainty, selection reasons, checkpoints, service quanta, active service time, and wall-clock deadlines.
- Partial and final evidence, acceptance status, original failures, repair history, holds, and resumption conditions.

Keep scheduling state, execution state, outcome, and engineering acceptance distinct. A valid failing test can be a completed investigation result that creates follow-up work. A scheduling cancellation, setup failure, or parked assignment does not become a demonstrated test failure.

Bind evidence to its actual inputs. Changes invalidate only affected evidence. Preserve accepted work through chat compaction, restarts, handoffs, and retries without rediscovering or recounting it. Detect missing dependencies and cycles instead of leaving unexplained permanently blocked work.

CONTINUOUS REPLENISHMENT

After completion, stable usable partial output, prerequisite acceptance, acknowledged cancellation, resource release, new work, or relevant timer events, update readiness and dispatch eligible assignments that fit available capacity. Execute this loop in code without requiring another main-model turn.

Continue until capacity is occupied or no compatible eligible work exists. Avoid batch barriers and unnecessary all-worker waits. Use events where supported, bounded polling with backoff where necessary, and periodic reconciliation for lost events.

Service-quantum expiry, reassessment times, backoff expiry, and deferred-work eligibility must wake the scheduler even when no worker finishes. A long-running assignment must not prevent reconsideration of better ready work.

Blocked assignments must not reserve large private backlogs. Preserve their identities and resumption conditions, then reuse genuinely available capacity for independent work. A bookkeeping label does not prove that a backend slot, subprocess, memory reservation, or lock has been released.

Allow bounded batches to amortize setup and model overhead. Publish individual usable results promptly and keep unstarted portions splittable. Execute routine validated commands directly through the process executor when a separate model conversation adds no useful judgment.

Keep mapping, diagnosis, implementation, review, and reporting moving alongside unrelated execution. Gates should block only work that depends on their results.

ADAPTIVE FAST-FIRST SCHEDULING

Implement an explainable policy that respects user priority and acceptance requirements while favoring quick useful results. Do not claim globally optimal scheduling under unknown durations and multiple resource constraints.

Among comparable eligible assignments, prefer the lowest expected remaining cost to the next valid useful result. Include setup and restart cost, artifact reuse, scarce resources, uncertainty, and dependency unlock value. A longer prerequisite can outrank an isolated short task when it enables substantial downstream progress.

Use understandable duration classes or feedback queues. Give unknown work bounded discovery opportunities so unseen fast cases are found. Learn estimates from matching observations and relevant history, with confidence and provenance visible.

When a scheduling quantum expires, preserve evidence and update estimates or service class. An interrupted observation establishes only that execution consumed at least the observed service; it is not a completed duration. Do not blindly subtract elapsed time from an obsolete estimate. Separate scheduling quanta, correctness timeouts, active service budgets, and wall-clock deadlines.

Favor fast valid outcomes regardless of whether they are successes or failures. Do not optimize apparent pass rates or count cheap administrative activity as meaningful progress.

For a finite inventory, perform a broad fast sweep, then automatically advance through progressively more expensive eligible work. Give deferred assignments larger justified service opportunities or a different useful diagnostic approach. Do not repeatedly restart the same slow assignment with an insufficient quantum.

Prevent starvation under documented workload assumptions through dependency-aware promotion, aging, or explicit service opportunities. Preserve the fast sweep's purpose rather than imposing an arbitrary slow-work quota. Under continuing arrivals, make the fairness and throughput tradeoff explicit.

Every deferral needs a reason and a machine-actionable resumption condition. Keep original requested work distinct from generated follow-ups; an expanding supply of easy auxiliary tasks must not postpone the original inventory indefinitely. A cleared fast queue is not a completed run.

SAFE PARKING AND PREEMPTION

Declare whether each task type supports deferral before launch, checkpoint-and-resume, cooperative cancellation and restart, safe suspension, or nonpreemptible execution. Interrupting an agent does not necessarily stop its subprocesses, and stopping execution does not automatically create a resumable checkpoint.

Prefer deferring unstarted expensive work and yielding at safe boundaries. Preempt running work when the expected improvement exceeds lost service and restart costs and the action releases the resource needed by replacement work. Reassess as evidence changes; do not assume elapsed duration alone justifies interruption.

Suspended processes can retain memory, locks, and output ownership while wall deadlines continue. Do not suspend a holder of a resource needed by replacement work without a validated release strategy. Respect nonpreemptible operations and supported cancellation paths.

Control only owned execution. Use durable worker/run identity and process-group/start identity rather than a bare recyclable PID. Verify cancellation or reconcile survival before releasing reservations or launching conflicting work. Retain monitoring and ownership of processes that outlive their reasoning worker.

Prevent thrashing with minimum useful service, checkpoints, hysteresis, and bounded interruption/restart waste. Preserve original identity, consumed budgets, deadlines, failure history, evidence, and holds. Parking must not reset engineering repair allowances.

Mark timing evidence invalid when interruption or suspension compromises the required measurement. Schedule a clean qualifying attempt where necessary. Scheduling cutoffs must never manufacture passes, failures, or coverage.

RESOURCE-AWARE PARALLELISM

Track reasoning capacity separately from actual processes, CPU demand, memory, I/O, and exclusive resources. Account for job descendants and nested delegation. A per-session worker ceiling is not permission to multiply that ceiling across independently created sessions.

Provide a supported worker-facing submission/results interface so managed heavy execution passes through admission and ownership checks. Discover and account for backend-owned work through verified interfaces where possible. Explain any unobservable or unenforceable usage; process-pool limits alone do not establish global resource enforcement.

Use actual available and permitted capacity. Avoid arbitrary small worker pools, blanket build serialization, and artificial contention. Continue independent reasoning when compute is constrained. Preserve concurrency that belongs to a task's actual semantics.

Start with bounded probes when resource estimates are missing, then ramp up promptly when measurements permit. Missing historical data must not become a permanent small concurrency limit. Adapt from useful throughput, memory pressure, swapping, errors, queue delay, and actual backend limits; high CPU utilization alone does not prove harmful contention.

Make throttles scoped and temporary, with explicit reasons, reassessment, and release conditions. Backfill compatible work while respecting justified reservations. Avoid deadlocks and starvation caused by resource acquisition order or partial reservations. Apply backpressure without retry storms.

Reuse stable compatible artifacts and caches, enforcing single-writer ownership where required. Check source, toolchain, flags, inputs, and dependency compatibility. Prefer targeted work and reusable outputs when they answer the question faithfully.

Schedule exclusive measurements only when justified by the run's priorities and acceptance requirements. Reserve only the necessary resources and interval, then release them promptly.

GENERIC WORK INVENTORIES

Provide a reusable run format and self-contained examples for task lists, test inventories, and engineering backlogs. Treat any file named PENDING as one optional input convention, not a hardcoded project workflow. Allow incremental discovery, stable references, deduplication, and explicit unmapped entries.

Keep workload-specific discovery and execution in adapters or configuration rather than embedding repository names, machine names, absolute installation paths, model IDs, or fixed throughput targets in the scheduler.

Use structured command arguments and working directories. Do not execute arbitrary inventory prose as shell code. Keep inventories paired with their actual source and configuration. Support separate baseline lanes when needed without assuming that the default branch is the newest relevant work.

Create bounded mapping, setup, execution, diagnosis, correction, and review tasks as evidence makes them ready. Start known executable work before discovery is complete. Expensive shared preparation should release usable outputs incrementally when valid.

For slow tests or checks, assess real coverage overlap and cheaper diagnostic alternatives using inputs, assertions, boundaries, paths, and failure modes. Preserve original acceptance criteria. Reduced diagnostics and source review must have separate evidence categories.

For failures, favor cheap discriminating experiments and faithful checks of the actual implementation. Parallelize distinct hypotheses, preserve matched comparisons, and apply changes only within authorized write scopes. Retain independent review and the existing repair/takeover rules.

RECOVERY AND USER CONTROL

Maintain one active scheduling authority per run. Use atomic claims, stable operation identities, and idempotent event processing. Reconcile live workers, processes, reservations, and partial outputs before replacing work after restart.

Handle crashes before launch, after launch but before acknowledgment is recorded, and after completion but before result persistence. Use backend idempotency where available. Preserve and reconcile uncertain launch outcomes instead of blindly retrying. Guarantee accurate outcome accounting at supported boundaries without claiming universally exactly-once external execution.

Expired leases or missing heartbeats do not prove execution stopped. Late results remain attached to their original attempt and inputs and cannot overwrite a successor or reopen accepted work.

Provide concise interfaces for start, status/explain, pause, resume, drain, stop, recover, and report. Clearly distinguish pausing new dispatch, parking active work, and terminating owned execution.

Persist a user pause/stop decision before acknowledging it. Events, hooks, restarts, and automatic recovery must respect that decision; only an explicit authorized resume clears it. Scheduler-directed parking is separate and follows its recorded resumption condition.

Verify how interruption of the controlling chat reaches the execution controller. If no supported bridge exists, provide an explicit stop mechanism and disclose that stopping the chat alone does not stop detached execution. Automatic continuation must never override a user stop.

Preserve permission and service restriction holds. Continue independent authorized work, but do not route a restricted operation through another worker, model, account, or backend. Hard budgets, explicit stops, and unresolved holds take precedence over replenishment.

MEASUREMENT AND EFFICIENCY

Measure progress against the original requested outcomes. For tests, distinguish unique valid passes and failures from setup errors, cancellations, retries, source-review dispositions, reduced diagnostics, and deferred work. Preserve original failures after successful corrections.

Track elapsed time from run start, setup and active service, cumulative and recent useful-result throughput, dispatch latency, avoidable idle time, bottlenecks, restart waste, and remaining coverage. Report model usage or cost only from available telemetry and identify gaps.

Explain unexpected idleness, task selection, deferral, and preemption in concrete terms. Use compact events, bounded context, incremental reports, and concise updates. Keep routine scheduling out of the main model's conversation loop and avoid synchronous hooks that perform long-running control work.

Treat user-provided timing and throughput goals as measurable objectives, not guarantees or reasons to weaken acceptance. Report infeasible targets and actual bottlenecks while continuing useful work within the authorized budget.

VALIDATION AND ACCEPTANCE

Discover and preserve the kit's actual test and example entrypoints. Add meaningful deterministic scheduler tests, controlled subprocess tests, and a bounded live agent-backend test. Label simulation, real process execution, and real model integration separately.

Cover:

- Slow work followed by newly ready fast work, worthwhile preemption, justified nonpreemption, and eventual progress on expensive work.
- Unknown durations, stale estimates, progressive service, shared setup, dependency fan-out, continuous arrivals, and avoidance of thrashing and starvation.
- Partial outputs releasing only actual dependents and unrelated work continuing during slow preparation or review.
- Actual worker and subprocess admission paths, nested delegation, retained resources during suspension, exclusive outputs, cold-start ramp-up, throttling, and recovery.
- Dependency cycles, resource deadlocks, duplicate and out-of-order events, cancellation races, concurrent controller starts, crash boundaries, surviving processes, and late results.
- Invalid timing, reduced diagnostic coverage, setup failure, actual test failure, holds, hard budgets, persistent user stop, and preserved repair history.
- Historical-record compatibility, installer upgrades, preserved configuration, source/install parity, repeat-install idempotence, and safe disable/uninstall behavior.

Benchmark against matched FIFO and fixed-batch scheduling on representative mixed workloads using identical resources. Include nonpreemptible work, setup costs, and poor estimates. Measure early useful results, completion over time, total completion time, dispatch delay, overhead, idle resources, and wasted interrupted work. Establish testable targets and tolerances before measuring, investigate regressions, and avoid tuning only one favorable fixture.

The live test must demonstrate actual dispatch, observation, result ingestion, automatic replenishment, and supported interruption/recovery behavior on a bounded workload. A simulated adapter cannot establish this, and a separate thread pool cannot establish integration with a native subagent tree.

Require independent review of consequential scheduling, concurrency, recovery, authorization propagation, evidence accounting, and packaging. Resolve material findings using actual code and evidence.

INSTALLATION AND DELIVERY

Update implementation, policy, role guidance, documentation, tests, and examples coherently. State what code enforces, what depends on backend capabilities, and what requires agent judgment.

Inspect packaging and installer assumptions rather than merely adding source files. Include required modules, adapters, hook definitions, and dependencies through a tested upgrade path. Preserve installation ownership checks, unrelated configuration, and historical evidence.

Preview and apply the source installer in the authorized target environment, verify source/install parity, and verify that a repeat preview makes no changes. Respect product-required trust steps and report any remaining activation requirement precisely. Do not silently enable a controller for unrelated tasks. Explain when a fresh chat is required.

Deliver working source, validation evidence, benchmark results, installation status, a minimal quick-start, self-contained examples, and restart/operating instructions. Explain how to inspect decisions, pause, resume, recover, and distinguish completed work from deferred coverage. Report source revision and dirty state, validation, installation, and commit/push status separately.

Proceed through implementation and acceptance rather than stopping at a plan. Complete independent authorized work even when one integration requirement is blocked. Do not mark the solution complete while dispatch is only advisory, required live behavior is unverified, or recovery can silently duplicate work or erase evidence. Report genuine limitations explicitly.
