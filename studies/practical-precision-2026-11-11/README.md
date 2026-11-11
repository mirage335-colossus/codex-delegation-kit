# Practical arithmetic precision — November 11, 2026

The retained recommendation is to start practical numerical work at the lowest
useful precision and make automatic mode prioritize qualified, sustainable
capacity on demanding workloads. Higher precision needs a practical benefit or
an explicit requirement. The exercises refined how directly that priority must
be stated; they do **not** establish a broad improvement in agent reliability.

## What changed

The [final prompt](prompt-v2.txt) explicitly makes automatic mode the user's
maximum-useful-processing option. It requires considering headroom before a
backlog forms, comparing complete algorithms, raising precision locally, checking
actual arithmetic instructions, and preserving a simple precision override.
Neither FP64 agreement nor an invented universal dB loss becomes an automatic
acceptance gate. Exact requirements and qualification remain binding.

The canonical source [policy](../../policy.md#practical-numerical-precision)
contains this guidance, with prominent README/AGENTS summaries. Nine native role
files and the controller's common instructions carry a shorter reminder; that
reminder was checked for delivery but was not independently behavior-tested.
The prompt-only initial Astra role remains unchanged. Existing phrases that
could imply preserving all existing numerical precision were clarified.
The twenty-three-file runtime inventory and all model/effort pins are unchanged.

Only the source checkout was updated. No global installation, pumpModem edits,
publication, commit or push was performed. Source baseline:
`81556e2240af6bad5c9240ffb6d49e2d880a7f5e`, initially clean. Study files are clone-only
research artifacts, not another runtime bundle or coordination registry.

## Motivating evidence

[Source excerpts](source-chat.json) retain six recent turns from **Connect Robust
modem GUI features**, chat `01a1c4c0-c110-76c1-aebe-036f4345ca41`, read through the
Codex chat tool. This preserves the user's successive corrections and assistant
final reports, rather than every tool call or the whole historical conversation.

The user repeatedly redirected decisions from an agent-authored FP64 score
tolerance to reception quality, wider searches, workspace capacity and avoiding
backlog. They rejected replacing a ppm criterion with another universal 1 dB
criterion, and asked agents to investigate why hardware-supported lower precision
was not yielding arithmetic gains. They emphasized automatic selection because
users cannot tune all processing stages themselves.

The final assistant report distinguished a 3.85× FP64 chirp-Z algorithm win over
a Q15 route from a 1.15× isolated packed-arithmetic gain and a larger Radeon
algorithmic gain. It retained uncertain sensitivity coverage and a weak-signal
miss. These are historical reported observations, not independently repeated
measurements. They motivate comparing useful complete work instead of bit width.
The user's proposed explanation about model training is not established here.

## Frozen development comparison

[Protocol](protocol.md), [cases](cases.json), [rubric](rubric.json),
[original answers](results/development-answers.json) and
[arm map](arm-map.json) retain the comparison. Each of three pairs used one fresh
Luna-high scout per arm, requested through the pinned role, the same policy
excerpt and scenario, and a 650-word limit. Only treatment received
[v1](prompt-v1.txt). Source files were not changed until these agents and the
transfer pair had finished. Native task-level masking is not OS isolation;
resolved model telemetry, token usage and comparable cost were not independently
captured. No cost or speed advantage for the agents is claimed.

| Scenario | Existing guidance | v1 | Independent semantic assessment |
| --- | --- | --- | --- |
| Modem score gate / arrival deadline | Q15; diagnostic gate | Same | 4/4 each |
| Particle capacity / missing packed arithmetic | Automatic capacity; investigate instructions | Same | 4/4 each |
| Faster FP64 algorithm / local wider accumulation | Chirp-Z; mixed reducer; exact counter | Same | 3/4 each |

Both arms made all six expected discrete choices. These are three pairs, not
six independent trials per arm. An arm-blinded Sol review found no severe error;
both counterexample answers incompletely specified the simple reference override.
Both modem answers scoped further qualification but gave no numeric sample budget
or stopping rule. The frozen rubric did not require those numbers.

The case wording strongly cued the expected choices. This is a null result on
these supplied facts, not evidence that the historical difficulty was reproduced
and cured. Both particle answers chose FP32 whenever it could meet the current
deadline, extrapolating a small easy-case observation into a broad dispatch rule.
That passed the frozen criterion of automatic access to the demanding route;
it suggested clarifying that unrequested idle efficiency should not trade away
headroom. v2 makes that priority and the override explicit. The full blinded
review is retained in [development-review.md](results/development-review.md).

r05 initially stopped before reading its packet because the fresh context omitted
standing role authorization. The coordinator supplied the already-existing policy
authorization to the same agent, with the same remaining budget and no feedback
on its task answer. [The original interruption](results/r05-interruption.txt)
is retained. This extra context limits how tightly matched that pair was.

## Executable transfer and adaptive diagnostic

The [transfer task](transfer-task.txt), template and
[12-check evaluator](evaluate_transfer.py) were frozen before v2 was written.
Two fresh Luna-high workers edited separate selectors using identical synthetic
observations and interface constraints; one received existing guidance, the other
existing guidance plus v2. This is one selector exercise covering two application
settings, not two independent application benchmarks. Both workers ran their own
checks; the coordinator executed the protected checks afterward.

**Both passed 12/12 frozen checks.** Those checks cover demanding-case capacity,
capability and qualification, memory boundaries, minimum precision overrides,
explicit error requirements, a higher-precision algorithm winning, exact large
integer IDs, input preservation and reordered inputs. See
[t01](results/t01-evaluation.json) and [t02](results/t02-evaluation.json).
No hidden-check repair was made. The v2 worker's initial package import failed
before assertions; its corrected file-based check passed. The
[execution notes](results/execution-notes.md) retain that setup failure.

Inspection found a consequential difference despite the tied scores:

- Existing guidance produced a new balanced score combining normalized idle
  latency and demanding capacity, although the user had supplied no such weights.
- v2 selected highest qualified demanding capacity, using idle latency for ties.

The [supplemental diagnostic](supplemental_diagnostic.py) was designed **after**
reading both implementations. It supplies two qualified routes: 80 useful jobs/s
at 0.8 ms idle latency, and 85 jobs/s at 0.9 ms. Existing-guidance code selects 80;
v2 code selects 85. Swapping their precision labels leaves those choices intact.
The [raw result](results/supplemental.json) demonstrates this implementation-level
mechanism, not a fresh holdout or an unbiased prompt-effect estimate. These are
synthetic numbers, not a measured 6.25% application speedup.

This supports retaining the more explicit recommendation for the user's stated
objective, while leaving broad behavioral effectiveness unproven. It does not
justify a universal lowest-bit rule, adopting unqualified paths, relaxing exact
contracts, or keeping hardware busy without useful work. No further prompt tuning
was performed on the transfer or supplemental outcomes.

## Reproduce and verify

```sh
python3 -B studies/practical-precision-2026-11-11/evaluate_transfer.py studies/practical-precision-2026-11-11/transfer/t01/selector.py
python3 -B studies/practical-precision-2026-11-11/evaluate_transfer.py studies/practical-precision-2026-11-11/transfer/t02/selector.py
python3 -B studies/practical-precision-2026-11-11/supplemental_diagnostic.py
```

`development-freeze.json`, `transfer-freeze.json` and `v2-freeze.json` retain SHA-256
digests. The native experiment invocation messages/results remain in this chat;
archived JSON preserves answer fields/text with normalized formatting. Common
role/system instructions may affect both arms. The source prompt-delivery patch
was applied only after participant work finished, preserving the shared baseline.
The full production application, sustained workloads, hardware dispatch and long
agent sessions were not exercised. Independent review covers source and claims;
it does not turn synthetic selector outcomes into those missing measurements.

Relevant primary references: [OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
supports task-specific criteria and retaining comparisons rather than relying
on impressions. [AMD's FP16 article](https://gpuopen.com/learn/first-steps-implementing-fp16/)
illustrates compiler/instruction verification and conversion overhead; its
toolchain advice is dated. [CUDA WMMA documentation](https://docs.nvidia.com/cuda/archive/13.3.0/cuda-programming-guide/05-appendices/cpp-language-extensions.html)
separates operand from accumulator types. These sources inform checks; none sets
a universal acceptable error threshold or proves a modem speedup.
