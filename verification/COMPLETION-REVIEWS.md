# Completion reviews: bounded evidence and useful next steps

This clone-only guide helps maintainers review evidence before stopping a substantial task and identify a small authorized next step. It defines no runtime schema or controller and cannot establish that a model will follow prose guidance. Treat each scenario as a semantic regression prompt, retaining uncertainty where evidence is missing.

## Review the task as it was authorized

Read the request, relevant project instructions, source and dirty state, and actual evidence. Separate hard requirements from adjustable choices and assumptions. Identify available inputs, executable entry point, interpreter, and capabilities. An example, proposal, remembered convention, or prior run is neither authorization nor a current result.

Record stable inputs, source revision and changes, commands, environment, assertions reached, and outputs. When setup fails before assertions, report zero assertions for that check, preserving earlier coverage. Retain the setup failure, repair a verified prerequisite when in scope, and rerun boundedly. Keep skipped, unexecuted, queued, interrupted, and failed checks distinct from passes. Loading a fixture or preparing inputs does not show that a recommendation or application behavior worked.

Compare actual inputs and conditions, not just output labels or equal numbers. Distinguish public runtime output, private oracle/ground truth, evaluator measurements, and forecasts. A bounded result does not prove broad reliability, deployment readiness, or end-to-end success.

## Bounded semantic regression scenarios

These examples are prompts, not a checklist or quota.

1. **A hard constraint is contaminated by another task.** A prior project asked for at least 10,000 cycles; the current user explicitly requests a 2,000-cycle diagnostic and says not to reuse the other project's floor. The reviewer should preserve the current user's bound, distinguish it from historical context, and proceed within the authorized diagnostic. Do not silently import the old threshold or relax a current hard requirement to make a candidate fit.

2. **A source archive is unavailable, but a local discriminator is runnable.** The full historical archive cannot be fetched, while the supplied finite fixture and documented local entry point can separate the two live hypotheses. The reviewer should record the archive limitation, use the local discriminator only for the claim it supports, and keep broader historical or production claims unverified. Do not block useful bounded work solely because a larger source set is unavailable.

3. **A known interpreter failure occurs before assertions.** A small check fails because the selected Python lacks a required package; no assertion starts. The reviewer should label this as setup failure with zero assertions, verify the package or supported interpreter, and rerun the same bounded check. Do not report a product failure, a pass, or a completed validation based on test discovery alone.

4. **Work is coupled under a fixed output and resource envelope.** The task has interdependent cases, a fixed number of outputs, and limited memory. The reviewer should reason conditionally about feasible batching and concurrency, preserve required outcomes and the resource bound, and state the few alternatives that materially change feasibility. Do not hide extra batches, reset limits between phases, or trade away duration, energy, sensitivity, or required cases without authorization.

5. **A private evaluator is mistaken for a public result.** A private projection or oracle says a candidate has a certain score, while public execution only produced raw output and a forecast estimates future performance. The reviewer should label each source correctly, retain the public output as observed, and avoid attributing private evaluator values to the runtime. If a claim depends on a matching input, compare the actual input bytes or a reliable identity record; similar results alone do not establish input equality.

6. **A limit is near while one authorized check remains.** A required bounded check remains feasible and authorized near the execution limit. Reserve capacity to finish it and report evidence or a concrete blocker. If the remaining budget cannot cover it, respect the limit and return the exact unfinished check; a new phase or batch cannot reset the allocation. Do not ask the user to close already authorized work or spend the remainder on avoidable handoffs or checks that cannot resolve the uncertainty.

7. **Cached usage is used to claim workflow savings.** One approach reports fewer uncached input tokens, but used extra actors, execution groups, retries, or helper work. The reviewer should compare whole-workflow cost and time using explicit units and include orchestration, cached and uncached input, output/reasoning, setup, and repair where available. Do not infer savings from one token row, agent count, or a rough model index alone; distinguish measured usage from an estimate and note missing telemetry.

## Evidence behind the examples

An initial generic cue did not elicit the needed scale reasoning. A revised cue improved explanation, but the first fixture confounded cases and could not execute the recommendation; that defect was corrected before a fresh paired trial. In the runnable finite synthetic receiver trial, both versions independently narrowed internal configuration while preserving fixture duration, bit count, signal power and noise realization, then executed the receiver's complete hypothesis search. The revised version explained its quantitative reasoning better but did not add execution success. Both actors exceeded the six-execution-group limit by using seven groups. One actor mislabeled a private evaluator measurement as public receiver output; the other left input-identity verification blocked by its interpreter. Parent-level verification later established matching inputs without crediting either child with that work. This supports selective generic guidance improvements, not a reliability or cost claim: the small bounded run was not a matched model-cost study and did not qualify real hardware or production.

## Comparing guidance prospectively

For a behavioral comparison, freeze prompt, inputs, tools, environment, and criteria before seeing either response. Preserve original outputs and case provenance. Validate the fixture and harness first. If a defect invalidates both arms, mark the comparison invalid, repair, and rerun both under the same conditions. If it affects one arm, preserve the failure. Do not coach an arm with hidden answers or oracle labels.

Judge behavior and evidence separately: a stronger explanation may add no successful execution, while execution counts can miss constraint errors. Record changes, failures, unexecuted work, and limits. A small pair may motivate selective generic wording, but does not qualify deployments or prove universal gains. Static checks verify text and links, not model behavior.

State outcome, evidence, limits, and any remaining authorized next step; continue it when feasible. Otherwise summarize what passed, failed, and was not run. See [OpenAI's evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) for evaluation design concepts; no platform or API is required.
