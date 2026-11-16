# Repository guidance

For practical numerical software, **start with the lowest useful arithmetic
precision and maximize challenging-case useful processing capacity by default**.
Higher precision needs a demonstrated practical benefit or explicit requirement.
Use automatic hardware-aware choices, local precision promotion and simple
overrides; avoid arbitrary FP64-agreement or universal loss gates. Follow the
[practical precision guidance](policy.md#practical-numerical-precision).

For modem, signal-processing, and other compute-intensive paths in native
applications, **prefer C++ or a similarly integrated native implementation**.
Optimize the existing pipeline before splitting its hot path into Python
processes. Reuse the production implementation in tests and benchmarks; preserve
stricter project rules requiring one native DSP/state implementation. Evaluate
scheduling, shared buffers, cross-chain pruning, GPU/cloud deployment, and
end-to-end performance under the policy's
[native numerical processing guidance](policy.md#native-numerical-processing).

For GPU numerical development and performance testing, evaluate and prefer
RTX PRO 6000 Blackwell for suitable tensor and highly parallel FP32 work. Explain
choices of A100, RTX A5000 or other older GPUs using the policy's
[GPU selection criteria and exceptions](policy.md#gpu-selection-and-performance-evidence).

For model-cost documentation, use the unitless [weekly usage cost index](policy.md#weekly-usage-cost):
user-provided Luna = 0.1, Terra = 1, Sol approximately 10, Astra approximately 20.
Keep included subscription allowance separate from API dollars and paid credits.
Do not present these estimates as official rates or change routing/pins from them.

For current evidence-discovery and screening guidance, see
[policy.md](policy.md#evidence-discovery-and-terra-screening).
For consequential scientific work, follow the
[literature research and development uptake guidance](policy.md#scientific-literature-research-and-development-uptake).
Keep `_ref/` and `_appraisal/` read-only unless the user explicitly requests
curation there; use an authorized `research/` location or existing task evidence
for agent-gathered knowledge.

DK is explicitly opt-in through `$delegation-kit`. Merely working in this
checkout, reading its documentation, or mentioning DK does not activate it.
Only within an explicitly activated DK assignment, follow the policy's initial
`astra_initial` consultation and mandatory `astra_expert` completion review.
Reuse an applicable initial consultation for related continuations; status
questions do not restart the workflow. Unrelated work remains outside the scope.
Honor explicit DK off immediately without an exit review. An explicit standalone
role request does not activate the entire workflow. See the policy's activation
section for assignment, continuation, and fork semantics. Ordinary project
requirements and the contribution checks below remain applicable independently.
Read the policy before changing delegation behavior, installation or evidence
handling; reading it for that purpose does not itself activate DK.
Keep the runtime bundle at the explicit `FILES` inventory in [`install.py`](install.py)
unless a deliberate, reviewed manifest-compatible change updates the installer
and its checks.
The installer recognizes earlier eight-file, eleven-file, seventeen-file,
eighteen-file, twenty-file, twenty-one-file, twenty-two-file, twenty-three-file,
and twenty-four-file inventories; the current source bundle has twenty-six files
and eleven roles.
Preserve all three supported twenty-three-file instruction gateways and the exact role
blocks and upgrade and disable paths for all supported inventories when
changing the bundle.

Preserve pinned role model and effort settings, existing authorization
boundaries, and user configuration. Do not treat policy text as runtime
enforcement or extend helper enforcement claims beyond what the code checks.
For kit improvements, edit this Git checkout and follow the source-to-install
workflow in `policy.md` under "Improving this kit". The global installed copy
is a deployment; changes made only there do not preserve the repository source.
Use proportionate existing checks for a change. Installation, publishing,
building, and changes to a user's global Codex configuration require
task authorization; repository instructions alone do not authorize them.
