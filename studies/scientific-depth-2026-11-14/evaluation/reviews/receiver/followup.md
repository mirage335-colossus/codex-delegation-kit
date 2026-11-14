# Receiver review follow-up: native resource correction

This follow-up preserves the initial review and re-evaluates RX-09 only. All other dispositions remain unchanged.

## New evidence credited

The added native chapter is materially stronger than the evidence available at initial review. It ties costs to a concrete source fixture, `tests/test_gui_robust_live.cpp::late_affine_clock_support`, through `live::detail::prepare_profile` and a helper-enabled 6000 complex-sample/s profile. See `research/native/chapter.md:101–129` and the integrated `research/lead/synthesis.md:122–145`.

The source-derived case includes:

- Complete DATA, low pilot and Helper passband/skirt construction, with a guarded approximately 2960.52 Hz upper edge under Nyquist for the admitted 2400–2500 Hz Helper-tone cases; conservative minimum rates 5722/5922 samples/s. The selected tone, leakage and final spectrum are correctly marked runtime-returned/unmeasured.
- A named public slot set and two arrival-prior settings; public timing proposals up to 26 and segmented proposals capped at eight. It separates the ordinary full-support path, Helper-only quiet, varying-channel and line work; notes gaps force unsupported erasure, narrowing has no automatic full-prior rescore, and the fixed-prior supplement is not an ordinary-stream caller.
- Explicit reusable resource formulas and one declared scenario: 17 bytes per stored I/Q-plus-validity sample, TX ring `(ceil(delay·Fs·tx_scale)+64)·16` bytes, and 2×16×6000 = 192,000 interpolation tap contributions/s per geometry for a conservative fractional two-ray case. It also provides conditional record-size examples and clearly excludes phase/gain, allocation, cache, full receiver and queue costs where those are not computed.
- Pipeline requirements for preparation, full public priors, quiet/completion, fallback, in-flight leases and memory, complete service/backlog and target hardware, alongside the measured-versus-source-boundary distinctions. Synthesis §§128–136 integrates the same evidence and names the next phase-specific comparison.

These details answer much of the receiver's source/observability and common pipeline-cost question. They are not runtime work estimates, an executed test fixture or product qualification; that limitation is stated plainly in the native report.

## RX-09 revised disposition

**Still Partial.** The added material does not yet provide a comparable source-derived ledger for the baseline and the proposed shared-path/covariance receiver candidate over the complete service path. In particular, there is no candidate-versus-baseline count for preparation, acquisition/coarse bank, added tracking/state or likelihood work, reacquisition, codec/decision, quiet/completion, leased receiver workspace, and any explicitly charged full-prior fallback on the same concrete fixture. The chapter explains these costs, gives sample/ring/interpolation arithmetic and public search caps, and correctly says a new fixed-bank route must report incremental cost; it does not sum or estimate that delta. A partial-time component estimate is appropriate even while CPU time remains unmeasured and no product receiver run is authorized.

A further source-derived table should use the named fixture and compare (a) ordinary full-coverage receiver, (b) a fixed-bank/shared-path candidate at a declared tap/state count, and (c) the proposal-failure/full-prior arm. Hold sample interval, DATA/Helper schedule, public priors, arrival alternatives, quiet slots and work lease constant. List source-counted operations/states and workspace formulas per stage, include the cost retained when Helper narrowing fails, and label unknown data-dependent or runtime work rather than estimating it from headings. If an actual “20-record pilot” is part of the completed correction, cite its artifact and exact measured/source-derived columns: I could not find that pilot in the current `research/native/` files or lead synthesis, and the reviewed chapter explicitly says this fixture was inspected but its assertions were not executed (`native/chapter.md:111`).

The existing disposition file and initial `review.md` remain the record of first review; the revised row above is the follow-up judgment. Web meter remains 11/24; no external calls were added. No Pump build, receiver run, or product test was performed.
