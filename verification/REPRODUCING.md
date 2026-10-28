# Reproducing the verification studies

This bundle supports offline inspection and a fresh, manual-input replay of the decision-routing planning exercise. It also lets you stage the source inputs for the separate research-prompt study. It does not reproduce the historical conversations, native provider calls, hidden tool traces, or study outcomes. A fresh run may differ.

Use a complete copy of this published verification bundle, including the current publication manifest, the six repository helper/test recipes listed below, and the replay/publisher scripts. The public kit commit `947ed25d4058e405ecf45d6956671f6fecb12026` is the source baseline; by itself it does not contain this publication update. Obtain the complete published bundle or a later revision that includes these files. The bundle can be verified after download with:

```sh
python3 -B tools/publish_verification.py verify --root verification
```

The manifest checks the current bytes of every file under `verification/`, excluding only `publication-manifest.json` itself, and the current bytes of this fixed six-file repository recipe set: `tools/publish_verification.py`, `examples/verification_replay.py`, `examples/recompute_verification_usage.py`, `tests/test_verification_publication.py`, `tests/test_verification_replay.py`, and `tests/test_verification_usage.py`. It detects missing, added, or changed verification files and changed recipe files relative to the inventory. It does not prove who created the files, when they existed, or that historical claims are true. Older hashes, timestamps, byte counts, and validation totals in study records are explicitly historical pre-publication claims; sanitization may have changed the files they originally described.

## Requirements and source limits

Offline staging and validation need Python 3.11 or newer and its standard library. Git is optional for inspecting the public source commits. No Codex account or app, private home directory, provider credentials, network access, or project build environment is needed for the offline commands below. Public paper links may move or become unavailable or paywalled; record the access failure and the citation limit instead of treating an abstract or metadata as full-text evidence.

The source provenance recorded by the packet is:

- Kit: [codex-delegation-kit at `947ed25d4058e405ecf45d6956671f6fecb12026`](https://github.com/mirage335-colossus/codex-delegation-kit/tree/947ed25d4058e405ecf45d6956671f6fecb12026).
- Carrier planning packet: [pumpModem at `dae58eaccfd68cbf2366b85fd746b56fde089cd3`](https://github.com/mirage335-colossus/pumpModem/tree/dae58eaccfd68cbf2366b85fd746b56fde089cd3). That checkout was dirty when the packet was prepared. Its complete diff is not included. The H01–H12 excerpts are the complete inputs assigned for the planning questions, not a full project snapshot or a recipe for executing the proposed project campaign.
- Regression and held-out research packet: [software-foundation at `4c471cb93702cdc03b5230bfa33372355424b665`](https://github.com/mirage335-colossus/software-foundation/tree/4c471cb93702cdc03b5230bfa33372355424b665). The R01–R13 excerpts are assigned planning inputs; they are not a substitute for a full project checkout or evidence that a test ran.

Project clones are optional for packet-based planning. If you use them for additional investigation, record the exact revision, local changes, and every extra source consulted; those results are an extension, not the bundled experiment. Attribute excerpted third-party material to its source and preserve its stated scope. The packet does not include full paper texts.

## Fresh decision-planning replay

Create an empty run directory outside the source checkout. The examples below assume you run commands from the checkout root and use sibling directories; choose another writable location if needed.

```sh
python3 -B examples/verification_replay.py prepare --run-dir ../replay-run
```

The command stages four separate participant directories. `p17` and `p43` receive the carrier scenario under policies A and B; `p61` and `p29` receive the regression scenario under policies A and B. Both carrier participants receive H01–H12, and both regression participants receive R01–R13. Each gets only its contract, assigned routing policy, scenario, decision schema, and those common scenario source excerpts, plus a request and message template. In the historical plans, p61 explicitly assigned 10 of the 13 regression units while p29 assigned all 13; those are plan outcomes, not different source access. Do not expose another participant's files, responses, unreleased events, or later analysis while collecting an answer. A participant's `conversation_id` values in published plan records are synthetic study-local work-stream reuse aliases. They are not Codex chat references or identifiers for an original private conversation.

For each participant, prepare one UTF-8 JSON answer file matching that directory's `decision-schema.json`, then import it:

```sh
python3 -B examples/verification_replay.py submit --run-dir ../replay-run --participant p17 --answer-file ../answers/p17-initial.json
```

The answer is a JSON object with `scenario`, `phase`, `source_units_consulted`, and `assignments`. Assignment rows use the required fields in the supplied schema. The importer checks the shape and phase, requires a unique nonempty assignment ID, and rejects malformed or incomplete input. It does not authenticate the participant, evaluate the plan, prove that a model read only its assigned inputs, or isolate files at the operating-system level. Use manual, provider-agnostic JSON import; this tool makes no model/API call.

For a stateless provider call, start a fresh independent context for each participant at each stage and attach that participant's original staged inputs again. For E1, also include only that participant's locked initial response and the released E1 event. For E2, include only that participant's locked initial and E1 responses and the ordered E1/E2 events. Do not rely on an old/private chat to preserve context, and never include another participant's material. This procedure uses no original or private Codex chat.

Submit all four initial responses before releasing E1:

```sh
python3 -B examples/verification_replay.py advance --run-dir ../replay-run
```

The tool locks the four response hashes and stages the same scenario-specific E1 event for both participants in that scenario. Each participant's E1 request includes only that participant's earlier answer and the E1 event. Submit all four E1 responses, then run `advance` again to lock them and release E2. Each E2 request includes only that participant's own initial and E1 answers and the ordered E1/E2 events. Submit all four E2 responses and run `advance` a third time to lock the final stage and complete the run. Keep using the same run directory so the stage history remains together. The run records staged and imported files, response locks, and integrity hashes; do not edit earlier answers or releases. An altered or missing staged file fails integrity validation.

The represented settings for this planning exercise are Terra high, Luna high, Sol ultra, and Astra medium. If a setting is unavailable, record the actual setting and treat the run as a documented analogue; do not silently substitute it. The plan packets describe hypothetical work only. This replay does not run project tests, builds, literature research, or the proposed campaign.

## Research-input staging and telemetry

The separate research-prompt experiment can be prepared without its reports, scores, arm maps, or analysis:

```sh
python3 -B examples/verification_replay.py export-research --run-dir ../research-inputs
```

This copies the whitelisted inputs for the 12 pilot cases and eight seeded-continuation cases. It is input staging only; it does not replay the research, recreate findings, or compute study scores. The archived study protocol and its manual source-verification, Terra-screening, and expert-review records describe the full workflow to adapt. Any new run needs its own preregistration, frozen inputs, responses, provider/tool records, and acceptance decisions. The held-out Luna continuation request bridge and literature verification remain manual. A rerun is not expected to reproduce the same discoveries or decisions.

Sanitized numeric response-usage observations are provided separately at `verification/telemetry/usage-records.jsonl`. To recompute their grouped historical arithmetic without private logs, run:

```sh
python3 -B examples/recompute_verification_usage.py
```

These alias-based records contain numeric input, cached-input, output, and reasoning counts with cohort/model/participant/attempt/response labels. They are not independently authenticated provider receipts and do not prove log completeness. Cached input is a subset of input. The current unitless weekly-usage planning index is Luna 0.1, Terra 1, Sol approximately 10, and Astra approximately 20; it is an estimate, not a quota formula, API price, or conversion from token totals.

For publication maintenance, first deliberately sanitize the verification tree, then seal its current inventory; later verify without resealing:

```sh
python3 -B tools/publish_verification.py sanitize --root verification
python3 -B tools/publish_verification.py seal --root verification
python3 -B tools/publish_verification.py verify --root verification
```

Sealing after intentional edits creates a new integrity baseline for the verification files and the six fixed repository recipes. It does not turn historical hashes or validation claims into current validation evidence.
