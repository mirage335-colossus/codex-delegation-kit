# Blind whole-work cost review

## Evidence and denominator

Frozen snapshot: receipt provenance names revision `15b17f7d3886f1baadf3c22b8990083eda6f85cd` and seven dirty paths (three GPU leaves and four receiver/test files). The supplied snapshot has no Git metadata, so those provenance fields are the revision baseline; I did not consult the current checkout or history. CPU and GPU receipts have the same source input hash and identical 61 shared-source hashes. All three GPU runtime leaf hashes match the frozen `tools/` files.

The CPU receipt is `triad-manual-complete-capacity-v3`, top-level `measured_with_unresolved_margins`; it reports 12 inference workers for each of eight individual scenario streams on a Ryzen 5 PRO 5650U (12 logical CPUs, 6 physical cores). Ratios are processing seconds per unique baseband second normalized to the shortest exact successor interval in the local 24-slot profile. They are not 12 concurrent-stream throughput. `nominal_service` is a conditional full nominal receiver composition; `complete_capacity` adds maxima over covered acquisition/fine strata. The latter status and interval, not its point alone, bound conservative service.

## CPU throughput forecast

Nominal composed ratios range 0.1630–0.3928 processing s / baseband s (reciprocal: 6.13–2.55 baseband s/s). All eight nominal rows report realtime `pass`, but `full_local_cpu_ceiling_demonstrated` is false for all eight and this is not a physical reception/sensitivity result. Conservative complete-capacity is `pass` for cases 2, 5 and 7; cases 1, 3, 4, 6 and 8 remain `unresolved`. Case 4 has a 7.49 point ratio and an extremely wide `[0.80, 18551.24]` interval, so it cannot support a stable throughput forecast. See the JSON table for each case and both intervals.

## Cost ranking and design attention

Nominal service sums fixed control + recurring bank + acquisition + complete nominal fine search. Fine search is the largest share in cases 1–3 (93–98%); bank preparation is material in cases 5, 7 and 8 (0.117–0.159 s/s), while acquisition is material in cases 4, 6 and 8 (0.044–0.054 s/s). Amdahl-style one-phase-to-zero ceilings in the JSON are strict arithmetic bounds, not expected gains: removing fine alone bounds nominal improvement to 1.85× for case 8 but 50.9× for case 1. Therefore prioritize measured work reduction by regime: fine search/adaptive tracking for 1–3; recurring-bank amortization or reuse for 5/7/8; acquisition candidate/work reduction for 4/6/8. Re-evaluate summed cost after each change—phase ceilings cannot be multiplied. Fixed control is under 0.5% in every nominal row, so optimizing controller/codec overhead cannot materially lift throughput.

## GPU evidence and limits

GPU receipt status is `bounded_mixed_precision_cost_regime_observed`; CUDA operations and matched score/work checks are present, but `local_cpu_service_established=false` and `complete_receiver_qualification=false`. Paired same-host CPU/CUDA phase timings exist only for cases 1, 2 and 6. Fine speedup spans 1.07–2.39×; recurring-bank speedup is 0.77× (slower on CUDA) in case 1 and 1.26–1.35× in cases 2/6. Acquisition spans 0.32–15.33×. These diverse bounded results favor testing phase-specific transfers against complete CPU cost; they do not justify assuming GPU acceleration wins a complete receiver or transferring EPYC timings to the Ryzen target. The GPU’s 426.22s trace elapsed is cloud run elapsed, not CPU service or a whole-receiver speedup.

## Recommendation

Next decision-quality experiment: produce a same-source complete CPU forecast table (the receipt-level composition is already above), then test a complete, matched GPU trace or phase-targeted CUDA variant on the largest forecast contributors, preserving identical public work, CPU target measurements, memory and receiver workspace. Start with fine on 1–3 and bank/acquisition on 4–8; retain all 12-worker single-stream conditions. Do not count setup/simulation elapsed as recurring service.
