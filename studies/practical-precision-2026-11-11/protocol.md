# Practical precision prompting — frozen development protocol

Source: `81556e2240af6bad5c9240ffb6d49e2d880a7f5e`, initially clean.
Date: November 11, 2026. Source conversation: `source-chat.json`.

Objective: test whether guidance changes autonomous engineering choices toward
useful processing capacity, low practical arithmetic precision, and automatic
hardware-aware defaults without inventing precision requirements or ignoring
explicit ones. The user's theory about model training is not tested.

Three matched development pairs use fresh `luna_scout` contexts, requested Luna
high, with the same case, common instructions, role, and response budget. The
baseline is the frozen relevant policy excerpt; the treatment adds `prompt-v1.txt`.
Participants receive no source chat, rubric, other answers, or proposed policy
patch. They may read only their supplied packet and return at most 650 words of
JSON decisions/rationale. No recursive initial/completion consultation applies.
These are decision exercises with synthetic supplied observations, not measured
hardware benchmarks or production qualification. The surrounding native role and
system instructions are common; fresh context does not prove total isolation.
Requested pins do not establish resolved runtime telemetry.

Freeze prompts/cases/expected decisions before dispatch. Preserve every original
answer, including null/negative outcomes. Score the six predeclared decisions and
the following behaviors independently of arm labels: objective fidelity, concrete
action, actual arithmetic versus storage, proportionate local promotion, automatic
selection/user burden, and honest evidence limits. Do not reward precision words
or intentions alone. A reviewer receives anonymous answers and case facts, with
no treatment labels. Small samples and model nondeterminism limit causal claims.

Refine once from observed weaknesses and independent review. Then freeze two
fresh transfer cases in an executable selection fixture, with the same synthetic
observations, interfaces, protected evaluator and run budget in both arms.
Participants implement a selector used by that fixture; passing establishes
executed selection behavior only, not actual DSP speed, sensitivity or broad agent
reliability. Reserve a control where higher precision or an explicit contract
must win. Report development and transfer separately; do not tune on holdout
results and continue calling them holdouts.

The delivered source guidance will be compact and applicable to practical
numerical work. Preserve runtime inventory, role pins and authorization. No
pumpModem source edits, cloud work, publishing, global install or commit are part
of this study. Documentation links/diff and existing distribution checks are the
proportionate source checks. Additional prompt-delivery surfaces, if changed,
also require existing backend/role checks.
