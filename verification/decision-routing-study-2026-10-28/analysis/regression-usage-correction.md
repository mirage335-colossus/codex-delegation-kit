# Regression review-accounting correction

P29 P09 explicitly includes independent review of any eventual patch, but the original estimate's P09 basis and 4–8 request budget describe consequential decision review only. P12's handoff is from the repair author and does not itself account for independent acceptance review. P61 separately budgets that work in A10. The original estimate and planned assignments remain unchanged.

If both a consequential decision review and a later patch acceptance review occur, an additional **$0.082584–$1.127008** sensitivity covers the latter within P09. It assumes a Sol reviewer independently inspects the patch, preserved failure, focused results, contracts and neighboring consumer, and writes findings. The low endpoint assumes reuse of P09's expert conversation; the high endpoint is cold. This is conditional on the applicable causal evidence, repair and authorization, and is not observed usage. If P09 is triggered only by a patch and no separate consequential decision review occurs, its existing budget can cover the acceptance review; adding this increment then would double-count.

| Participant and scenario | Low, cache assumed | High, cold | Low, no cache |
|---|---:|---:|---:|
| P29 original base | $0.696362 | $6.616990 | $1.181353 |
| P29 original base + all conditional reserves | $0.813675 | $7.891262 | $1.384299 |
| P29 base + all reserves + acceptance increment | $0.896259 | $9.018270 | $1.564163 |
| P61 original base | $0.695615 | $6.565122 | $1.173695 |
| P61 original base + all conditional reserves, including A10 | $0.919990 | $8.967505 | $1.556662 |

All-reserve totals illustrate a fully triggered scenario; they are not a probability or a claim that every branch will happen. The first two active hours remain a fixed horizon, so this work may not fit. No campaign or review was executed.

The increment uses the same work-based 4–8 request assumption as A10, with an already-established P09 expert conversation and independence from the patch author. Each request includes the original 16,000/48,000 shared-context sensitivity and the same excerpt and history formula. For the 79,290 bytes of listed source units, payload/history is 9,932/79,504 tokens, common input 64,000/384,000, total input 73,932/463,504, cached subset 51,200/0 and output including estimated reasoning 3,200/20,000. Bytes are not observed tokens, and reasoning volume is unknown. At the same Sol input/cached/output rates of $2/$0.10/$10 per million, the increment is $0.082584/$1.127008; the low no-cache sensitivity is $0.179864. If acceptance needs a fresh conversation, one first request is cold and the low estimate rises to $0.106904; cache lifetime and eligibility are uncertain. Details and recomputable components are in the accompanying JSON.
