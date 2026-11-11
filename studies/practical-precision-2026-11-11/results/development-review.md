# Arm-blinded Sol assessment

Reviewer: existing `exercise_review` Sol-ultra adviser, given only cases.json,
rubric.json and opaque r01–r06 responses. It had reviewed the experimental design
but was not given arm maps, prompts or packets for scoring. No claim of complete
independence from the study design or OS-enforced blinding.

All six responses made both expected mechanical decisions. No severe errors.
Each scenario pair tied on the frozen semantic criteria.

| Responses | Mechanical | Semantic | Findings |
| --- | --- | --- | --- |
| r01, r04 | 2/2 each | 4/4 each | Automatic demanding route, reference override, no energy requirement, actual instructions distinguished, no promised speedup. |
| r02, r05 | 2/2 each | 4/4 each | Failed diagnostic retained, no unsupported 1 dB gate, deadline and reception tradeoff, uncertainty and scoped qualification. No sample budget or stopping rule, but those were not specified by frozen rubric. |
| r03, r06 | 2/2 each | 3/4 each | Complete algorithm cost, wider accumulation locally, exact uint64. Simple reference override incompletely specified. |

The easy-case FP32 dispatch preference is a refinement opportunity, not a failure
under the frozen automatic-access criterion. Both answers generalize a single
easy-scene result into a broad preference. The scenario wording strongly cues
mechanical answers; the supplied-cost counterexample is a direct comparison.

Later unblinded conceptual review endorsed keeping v2 for the user objective,
while requiring plain reporting of the frozen 12/12 tie and post hoc synthetic
discriminator. It advised qualified sustainable capacity within reception,
deadline/backlog and resource constraints, and no inferred global activation.
