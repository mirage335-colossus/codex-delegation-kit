# Autonomous scientific research: retained lessons

This directory preserves knowledge useful for improving automatic scientific
research and development uptake. At the user's request, the recent commit was
replaced to remove third-party payloads and historical replay archives. See the
[retention boundary](RETENTION.md) and [lessons learned](lessons-learned.md).

The installed implementation is in the repository's current policy, role prompts
and backend/installer code. This study is source-only learning material.

## What the exercises established

Ordinary development requests did initiate substantial research, independent
criticism and concrete development uptake in the tested environments. Reference-level
breadth/depth, reliable automatic selection in ordinary installed-app chats,
causal improvement, and cost savings remain unproven. Model instructions express
expected behavior; they are not runtime enforcement.

| Episode | Supported depth judgments, out of 48 | Outcome |
| --- | ---: | --- |
| [D1](evaluation/development-d1/result.md) | 16 | All eight domains Partial |
| [D2](evaluation/development-d2/result.md) | 24 | All eight domains Partial |
| [D3](evaluation/development-d3/result.md) | 23 | All eight domains Partial |
| [D4](evaluation/development-d4/result.md) | 22 | All eight domains Partial |
| [Explicit-research control](evaluation/positive-control-v4/result.md) | 25, plus one Supported boundary | All eight domains Partial |
| [D5](evaluation/development-d5/result.md) | 23 | All eight domains Partial |
| [D6](evaluation/development-d6/result.md) | 25 | All eight domains Partial |
| [Actual-primary V6](evaluation/primary-scientific-v6/operation-02/result.md) | 20 | All eight domains Partial; uptake supported |
| [Actual-primary V7](evaluation/primary-scientific-v7/operation-01/result.md) | 28 | All eight domains Partial; uptake passed |
| [Actual-primary V8](evaluation/primary-scientific-v8/operation-01/result.md) | 25 | All eight domains Partial; uptake passed |

These dependent development episodes are coverage observations, not independent
trials or evidence of causal improvement/regression. The
[reference calibration](evaluation/reference-self-test/result.md) reached seven
complete domains and 47/48 adjudicated depth judgments; it was not autonomous
research and did not replace the original passing standard.

The final [V9 matched design](evaluation/groundwave-matched-v9/decision.md) produced
unequal endings: ordinary development completed, while the research case stopped
at a runtime guard. Its [runtime diagnosis](evaluation/groundwave-matched-v9/review/r-case-runtime-hold-diagnosis.md)
and [qualitative closeout](evaluation/groundwave-matched-v9/review/retained-work-qualitative-closeout.md)
retain useful observations but establish no valid scientific-depth contrast.
The user stopped further campaigns because their cost and duration had become
disproportionate. No further scientific exercise was run for this cleanup.

## Material to reuse

- [Evaluation criteria and domain maps](evaluation/baseline/acceptance.md),
  [comparison matrix](evaluation/baseline/coverage-matrix.json),
  [ordinary tasks](inputs/tasks/), and [study protocol](evaluation/protocol.md).
- [Discovery-before-closure diagnosis](evaluation/strategic-diagnosis.md),
  refinement proposals under `evaluation/`, and the
  [experimental redesign](evaluation/experimental-redesign-2026-11-15.md).
- Domain reviews linked from the outcome reports, including failed judgments,
  independent critique and separate uptake findings.
- [V9 source review](evaluation/development-v9/source-review.md) and
  [source closeout](evaluation/development-v9/source-closeout.json), whose test
  counts are historical source checks, not scientific attainment.
- [Deduplicated prompt variants](prompt-history/versions.json) and
  [native harness implementation references](harness-reference/README.md).

The small retained helpers use only the standard library. Their isolated tests
can be run from the repository root:

```sh
python3 -B -m unittest discover -s studies/autonomous-scientific-depth-2026-11-14/tools -p 'test_*.py' -v
```

Reports retain their original grades, reasoning and caveats. Their retention
notices qualify historical preservation claims and omitted evidence locators.
They do not promise byte-complete archives or historical replay.
