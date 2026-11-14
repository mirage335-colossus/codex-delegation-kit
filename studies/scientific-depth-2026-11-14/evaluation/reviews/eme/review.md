# Independent EME depth review — initial disposition

## Assignment identity and review boundary

Compared the frozen EME first-pass package at
`evaluation/first-pass/eme/` with the EME rows of the frozen matrix, its
acceptance rules, the EME evaluator map, the reference EME material, and
first-party sources. The participant package has not changed between its
frozen first pass and the current `research/eme/` copy: SHA-256 hashes match
for `chapter.md` (`3b3ecd22…`), `source-ledger.md` (`f2eba7d2…`),
`link_budget.py` (`bbb000ab…`), and the recorded output
(`7809f77f…`). Pump source identity is HEAD
`13db435fc85114be2e2a0298580d5c3e2bcba996`; the four read-only EME reference
files have no dirty-status entries. No pump source was changed, built, or run.

The comparison is about substance and application, not report length or use of
the same model. The chapter is candid that it is not an exhaustive review and
does not establish a calibrated 5.8 GHz link. That is appropriate. Several
important uncertainties are genuinely open. They do not, however, replace
accessible source-derived findings that are absent from the chapter.

## Independently checked evidence and calculations

**Near-band primary measurement.** I opened the full text of Sun et al.,
“Promoting Earth-Based Radar Astronomical Observations of the Moon,” *Sensors*
20(7), 1874 (published 2020; observation 26 April 2019), at
[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7180880/). Its methods distinguish
the calculated pre-observation result from measured spectrum results:

- Lines 149–175 give 7,209.125 MHz, 200 W, LHCP transmission, two receive
polarizations, station apertures, the 503 km and 1,118 km footprints, and the
footprint-derived RCS/SNR method.
- Lines 181–188 give the 49-point DE436 footprint calculation: 35 Hz and
  90 Hz predicted spreads, separate from the common Doppler center and its
  hourly change.
- Lines 191–205 report 60-minute echo detection, measured spectrum peaks and
  offsets, 2 Hz/5 Hz spectral resolution, approximately 40 Hz/90 Hz widths in
  the plotted spectra, and same/opposite-circular ratios 0.44/0.45.
- Lines 202–216 report data-integrated SNR estimates of 177,000/203,000 and
  observed-area OC albedo 0.06 for both stations. The paper uses albedo 0.07
  for its earlier predicted SNR estimates (line 186).

The participant correctly identifies 35/90 Hz as the *a priori geometric*
width estimate, and correctly distinguishes that from measured center offsets
at chapter lines 62–63. It does not report the complementary measured
approximately 40/90 Hz spectra, 0.44/0.45 polarization ratios, 0.06 measured
albedo, or 177k/203k data-integrated SNR results. Its chapter lines 75 and 95
mention the 0.07 estimate but omit the actual nearby-band measurements. This is
a consequential, feasible source-reading gap: it affects the width estimator,
polarization transfer, cross-section uncertainty, and the interpretation of
the participant's calculation. None is a 5.8 GHz whole-disc measurement.

**Calibration counterevidence.** The official NASA PDS record for the Arecibo
transmit / Green Bank receive 12.6 cm mapping archive, [PDS record](https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=ARCB/NRAO-L-RTLS/GBT-5-12.6CM-V1.0),
confirms at lines 21–35 that products are local lunar maps with per-pixel
backscatter coefficients, incidence/beam-angle layers, polarization maps, and
beam/background corrections. Lines 30–31 and 50–51 state that calibrated
absolute coefficients remain a factor of 6–10 below earlier investigators for
unknown reasons, while polarization ratios are relatively well calibrated;
they also report residual pointing artifacts. The participant's lines 97 and
source-ledger row 12 accurately preserve this as a **12.6 cm sensitivity**, not
a 5.8 GHz distribution. I did not retrieve or analyze any PDS raster pixels in
this review.

**Foundational-source identity.** The initial source ledger row 7 and chapter
line 58 call the 1960 “A Theory of Radar Scattering by the Moon” an Evans and
Hagfors source. The official [NIST Journal of Research volume index](https://www.nist.gov/nist-research-library/journal-research-volume-64d)
lists the article on page 217 as by T. B. A. Senior and K. M. Siegel; the
official [NASA NTRS record](https://ntrs.nasa.gov/citations/20150020402)
identifies the same authors, title, and report. The indexed primary record
describes the quasi-smooth / discrete scattering-area theory and its measured
support, consistent with the chapter's physical summary but not its attribution.
I attempted full-text access through both official PDF routes. The NASA NTRS
PDF returned `Cache miss`; the NIST 16,741,766-byte PDF returned
`(400) Content length is too large: 16741766`. I therefore verify the
misattribution from official bibliographic records and index text, not by a
full-paper reread. The correction should identify Senior and Siegel and retain
the access limitation.

**Independent calculation.** I wrote and ran
[`link_budget_review.py`](link_budget_review.py), with its captured output
[`link_budget_review.txt`](link_budget_review.txt). Using the primary article's
503 km footprint, 7.209125 GHz, 200 W, 18 m/50% transmit aperture, 40 m/47%
receive aperture, 96 K, mean range, and the paper's 0.07 pre-observation
albedo, I independently reproduce `Pr=4.406024e-16 W` (`−123.560 dBm`),
`kTB=−163.336 dBm`, and `Pr/ΔPn=177,688` (`52.497 dB`) under its own
noise-power-standard-deviation estimator. This reproduces the participant's
arithmetic and comes within about 0.02 dB of the article's *data-integrated*
Km value 177,000, as well as 0.27 dB of its pre-observation estimate 167,000.
Those are distinct comparators; the participant currently reports only the
latter comparison. The unintegrated `Pr/kTB=39.776 dB` is a different metric.

As an illustrative target-band arithmetic check (not field evidence), using
5.760 GHz, 40 W, 3 m/55%-efficient dishes, `η=.065`, 384,400 km equal ranges,
and 80 K gives `σ=6.1640e11 m²`, `G=42.561 dBi` per dish,
`Pr=−152.998 dBm`, and `C/N0=26.570 dB-Hz`. This whole-disc reference still
omits the actual extended-target beam integral, pointing, calibrated
cross-section and station-specific noise. The check shows that a conditional
target-band power/noise calculation is feasible despite the missing station
inputs; the participant's target-band script currently stops at dish gain,
point-source pointing, width scaling and rain sensitivity.

The independent PDS review confirms the first-pass interpretation of the
factor-6–10 absolute-calibration discrepancy as `−7.782` to `−10.000 dB` if
used as a sensitivity. It is neither a probability distribution nor a
target-band correction.

## Frozen matrix dispositions

| Row | Initial disposition | Evidence comparison and material limit |
|---|---|---|
| EME-01 Path and observable identity | **Supported** | Chapter lines 1–54 clearly frames passive, distributed, polarization-sensitive EME, separates center Doppler, distributed spread, fading and terrestrial impairments, and bounds transfer from the 7.2 GHz local radar and operating reports. It distinguishes calculation from observation. Correct the foundational source identity noted above. |
| EME-02 Extended-target link budget | **Partial** | Chapter lines 40–54 gives a correct point-target special case and extended-surface integral with reference planes; lines 93–101 reproduce a real 7.2 GHz observatory-scale link and give explicit assumptions. The target-band section does not complete a 5.76–5.8 GHz received-power/C/N0 budget with an explicit cross-section and receiver noise. Missing actual station inputs limit a product claim, but a conditional target-band budget is feasible and the independent illustrative check above demonstrates it. Beam weighting is acknowledged but no integrated target-band factor is computed. |
| EME-03 Scattering alternatives | **Partial** | Chapter lines 58–71 and 103–110 compares point, uniform, Hagfors, composite, ephemeris and fading-only ideas, with limitations. It does not give or quantitatively compare a normalized angular kernel, diffuse fraction law, polarization-specific cross-section, or residual/observable that would discriminate these shapes. The fixed 0.07 value is not the measured 0.06 Mare Imbrium result from its cited near-band source. No exact C-band law is required; equivalent conditional alternatives and quantitative consequences are. |
| EME-04 Delay and power-delay profile | **Partial** | Chapter lines 58–60 correctly derives and labels the 11.564 ms finite-distance geometric support and separates it from echo power. It does not calculate or report a cumulative delay-power profile, t50/t90/RMS delay, source-table weighting convention, or an integrated beam-weighted comparison. These are available desk discriminators from classical pulse/delay measurements even though the target-band PDP remains unmeasured. |
| EME-05 Coupled Doppler and delay | **Partial** | Chapter lines 62–71 distinguishes common path trend from surface-dependent support and labels 35/90 Hz as footprint/DE436-derived, scaling only conditionally to 5.8 GHz. It does not preserve the nearby paper's measured approximately 40/90 Hz spectra beside those predictions, define estimator differences, or derive a delay-conditioned Doppler law, spectral shape, or coherence observable. The missing target-band spectrum is a genuine boundary; the omitted 7.2 GHz measured spectrum is not. |
| EME-06 Retarded geometry and station separation | **Partial** | Chapter lines 32–54 gives the two-leg range/path formulation and notes topocentric, reflection-epoch and unequal-station effects; lines 62 and 109 correctly tie the cited calculation to DE436. It has no independent retarded-geometry calculation or quantified instantaneous/geocentric approximation error. The actual intended station fixture is absent, but the cited paper's station geometry and epoch are available for a bounded check. |
| EME-07 Polarization conventions and alternatives | **Partial** | Chapter lines 73–77 explains reflection sense, OC/SC versus antenna mismatch, and appropriately limits a one-off 10 GHz operator estimate. It misses the cited article's actual local `μC=.44/.45`, measured OC albedo `.06`, and their footprint/calibration conditions. No target-band Jones/axial-ratio statistics exist; that boundary is reasonable, but nearby observed circular-channel data should have been carried through. |
| EME-08 Pointing, beams, noise and speckle | **Partial** | Chapter lines 79, 83–89 relates lunar noise to beam, distinguishes point-source pointing penalties from disk coupling, and reports a single station's >2 dB observation. It lacks an executed lunar beam-fill/antenna-temperature calculation, a measured beam-overlap or dish-size comparison, and a quantitative speckle/spatial decorrelation model. These quantities are correlated; simple dish gain alone is not full-disc link gain. The qualitative RFI and gain/noise dependencies are useful. |
| EME-09 Endpoint atmosphere and operations | **Partial** | Chapter lines 85–91 performs an auditable two-end rain sensitivity and avoids inferring a climatology; lines 87 and 112 preserve operational interference and failure causes. It cites gas propagation but leaves it uncalculated, and does not quantify cloud, low-elevation refraction/scintillation, occultation, or ionospheric two-leg effects. Missing site/weather inputs justify conditionality, not omission of all feasible standards-based comparisons. |
| EME-10 Model implementation by fidelity | **Partial** | Chapter lines 103–112 offers useful simple-to-composite alternatives and falsification/failure cases, and mentions existing `StreamingChannel` reuse. It does not compare a concrete delay–Doppler/scatterer versus replay representation by observables/cost/receiver use, and does not quantify the boundary of the existing native channel. Full implementation is out of scope; a deeper implementation comparison remains feasible from project docs and source models. |
| EME-11 Executed physical-observable and numerical checks | **Partial** | The link calculation and geometry/rain arithmetic are reproducible and independently check out. Primary sources are actually identified, and official PDS metadata is inspected, but the report omits several primary measured 7.2 GHz observations (spectral width, CPR, albedo and data-integrated SNR) and does not analyze any public numerical product or raw record. Recent relevant X/C polarimetric calibration/local-bistatic studies also need a bounded transfer check; they will not close the 5.8 GHz whole-disc gap. The absence of calibrated full-disc two-station 5.76–5.8 GHz IQ is supported as a boundary, but not a blanket substitute for these checks. |
| EME-12 Severity and joint states | **Partial** | Chapter lines 85–89 has a transparent two-site rainfall stress and operational interference examples; lines 105–116 separates failure causes and requests needed station inputs. It does not define a matched downstream receiver discriminator or a joint adverse/outage case that preserves dependencies among cross-section, beam, noise, weather, pointing, polarization and tracking. It correctly avoids occurrence probabilities. |

No row is unsupported in the sense of fabricated evidence, and none is
“outside declared conditions.” The essential rows do not meet the domain
acceptance rule because material rows remain partial.

## Six depth dimensions

1. **Regimes and observables — good, incomplete at the target band.** Correctly
   separates passive bistatic/monostatic EME, orbital radar, station practice,
   center shift, surface spread, delay support, interference and receiver
   factors. It has no scenario-specific station/waveform, so it properly limits
   application claims. The near-band local footprint and whole-disc target
   remain different regimes.
2. **Discovery and source inspection — partial.** Ledger rows 7–20 include a
   primary near-band journal paper, an official PDS record, ITU standards,
   operational reports and an acknowledged bounded search. The key primary
   paper is not fully mined for its actual measured outputs; the 1960 paper is
   misattributed. The source map includes useful more recent Mini-RF X/C
   calibration and bistatic evidence (Peters et al. 2026, Chan et al. 2025,
   Fassett et al. 2025) that is not in this study's source ledger. These are
   local SAR/calibration leads, not missing target-band EME observations, but
   can materially inform transfer/cross-polarization limits.
3. **Alternatives and counterevidence — partial.** The model-family discussion,
   6–10× absolute-calibration discrepancy, and 802.11a interference are strong
   examples. It omits the primary paper's distinction between predicted and
   measured spread/polarization/albedo and therefore leaves contrary and
   complementary measurements unused. There is no calibrated target-band
   cross-section or angular law.
4. **Quantitative interpretation — partial.** The equations, units, SNR
   estimator, reference planes and distinction between `Pr/kTB` and the
   integrated paper metric are unusually clear and independently reproduced.
   The main gaps are an explicit target-band link/noise reference, delay-power
   quantiles and weighting, spectrum/correlation definitions, and numeric
   polarization transfer. The 35/90 calculation and 40/90 measured spectrum
   must not be collapsed into one width.
5. **Executed discriminators — partial.** The participant runs a small
   source-matched calculation, target-band geometry/frequency/pointing
   sensitivities and two-end rain arithmetic. Those are meaningful and
   reproducible; our check confirms the source-matched arithmetic. No public
   PDS pixels, radar IQ, or EME recordings are reanalyzed; the cited paper's
   accessible plotted observables are incompletely reported. This gap is
   feasible to reduce even while calibrated 5.8 GHz data remain unavailable.
6. **Decision and next experiment — partial.** The handoff gives practical
   failure modes, identifies missing `Pt`, `G/T`, polarization, weather, and
   receiver inputs, and recommends explicit capture/beam/noise checks. It
   does not select a conditional target-band receiver budget or connect one
   defined case to an expected/falsifying result that changes a model choice.

## Feasible corrections and remaining boundary

Prioritized scientific corrections for the original owner to consider:

1. Correct the 1960 article attribution from Evans/Hagfors to Senior/Siegel;
   keep the full-text access failure explicit. A public indexed NIST record
   was sufficient to identify the bibliographic error.
2. Reopen the full 2020 *Sensors* article and add a compact matched table that
   keeps **predicted** footprint spreads 35/90 Hz separate from **measured**
   spectra about 40/90 Hz; report 2/5 Hz bin resolutions, OC albedo 0.06,
   SC/OC 0.44/0.45, and model-predicted versus spectrum-integrated SNR (including
   the 0.07 input). State local footprint, date, calibration and 7.209 GHz
   transfer limits. These are accessible primary results, not new C-band
   coefficients.
3. Add a clearly conditional 5.760 GHz full reference-plane budget with one
   stated station pair, assumed cross-section and receiver/system temperature;
   include an extended-target beam integral or explicit broad-beam limit,
   then show the change under the stated cross-section and noise sensitivities.
   Keep it separate from a calibrated observed SNR claim.
4. Add the easiest source-based PDP/delay and angular-law discriminator:
   reproduce at least one classical measured table/curve with the correct area
   measure, calculate defined quantiles, then compare the assumptions against
   the 7.2 GHz footprint data. Preserve the no-5.8 GHz-data boundary.
5. Inspect recent primary Mini-RF X/C calibration/local-bistatic evidence only
   for what it can decide: instrument cross-channel calibration, terrain and
   incidence/phase dependence. Do not transfer it into a whole-disc EME kernel.

The unresolved physical boundary remains real: no matched calibrated,
whole-disc 5–6 cm two-station complex echo dataset was identified in the
bounded search, so a 5.8 GHz scattering law, full Doppler spectrum, angular
polarization statistics, joint carrier/spatial covariance, and receiver
success probability cannot be claimed as measurements. A future discriminating
campaign needs simultaneous calibrated two-station IQ (or an explicitly
limited self-echo baseline), station positions/time standards, transmit
reference planes, beam patterns/pointing, polarization calibration, receiver
noise, weather, ephemeris, sufficient delay/frequency span, and predeclared
noise/window estimators. The public 2019 7.209 GHz source and 12.6 cm map are
useful transfer controls but cannot replace that record.

## Metering and performed checks

The `review-eme` run consumed 6 metered web operations: three opens (one NTRS
PDF fetch failed with `Cache miss`), a further primary article open, one
search, and a NIST PDF open that failed with HTTP 400 because its 16,741,766-byte
content exceeded the fetch limit. The search result surfaced the official NIST
index entry and authors. The 2020 *Sensors* article and NASA PDS record opened
successfully. Operations were reserved/finished through the assigned meter;
the recorded run allowance is 24. No unmetered web calls were made.

Source/check commands included file/hash identity comparison, reading the
review contract/matrix and participant chapter/ledger/script/stdout, and the
small independent calculation script cited above. No pump build or experiment
was run. No PDS raster or raw echo file was acquired in this review. Current
status: **EME domain partial; preserve this initial disposition pending any
prospectively assigned corrections and second review.**
