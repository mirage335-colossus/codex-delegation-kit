> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# NATIVE independent scientific adjudication

**Overall: Partial.** The native plan is useful and technically grounded.
The material exception is NATIVE-08 (and the corresponding part of depth
check 5): the locked work does not close the contrast between long-window
native receiver admission and the computational cost of a wide distributed
channel teacher or a materially comparable propagation workload.

Only the locked submission was used as participant evidence. Participant paths
below are relative to `submission/`. The frozen question is native integration,
resources and evidence chain for the full declared development scope. Existing
code, existing assertions, historical reports, newly executed desk work and
future native tests have different evidentiary roles. Architecture approval in
the packet is not a grading result.

## Decisive checks

- **Pipeline and reference planes.** `project/src/triad_stream.cpp:445–489`
  composes DATA and Helper before returning the bounded source callable.
  `triad_simulation_stream.cpp:473–487,811–872,975–1025` keeps source
  coordinates, a bounded differential-delay ring, retune/phase, converter state,
  cursor and validity distinct. Bulk timing offset is outside the history
  formula. Receiver resource policy and actual source agree on one worker
  ceiling with the default twice the available hardware thread count, exact
  explicit overrides, full owner/input/stack reservations and ordered commit
  (`project/docs/development.md:89–107,214–224,262–269`;
  `triad_stream_resources.cpp:27–42`; `triad_stream_receiver.cpp:240–251,357–401,516–550`).
  `project/docs/robust-current.md:174–185,373–389` independently describes
  configured calendar and charged complete service. The maintained one second
  of receiver service per received second failure threshold is not a rate
  measured in the submission.
- **Adverse behavior.** Current scoring rejects any invalid row
  (`project/src/triad_receiver.cpp:371–403`); the message classifier independently
  rejects an invalid score and stream commit invalidates incomplete physical
  observation/interval (`triad_message_receiver.cpp:590–606`;
  `triad_stream_receiver.cpp:522–545`). Ambiguity breaks the quiet run; after
  some observed DATA, two scored quiet slots invoke decode. EOF/cancel is
  incomplete without physical completion (`triad_message_receiver.cpp:737–782`).
  Thus the submission is right that P4 requires more than changing the score
  producer and that a physical two-slot blackout can look quiet when it leaves
  valid noise. This is a conditional source/identifiability result, not an
  observed false completion or successful masked decode in this case.
- **Source-backed decisions.** Checked the [ITU F.1487-0 PDF](https://www.itu.int/dms_pubrec/itu-r/rec/f/R-REC-F.1487-0-200005-I%21%21PDF-E.pdf),
  Annex 3 §§1, 4.3: independent equal-mean paths, zero frequency shifts,
  differential 7 ms, 30 Hz per-path 2σ. Snapshot `tuning_presets.cpp:27`
  and `robust_profile.cpp:230–263,335–341` do not establish that mapping
  through the existing GUI preset; the two separate fixed-grid Gaussian ray
  sources and actual sum are available, with finite interpolation and no
  claim of exact ideal Gaussian equivalence. Checked [NTIA's LFMF repository](https://github.com/NTIA/LFMF/blob/main/README.md#low-frequency--medium-frequency-lfmf-propagation-model)
  and [original implementation](https://github.com/NTIA/LFMF/blob/main/src/LFMF.cpp#L812-L877):
  smooth Earth, 0.01–30 MHz and terminal heights below 50 m; separate reference
  field/power and basic loss; the 4.77 dBi receive reference enters power,
  but not basic transmission loss. No live dependency or mixed-path capability
  is inferred from LFMF alone. The [Sun et al. primary geometry/polarimetry experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC7180880/#sec2-sensors-20-01874)
  is at 7209.125 MHz, with 200 W CW and a targeted footprint. The
  [SM6FHZ station record](https://2ingandlin.se/EME_6.html) is the distinct
  October 2014 exact-band case. The [original Witvliet flare article](https://ris.utwente.nl/ws/portalfiles/portal/26242061/impact.pdf),
  pp. 35–36, supports the 35/45 dB desired and 12 dB background changes used
  to keep external noise separate from receiver noise and missing capture.
- **Performed rechecks.** Inspected the submitted scripts before running them
  from the assigned review directory. `owner-mask-check.py` and
  `owner-desk-calculations.py` reproduced byte-identical JSON. The first gives
  33 tested integer arrivals, Gram relative difference 5.466e−16, masked
  energy 39–51 against 64, and rank one/zero for one/no retained row.
  The second reproduces the geometric slope limits, two-ray notch periods,
  chirp loss and distinct outage runs at equal 0.8 mean gain. The locked
  `eme_angular_desk.py` converges between its two offline grids, and yields
  broad mixed-disk versus two .15° beams: relative loss 0/5.765 dB,
  delay p90 5.800/.525 ms, centered W90 54.870/19.484 Hz and 75 Hz
  correlation .648/.994. These are representative transfer observables, not
  a calibrated lunar response or a per-candidate computational quote.
  The submitted `wav-analysis.py` reproduced byte-identical results from
  supplied FFT/envelope CSVs (17 selected spectra, ratio-control peak +2.4576 s,
  correlation .715164, raw off-band control +.455843 there); the raw WAV hash
  and PCM frame/rate/duration check also passed. I did not regenerate the
  FFT/envelope CSVs from the WAV or interpret recorded gain states as an
  exogenous validity mask.
- **Source-checked arithmetic.** `verify_desk.py` and its stdout verify
  12 selected source/document hashes against the locked manifest, and reconstruct
  the submitted work estimates without invoking the product. At 48 kSa/s,
  600 s gives 28.8 million rows, 466.919 MiB owner payload and 906.372–933.838
  MiB with raw payload; default 4 GiB memory implies 63,161,283 input rows
  (1315.860 s) before tighter limits. A 1.4 Hz inner rate with 10 Added Symbols
  occupies 8.75 Hz DATA, yet needs at least 342,308,590 exact template work rows
  against 30 million, even at one clock and one ray. The specially mapped
  192 kSa/s to 5 Hz example needs 2,616,691 taps against 1,000,001. The
  proposed masked-search estimate (about 65 MiB all prefixes plus 20.3 MiB
  per-lag inverse/rank for illustrative J=130) is reproduced as a scale
  example; the current clock count is one or three, so 130 is not a native
  admitted bank with 26 workspaces per clock. Rebasing small FP32 sums
  preserves about 6.4e−5 energy that large cumulative subtraction loses, and
  retaining one of two .9-correlated rows gives precision 1, not 5.263. For
  5.8 GHz at the submitted 1.3 Hz/s and a 60 s window, 585 RF cycles coexist
  with .100862 μs envelope error; at 3600 s a 4 kHz offset incurs 1.452
  envelope cycles. That comparison supports the staged phase versus warp
  decision but does not time either path.

## Row judgments

See `dispositions.json` for exact row dispositions, participant locators,
verification and remaining actions. NATIVE-01–07 and NATIVE-09–11 have direct
evidence for their respective questions:

- The inspected stream and native target boundaries carry current pipeline
  reuse; appraisal may add provenance and a pinned reference outside DSP.
  The full timed emission, physical propagation, external/internal noise,
  front-end order and validity accounting are preserved as separate layers.
  Carrier correlations and coupling are physically demonstrated with common
  transfer examples instead of assigned from carrier count. A calibrated
  replay or complex transfer, conditioned Gaussian, geometry plus residual
  and reference/import do different jobs; the evidence does not warrant an
  unconstrained learned model or an on-line solver per receiving hypothesis.
- Actual DATA, Helper guard and IF/RF conventions control native admission.
  The distinction between history/tails and bulk motion is actionable:
  use signed public sample coordinates and residual bounded support, retain
  measured settling, and compare matched whole/split reads through gaps and
  tail delivery at unchanged physical inputs. For the illustrative tuner,
  the 29.63 ms time constant implies approximately .409 s to 10⁻⁶
  amplitude. This can overlap a public dwell. Assertions in the shipped
  `test_triad_v3_channel.cpp` are evidence of intended coverage, not checks
  run in this episode.
- Calendar/observability and intended hardware claims have appropriate
  boundaries. The phase correction, finite-path benchmark, restricted
  exogenous mask and import-first LFMF use are staged against alternatives.
  The submission gives concrete admission conditions, rather than claiming
  masked accelerated scoring, a released GUI profile, an installed solver
  or a GPU throughput increase. Accelerator options remain conditional on
  backend receipt structure, matched public work, fallbacks and same-stream
  evidence. Competitor infrastructure and protocol redesign do not decide
  the selected work.
- Release and qualification are separate gates. The proposed P0/P1/P2 first
  tranche has evidence and scope; the later operational decisions carry
  rejected controls, falsifiers, budget and task-specific checks. Dated
  long-window plan bounds in `project/docs/validation.md:1205–1216` have
  no newly measured whole-slot time and do not certify the mixed frozen
  export or hardware. The current reviewer checked the relevant snapshot
  against its own manifest, not against a live repository.

### NATIVE-08 and depth check 5

The frozen native map points to Fable-5.2 chapter 70, “Resources and validation,”
lines 224–250. I read that passage only from the supplied original comparator.
Its two cases isolate different scaling obstacles: the number of path
contributions per sample when directly rendering a fine distributed EME
teacher, and the elapsed physical time for multiple complete sub-9 kHz
messages. Its specific cell grid, timing budgets and sample sets are examples,
not required inputs. The same decision could be settled with different
geometry, a materially different deployed propagation workload, or a
source-grounded finite teacher with an executed cost/observable comparison.

The sub-9 and coarse-bank/resource half of this comparison is strong:
`work/architecture-review.md:59–67` and `work/owner.md:113–121` distinguish
retained raw capture, owner copy, the exact/mapped template caps, a failing
otherwise plausible narrow spectrum, timing that was never measured, and
profile/ingress choices. The masked-search calculation in
`work/architecture-review.md:35–43` is useful additional receiver evidence:
it distinguishes per-arrival Gram storage from total-window retention and
motivates temporary prefixes plus bounded lanes, but does not evaluate a native
propagation teacher. Neither the fast offline disk quadrature
(`work/research/inquiry-a.md:139–153`) nor the physical phase/envelope scale
check (`work/architecture-review.md:23–31`) computes work from sample count
times path terms (or a materially equivalent rendering cost), counts admitted
history/live latent state for a representative reduced teacher, or checks
what useful observable a reduced renderer preserves. `work/owner.md:87–95`
does adopt a bounded finite response outside the per-hypothesis loop and
provides convincing reasons to avoid independent delay/Doppler marginals.
It leaves the difference between dense direct rendering, a compressed response
and their possible native admission as a proposal. These are distinct from
hardware timing or an unknown site calibration: the submitted grid and source
contract are sufficient for a bounded, auditable illustrative work quote.

Remaining action for this judgment: on one declared distributed severe case,
state the actual complex rate, active/tail extent and geometry/support; compute
direct versus compressed/precomputed work and live memory under the native
history/admission rules; show an exact small reference and the useful
delay/frequency/cross-carrier observable retained or lost. State the simpler
model's applicability and what size is rejected or carried to later
implementation. No prescribed EME grid, production build, target hardware
timing or site measurement is needed for this desk comparison. The independent
evaluator reproduced the submitted observable and native arithmetic only; no
post-lock estimate substitutes for this missing participant work.

## Access and execution record

Metered evaluation case `native`: 18 admitted and finished web items (of its
initial 50), including the inaccessible generated NTIA API page and a
no-match search for the dotted IF notation; the NTIA source and README and
SM6FHZ's spaced notation supplied the decisive material. No browser,
connector, shell network, retries of blocked author acquisitions or live
project reads. The locked author queries were located from individual
meter receipts, after one evaluator parser attempt failed before extracting
queries because the meter contains receipt IDs rather than inline objects.
The author’s retained TTE image and numerical P.372-18 access limits remain;
those surfaces were not used to establish native behavior. No product code
or built artifact was executed, no model was implemented, and no live or
representative target hardware was timed. Local research output files
were written only in this assigned review directory.
