# Uptake evidence packet

This packet contains source and appraisal evidence for a continuation exercise.
The locator descriptions below identify static source inspection separately
from findings reported by dated appraisal documents. Appraisal code is not a
production modem change. The user has explicitly reserved pumpModem `_ref/` and
`_appraisal/` for explicitly directed curation; this packet is read-only
referential material and does not authorize changes there.

## Provenance and identity

The pumpModem repository was at `13db435fc85114be2e2a0298580d5c3e2bcba996`
with empty `git status --short` when inspected. Relevant artifact SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| `_appraisal/highFidelity-triple_Robust_Modem/hf-public-search.md` | `862fdec519637cfa018981328651817b943db87c4d47c35fb5931884783e8956` |
| `_appraisal/highFidelity-triple_Robust_Modem/hf-phase-refinement.md` | `3f4275910373f12d635d60a21f0e72d08808465c702c8ca9507b3dae644f906f` |
| `_appraisal/highFidelity-triple_Robust_Modem/hf-validation.md` | `239957f220de99e268bee365dac574a0c688cfad11821723fde3df52141cfa63` |
| `_appraisal/highFidelity-triple_Robust_Modem/src/hf_phase_refinement.cpp` | `df187b44def95ae659212bceaf188d69e27269c984b2cf8c89e42738c80966c2` |
| `_appraisal/highFidelity-triple_Robust_Modem/src/hf_public_diagnostic.cpp` | `c8199192f308d6c46c6be91994717b514396429068ea76d408114057ce90f750` |
| `_appraisal/highFidelity-triple_Robust_Modem/tests/test_hf_phase_refinement.cpp` | `189fa8feef6e60a72b2e9c61d037f92ac2361719ec5ca494f60348a73dfebb62` |
| `_appraisal/highFidelity-triple_Robust_Modem/tests/test_hf_public_receiver.cpp` | `cb2b54ebd7520af8d60729183e235c4a0339363dd75d15570a8961df384b2902` |
| `_ref/highFidelity-triple_Robust_Modem/Fable-5.2/70-implementation-options.md` | `3ddede19b017ea9071dc5433edd2ab3696f622e155cd98009582ea42904c9399` |
| `include/datapump/triad_modem_v3.hpp` | `0a2ae5cdffb5901d8ee3ce355dffd5333d8ee60a96365b961f39370d37155cef` |
| `src/triad_simulation_stream.cpp` | `211b8b5e2396c9f1b7a39c33858ea8cfa9a1c74d5d8aa9377641533532146bf1` |

## Existing OU capability and the prior report correction

Fable's implementation-options reconciliation says its source review found an
existing `ray_coherence_seconds` API and corrects an earlier blanket claim that
Lorentzian behavior was absent: exponential covariance has a Lorentzian
continuous-time ideal and a sampled/aliased discrete counterpart. It states
that arbitrary measured spectra, coupled scattering, and empirical calibration
remain separate requirements. (`_ref/.../Fable-5.2/70-implementation-options.md:76-85`.)

Current code inspection is consistent with that report. The production API
documents `ray_coherence_seconds` as independent stationary proper-complex OU
gains with exponential covariance (`include/datapump/triad_modem_v3.hpp:193-200`).
The stream implementation derives decay and innovation from receiver sample
interval and coherence (`src/triad_simulation_stream.cpp:720-728`), applies
direct/delayed gains, and advances them while preserving state
(`src/triad_simulation_stream.cpp:871-880`). This is a static source/API audit,
not a fresh runtime test or proof of measured HF fidelity.

## Phase-bank proposal, implementation, and findings

The public-search research note calls a Cartesian sinusoidal phase bank a
“candidate” and says it is “unimplemented and unqualified” at that document's
state (`_appraisal/.../hf-public-search.md:183-205`). Its follow-up protocol
then records a two-observation physical-template diagnostic and prescribes a
bounded candidate with fixed prior accounting (`_appraisal/.../hf-phase-refinement.md:3-43,143-196`).

At the inspected repository revision, appraisal implementation and tests are
present: `src/hf_phase_refinement.cpp:630-674,810-820` plans bounded phase shapes,
work and scoring; `tests/test_hf_phase_refinement.cpp:185-207` contains a blind
off-grid coherent-basin assertion. This current source presence is an audit
observation; the dated “unimplemented” statement is retained as earlier
proposal provenance, not current status.

The validation report says the physical-template diagnostic used exact selected
IQ/validity hashes. For the failed off-grid 128-second, 0 dB-Hz observation,
known physical-template LR was 150.650 versus public-cell LR 35.170, with 0.2054
clean-energy coherence; a moving control had 146.210 versus 125.365 and 0.8651
(`_appraisal/.../hf-validation.md:48-66`). The initial implementation test
failed after 89 assertions on the blind off-grid positive-CFO-edge fixture; a
segment-seed-only repair also failed. The breakpoint-based repair passed 107
focused assertions and the documented full 17-group suite
(`_appraisal/.../hf-validation.md:68-88`). These check outcomes are reported in
the document; this packet author did not rerun them.

The first two-case shadow helped the off-grid case: old/new/combined evidence
was 21.0376/130.0809/129.3878. On the long weak moving case, old/new-only/
combined was 94.0398/15.2060/93.3467; the report attributes the combined
reduction to the fixed prior split and says shadow scores include no receiver
decisions (`hf-validation.md:90-105`). The later staged-coherence shadow reports
long-weak combined evidence increasing from 24.0931 to 105.7873 and 4.16367 to
88.65537 for two slots, while the short off-grid control remained unchanged.
The separate six-episode receiver cohort completed with three predeclared
staged wanted messages passing and the paired baseline failing on one fresh
holdout (`hf-validation.md:156-175`). These are conditional selected cases, not
a population success estimate.

## Work-cap fallback and validation boundary

The refinement protocol reports a public plan of 522.569 s, 1920 samples/s, ±10
Hz CFO, and 13 timings where old and combined FFT quotes fit the 40-billion
ceiling but new-family direct work is 105,780,492 rows, beyond the 100-million
cap. The corrected pre-IQ planner preserves old97 at fixed half weight, gives
the unavailable new family zero evidence, and does not reallocate omitted prior
mass (`hf-phase-refinement.md:379-401`).

Static source inspection supports the documented behavior: the current planner
checks full-public-timing work before IQ-dependent selection and preserves the
old family when the optional new family is unavailable
(`_appraisal/.../src/hf_public_diagnostic.cpp:27-35,151-190`); unavailable
report JSON says `executed=false`, keeps old/new weights at .5/.5, sets new
evidence to negative infinity and retained new prior mass to zero
(`.../hf_public_diagnostic.cpp:287-300`). The receiver test asserts unavailable
new-family evidence does not restore old-family prior mass
(`.../tests/test_hf_public_receiver.cpp:338-350`). These are static source/test
observations; the 17-group execution is reported by `hf-validation.md:205-221`,
not rerun here.

The report explicitly says the six-episode complete-receiver cohort remains
bound to the earlier staged source and was not rerun under the fallback revision
(`hf-validation.md:211-221`). The report separately records a later shadow
replay, planner regression checks, and the earlier receiver-cohort result.

## Provenance and coverage limits

All line references above are to the files named in the table or to sibling
files under `_appraisal/highFidelity-triple_Robust_Modem/`; abbreviated
`_appraisal/...` locators resolve there. Fable locator is under
`_ref/highFidelity-triple_Robust_Modem/`. Findings about present code are
source-audit observations; statements about checks, episodes and receipts are
faithful summaries of the dated appraisal report. No build, test, benchmark,
receipt replay, or production-source modification was performed for this packet.
