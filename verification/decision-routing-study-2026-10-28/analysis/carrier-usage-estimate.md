# Carrier assignment-derived usage estimate

Phase proof: `locked/E2-lock.json` records all four responses submitted before estimation. These are hypothetical inference volumes, not observed usage or a claim the work ran. The locked first two hours plus developments do not resolve how much initial work completed; ranges assume meaningful initial progress, and actual overlap could lower the totals. No full restart is charged for E1 or E2.

| Participant | Read-only planned base, USD low–high | Low with no cache | Additional future-work reserve, USD low–high | New conversations, base |
|---|---:|---:|---:|---:|
| p17 | $0.83–$9.08 | $1.69 | $0.08–$1.12 | 6 |
| p43 | $0.78–$8.34 | $1.53 | $0.10–$1.10 | 7 |

Base includes queued read-only work and the E2-triggered Astra consultation. Future fixture/campaign and independent artifact review are in the additional reserve, subject to authorization and prerequisites; summing every reserve assumes all execute and is not a forecast. P17 A8 becomes queued diagnosis at E1; A10 becomes active at E2. P43 A1 becomes active at E2; L5, L6 and R1 remain contingent. P43 T3 is included for E1/E2 interim reporting, not an assumed completed future campaign. No stopped assignment was identified. The separate ADMIN-COORD row covers scheduling and handoffs outside explicit synthesis/screening assignments, based on stated reuse and six-slot concurrency.

Rows, phase increments, sources, request counts, model totals, new/reused requests, token components, cached subsets and no-cache sensitivities are in the accompanying JSON. Initial/continuation increments estimate actual source reads and tool cycles, synthesis, independent challenge or discriminators; future implementation rows allow bounded verification and repair, without assuming a repair occurs. Source byte sizes approximate input, not actual tokenization. First request in each new conversation is cold; low endpoint permits up to 80% cached shared-prefix input on subsequent requests; high is cold. Payload/history includes repeated context.

For each row, low input = 16,000 × low requests + 0.20 × excerpt bytes rounded up + 700 × low requests; high input = 48,000 × high requests + 0.75 × excerpt bytes rounded up + 2,200 × high requests. Output is 450–1,400 tokens per request including unknown reasoning. The shared context C is unmeasured, not a floor or guarantee: substitute C × requests + payload/history to explore alternatives. The approximately 85 KB / 11.5k-word extra full policy and role/tool harness can put real overhead outside this sensitivity range.

API comparison uses the supplied rates verified 2026-10-28 from [OpenAI pricing](https://developers.openai.com/api/docs/pricing), USD per million input/cached/output: Luna 0.10/0.01/0.50, Terra 1/0.05/5, Sol 2/0.10/10, Astra 10/1/50. Cost = ((input − cached) × input rate + cached × cached rate + output × output rate) / 1,000,000. These are tier comparisons, with no changes to settings. Model pins remain Terra high, Luna high, Sol ultra and Astra medium.

No weekly conversion is supported: the user-reported unitless Terra 1 / Sol approximately 10 / Astra approximately 20 indices concern included allowance, Luna is unknown, and none is calibrated to this work. API dollars and paid credits are separate.
