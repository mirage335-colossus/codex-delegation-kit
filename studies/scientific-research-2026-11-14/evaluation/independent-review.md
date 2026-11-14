# Independent technical review

Reviewed reports under opaque run IDs against the [frozen rubric](rubric.md) and
[uptake key](uptake-key.md). I did not consult the arm map. Report wording can
make assignment features visible, so this is label-blind review rather than a
test of successful blinding. I used the combined local exemplar slices as
comparison material and checked consequential originals. Participant disclosures
and verifier access are separate evidence.

## HF discovery

Both reports recommend a stationary Gaussian benchmark, a nonstationary and
distributed extension, and measured replay. Both keep one channel realization
across the composite waveform, distinguish per-carrier occupied bandwidth
from carrier spacing, and evaluate the Helper with separate tracking and
complex-gain assumptions. Both correctly treat F.1487's 7 ms / 30 Hz pair as
one conditional reference configuration rather than an environmental envelope,
and treat the 30 Hz as a per-path 2σ Gaussian PSD width rather than a two-ray
offset. The distinguished cases and the 3 kHz validation / qualified 12 kHz
application range follow Annexes 1 and 3. m31's broad statement at line 22 is
best read with that distinction. Neither report gives a quantified useful-work
cost target or actual receiver acceptability threshold for an appraisal model.
[ITU-R F.1487, Annexes 1–3](https://www.itu.int/dms_pubrec/itu-r/rec/f/R-REC-F.1487-0-200005-I!!PDF-E.pdf)

| Rubric dimension | m31 | m74 |
| --- | --- | --- |
| 1. Mechanisms and model families | **2.** Lines 20–34 cover fixed and local changing taps, distributed scattering, replay, climatology and physical hybrids. Wider propagation/regime map includes equatorial and disturbed conditions. | **2.** Lines 25–35 identify stationary scatter, tilted delay–Doppler clusters, time-varying modes, calibrated replay and model-plus-stochastic residuals. Disturbed equatorial coverage stays open. |
| 2. Primary evidence and access | **2.** Lines 7–16 and 22–34 use the official standard, original ITS results and recent field papers. The DRDC DAMSON summary and publisher-only Angling abstract cannot establish a matched joint tail. Lines 46–48 preserve those access limits. | **2.** Lines 27–33 name precise direct measurement windows, estimators, exclusions and site limitations. Line 53 excludes the unsupported preprint methods. |
| 3. Foundational/recent reach | **2.** Standard, agency memo and ITS precedents plus Java and two genuinely recent 2026 signal studies at lines 22–34, with calibration gaps at line 48. | **2.** Standard, original older field papers and recent Java and 2026 Doppler work at lines 7–35. Line 53 names joint tails and disturbance data still missing. |
| 4. Contrary evidence and reconciliation | **1.** Lines 26 and 34 flag shape, width and finite-window concerns and correctly distinguish a Cauchy residual distribution from a tap PSD. Leaves the named alternative PSD and its controlled matching unspecified. | **2.** Lines 20–33 separate shift, spread, RMS and support. Compares Gaussian and Lorentzian PSDs on a named finite width and distinguishes both from residual statistics. Limits auroral results to the sampled regime. |
| 5. Equivalence and simpler combinations | **2.** Lines 7, 24, 28, 38–44 make benchmark equivalence conditional, reuse two-ray primitives and factor physics, stochastic behavior and common correction. | **2.** Lines 23–35 and 39–43 reuse primitives, state what fails in the simple model, and distinguish Helper common frequency estimation from channel transfer. Current code identity was outside discovery scope. |
| 6. Discriminating implications | **2.** Lines 38–44 offer generator checks, SNR/cliff surfaces, false lock and reacquisition, and which receiver alternative to try under each failure. | **2.** Lines 41–49 give a worked intermediate-vs-severe notch, separate shape/width comparison, oracle and real tracking with gated fallback, and explicit expected observables. |
| 7. Calibration and qualification | **2.** Lines 28–34, 40–48 keep route and measurement scope, derive the example, and distinguish replay and proposal from receiver results. | **2.** Lines 3, 9, 33, 45–53 distinguish representative test settings, observed campaigns, ray-traced interpretations, calculation and unexecuted checks. |
| 8. Scope and reusable synthesis | **2.** 24/24 logical web operations reported, including a failed open. Four reported shell calls include a failed interpreter setup with zero assertions and a python3 retry. Table, rationale and ordered plan are reusable. | **2.** 24/24 logical web operations and four of six shell calls reported. Two ITU screenshots returned no viewable image and count toward the cap. Clear separation of checks, caveats and operation log. |

m74 supplies the only explicit, empirically motivated comparison of Gaussian
and Lorentzian *tap PSDs*. The existing [independent HF verification](hf-primary-verification.md)
confirms the scope of the original Lorentzian work. Its 142.86 Hz constructive
Helper example also makes periodic notch motion actionable: a 3 ms delay is
roughly 13 dB down at DATA while the 7 ms case is again constructive under the
same Helper reference. That is a concrete check for an intermediate corner, not
a product performance result. Nissen and Bello support the named short-delay
but broadened example and exclusions. Zaalov et al. support the separate
nighttime arrivals near 5 and 7 ms with different azimuths and Dopplers. Their
interpretation of the late arrival's mechanism is conditional.
[NTIA TR-92-284](https://its.ntia.gov/umbraco/surface/download/publication?reportNumber=92-284.pdf)
· [Nissen and Bello §§2–3](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2002RS002746)
· [Zaalov et al. §3.1, Fig. 2](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2006RS003611)

m31 contributes a distinct modern Alaska example: different measured spreading
by route and explicit uncertainty about whether secular drift within the
one-minute window accounts for spreading. This supports the proposed
multi-window discriminator. Its broader route selection, separate viability
and interference controls, and citations for equatorial and transauroral
conditions usefully complement m74. Both accurately limit the independent
2026 daytime Cauchy finding to frequency residuals. Dear et al. report a
1.882 ms delay span in an illustrative CIR, a mean 0.4627 ms RMS spread over
their quiet week and a separate 0.7–1.1 Hz Doppler shift range. These support
the distinct examples at m31:33 and m74:33, not a parameterized joint HF model.
[Alaska beacon study §4, Fig. 10](https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2026.1848834/full)
· [Fernandes et al. §3.2.1](https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2026.1713968/full)
· [Dear et al. §3.3 and Fig. 12](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2023RS007877)

Both cover much of the selected Fable HF model and Astra skywave slices.
Neither reconstructs their breadth of historic and contemporary measurements,
full measurement caveats, calibrated environmental tails or all relevant
front-end cases. m74 gives a stronger spectral-shape discriminator and m31 a
broader source map. Neither changes the other report's central architecture.

## EME held-out discovery

Both recommend a geometry-conditioned shared delay–Doppler representation,
with a point-reflector control, small jointly projected statistical taps,
facets for cases sensitive to the lunar footprint or polarization, and
representative replay if available. Both propose calibrated simultaneous tones
at the actual separations, separate wider-band delay sounding, and matched
receiver behavior with and without Helper. In both, geometric delay support
(about 11.6 ms) cannot fix coherence bandwidth, and a shared bulk shift does
not justify transferring the complex fade. The recommended direction and
primary field discriminator are equivalent.

| Rubric dimension | m22 | m89 |
| --- | --- | --- |
| 1. Mechanisms and model families | **2.** Lines 5–15 and 37–47 cover geometry, weighted scattering, polarization, budget/noise, and flat, tapped, facet and replay alternatives. | **2.** Lines 9–35 and 51–59 cover the same families, with more first-hand observation about shape/terrain and additional thermal and engineering anchors. |
| 2. Primary evidence and access | **1.** Lines 7–15, 47–49 support most decisions and mark indexed modern access, but misattribute JPL 42-166 and imprecisely define Taylor widths. Details below. | **2.** Lines 11–17, 33 and 63 generally state applicable access and limits. Correct lead author of the introductory 1974 paper and identify the original source of the archived diffuse-fraction figures. |
| 3. Foundational/recent reach | **2.** Hagfors, Evans, Taylor and recent radar/polarimetry/broadband leads. Lines 47–49 and 57 limit claims from recent indexed text. | **2.** Lines 11–17, 33 and 63 combine several original historical lines of evidence and recent literature at actual access depth. No suitable target dataset found. |
| 4. Contrary evidence and reconciliation | **1.** Lines 9–15, 35 and 49 distinguish geometry, uncertainty and bandwidth, but the Taylor width definition is inaccurate. The factor-of-two comparison is provisional. | **2.** Lines 11–17, 23 and 33–49 maintain distinctions among diffuse power, K factor, polarization, correlation and support. Uses limited-angle radar results as conditioning evidence. |
| 5. Equivalence and simpler combinations | **2.** Lines 26–45 give equivalent phase generation under a scoped approximation and a credible aggregation from facets to taps. A two-delay example warns of coherence revival. | **2.** Lines 39–55 distinguish two matching marginals from a matching joint distribution and state when facets and taps can preserve the same decision. |
| 6. Discriminating implications | **2.** Lines 51–55 propose joint fade and duration measures, same-settings comparisons and a useful oracle common-state control. | **2.** Lines 55–59 add fitting and validation on separate passes, covariance noise correction and explicit decision criteria for promoting model fidelity. |
| 7. Calibration and qualification | **2.** Lines 11–15, 47–49 and 57 specify assumed power, frequency and geometry limits and no availability forecast. | **2.** Lines 23, 31–35, 47 and 59–63 label derived numbers, measurement scope and no product test. |
| 8. Scope and reusable synthesis | **2.** 24/24 logical web operations reported, with blocked opens counted. Compact model table and practical checks. | **2.** 24/24 logical web operations and six of six shell calls reported, with failed blocked opens and a failed interpreter setup retained. The evidence table and calibration sequence are reusable. |

Taylor's 5760 MHz row supports 164/86 Hz for the full limb span and 60/25 Hz
for the estimated median-geometry widths in both reports. Taylor describes
the practical widths using echo-spectrum *autocorrelation* widths at its
10% and 50% points with a loose power-containment interpretation. m22:9
imprecisely calls these widths at fractions of peak power, which could lead to
a mismatched spectral estimator. m89:13 calls them measurable width summaries
and leaves the estimator implicit. m22:15 links the appropriate observations
at 2.3, 8.4 and 32 GHz but misidentifies their author. The PDF names D. D.
Morabito and the 34 m DSS-13 dish. The correction does not change the
beam-coupling conclusion. m22:47's additional 2025 campaign is supported
by the full paper's June 2024 7159.45 MHz compensation comparison, a method
precedent with high echo power and different stations/frequency. The cited
2020 bistatic experiment reports its modeled 35/90 Hz widths separately from
the observed spectra on two different footprints. Neither dataset provides
the proposed modem's channel covariance.
[Taylor, discussion of Fig. 6 and final table](https://wsjt.sourceforge.io/EME2010_K1JT.pdf)
· [Morabito, JPL report 42-166, §I](https://tmo.jpl.nasa.gov/progress_report/42-166/166C.pdf)
· [Tasmania team, §3.1 Figs. 4–6](https://www.mdpi.com/2072-4292/17/3/352)
· [Bistatic radar study, Eq. 4 and Fig. 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7180880/)

m89's older empirical anchors distinguish a delayed diffuse tail from an
instantaneously coherent component and give a measured link-budget precedent.
The introductory mapping article is Pettengill, Zisk and Thompson. Its
wavelengths, polarizations and delay–Doppler method are supported. NASA's
archived study reproduces the 35% and 25% values from Hagfors (1967a) in
Table 3.1 and explicitly notes the ambiguity of the extrapolation. Credit
those figures as historical estimates reproduced in the inspected report,
with original measurement provenance indirect. Lindgren's own institutional
thesis abstract confirms the power-budget estimate and measured average
agreement at 1296 MHz. The 2026 Li paper full text could not be opened in
this check. The recent modeling claims remain at indexed scope and m22's
possible spread disagreement cannot establish a contradiction absent matched
definitions and station geometry.
[Pettengill, Zisk and Thompson bibliographic record](https://ntrs.nasa.gov/citations/19740048201)
· [NASA archival report, Table 3.1](https://ntrs.nasa.gov/api/citations/19720017974/downloads/19720017974.pdf)
· [Lindgren, Chalmers thesis record](https://odr.chalmers.se/items/ea2e217b-7ea7-4c80-b29f-32542301f73e)

The [independent EME verification](eme-primary-verification.md) independently
supports this primary-source scope and identifies another material gap in both
reports: they state the distinction between geometric and effective delay but
do not compare competing historical area-weighting conventions and the
resulting different delay-power percentiles. The combined Astra/Fable EME
slice supplies material either report could use
for a larger appraisal: 5.76 GHz operating experience with Q65, beam/path
impairments and real on-band RFI, standard-driven gas/rain and interference
scenarios, and stronger comparative detail on plausible terrain laws. Those
gaps do not invalidate the common model decision or justify equating either
answer with the combined corpus. This is a held-out question from the same
project and neighboring RF subject matter.

## Source audit and development uptake

Both audit reports reuse the existing production `ray_coherence_seconds`
option and close duplicate work on an OU/Lorentzian generator for the specified
synthetic objective. Both identify the later implementation of a dated
unimplemented proposal in **appraisal** scope, preserve the negative
long-weak case and selected improvements, keep fixed prior mass at the cap,
and hold promotion pending final-revision receiver evidence. Material decision
differences are absent. m63 prioritizes the previously failing long off-grid
episode as the first discriminator before spending the six-case allowance.
m45 proposes the full frozen cohort first and adds a conditional cap-edge
operational comparison before promotion. Its explicit sampled OU PSD formula
explains the meaning of its reuse more precisely.

| Uptake criterion | m45, eligible prefix | m63 |
| --- | --- | --- |
| Existing OU equivalence and limits | **2.** Lines 5 and 28 tie reuse to the API, implementation matches, recurrence and packet. The sampled PSD and field-calibration limits are valid. | **2.** Lines 5–7, 29–31 tie reuse to source, initialization, finite sample timing and legitimate remaining needs. |
| Dated proposal vs actual appraisal code | **1.** Lines 7, 28–32 establish source identity and use the shared packet and validation report, but the participant's direct planner/scorer and test confirmation depends on call 12. | **2.** Lines 9–11, 29–31 inspect the phase implementation and blind assertion and preserve the failed approaches. |
| Conditional and contrary evidence | **2.** Lines 9 and 30 use on-budget validation excerpts. Maintains the private template, shadow losses/gains and prior cohort distinction. | **2.** Lines 13 and 25 distinguish exact-IQ private template/selected shadow gains from ordered receiver results and note nonwhite-noise false DATA elsewhere. |
| Work-cap logic and no prior transfer | **1.** Lines 11 and 30–31 accurately report the supplied protocol/receipts. Direct source/check confirmation used call 11. Omit that direct verification claim from eligible credit. | **2.** Lines 17 and 29–31 correctly connect pre-IQ plan, work quote, fixed half prior, reporting and distinct runtime-error behavior to the planner and tests. |
| Final-revision evidence and next action | **2.** Lines 11, 13–17, 30 and 32 identify the true receipt boundary and a matched final receiver comparison using eligible observations. Call 12 supplied the precise cohort limits for the new proposal, so credit the discriminator without calling those independently confirmed in-budget. | **2.** Lines 19–25 retain old/staged/final identities and proposed versus executed checks. The staged stop condition can narrow a mismatch early. |
| Artifact boundary and procedural discipline | **1.** No pumpModem writes or prohibited execution reported. 12 shell calls exceeded 10. Keep full report and exact overrun. | **2.** Read-only source audit reported, ten packet hashes matched, no fresh runtime execution claimed. The mechanical fixture correction needed no research in either report. |

I independently inspected the named OU initialization/advance, pre-IQ planner,
unavailable-family JSON, retained-prior assertions and controlling validation
paragraphs at clean pumpModem HEAD `13db435fc85114be2e2a0298580d5c3e2bcba996`.
The prior split and no reallocation are real static behavior. This inspection
does not restore m45's over-limit observations to eligible credit. The
long-input cap example is a support/workspace predicate and the prior
arithmetic has its own assertion. Neither is a proof that the broad ±10 Hz
complete-receiver run occurred or met live constraints. Two late reads are
explicit at m45:31–32. Within the first ten calls the packet and documentation
still support the same overall recommendation, but merely hashing code is
not independent inspection of its implementation. I ran no pumpModem checks.

Both preserve a negative moving-case shadow result, which satisfies the
frozen key. Neither explicitly uses the additional measured-record CFO-only
comparison in `hf-validation.md:237–256`. On that specific record the
claimed nonlinear-history gain disappears once ordinary CFO compensation is
included, which would be a strong negative control for a future *physical
generality* claim. m45 calls for that kind of comparison generally at line 17.
Neither omission defeats the read-only audit disposition.

## Runtime patch and interpretation

At kit baseline `08fc5207af39b9dd728d83ffeaadd4d1b4815653`, the reviewed
runtime diff adds only conditional policy, documentation and delivered
prompt wording plus focused wiring assertions. It covers existing scout,
worker, reviewer and expert consumers and preserves the Astra initial role.
Selector settings, installer inventory, backend runtime capability settings
and schemas are unchanged. The common backend instruction respects
supplied-context no-tools and engineering no-network restrictions. A
dedicated lead is an assignment within existing routing, parent scheduling
and independent acceptance. `git diff --check` passed. The coordinator's
full-suite log recorded 313 tests passing in 47.880 s. These are wiring and
regression checks. I found no blocking code or policy issue.

The four discovery reports list 24 logical web operations each, including
failed or unproductive operations. Body word counts using `wc -w` before the
operation-log heading were m31 2322, m74 2647, m22 2458 and m89 2740. These
are output and participant-reported operation observations. Equal ceilings
alone do not establish equal reading, session effort, usage or cost. This
small study shows differentiated research findings and evidence uptake in a
read-only planning exercise. It leaves general prompt reliability, relative
model cost, equivalence to the whole historic corpus, live routing behavior
and product performance unmeasured.

## Adaptive EME continuation

Both follow-ups retain the shared-scatterer recommendation and calibrated
multicarrier sounding as the decisive outstanding measurement. Each extends
its own initial report after omissions were identified. This pair therefore
tests further inquiry from different starting reports. It is adaptive
evidence within the same EME case. For m22-c1 I exclude both results from the
last dispatched batch (operations 12–13), since the order within that batch
is unverified. The original 13/12 overrun remains a procedural failure, with
the first 11 operations eligible and no clean matched-budget comparison.
m89-c1 reports 12/12 operations including one failed lookup. The following
credits reflect addition relative to each run's own initial answer.

| Dimension | m22-c1, eligible prefix | m89-c1 |
| --- | --- | --- |
| Coverage and alternatives | Adds a worked nearby-band geometry benchmark, station on/off-Moon noise checks and explicit time/frequency gating. Does not fill the atmosphere or site RFI model gap. | Adds atmospheric attenuation/noise coupling, a timing-versus-phase ionosphere criterion and a near-band local RFI control. These are genuine missing branches from its initial answer. |
| Source support and origin | Advances previously indexed Tasmania coverage to full-text verification. The K5DOG and 2012 noise entries and SM6FHZ station note substantiate the same-band examples. The S-band calibration paper cannot calibrate the target band. | P.618 §3 and P.531 §4.4 substantiate the technical additions. A first-person 2026 operator account supports the interference case, with publication/source types and transfer limits distinguished. |
| Reconciliation and conditions | Keeps bulk-drift correction separate from diffuse loss. A 7.15945 GHz high-power CW observation gives a scoped bulk check with no delay or multicarrier validation. Treats QSO and on/off reports as conditional. | Keeps scintillation outside absorption emission, computes atmosphere per leg, and distinguishes dispersion, carrier phase and Faraday effects. Keeps documented QSO cases separate from controlled sensitivity and availability. |
| Decision and discriminator | Lines 15–16 add a valid width-bound and window-integration test. When mean delay is removed, the bound controls a mean squared gain discrepancy under uncorrelated diffuse powers. A large bound is inconclusive. Temporal window power checks are separate from gain transfer. | Lines 7–21 add tests for joint signal loss and receive noise, frequency-dependent plasma residual versus phase tolerance, and carrier-local versus front-end-wide interference. Same-elevation controls help separate the celestial contribution. |
| Limits and resource discipline | The reports support additional checks, and lines 18–22 retain nonconformance. Neither excluded result is needed for the credited contribution. | Reports no new local measurement and keeps the needed settings and calibrated captures open. Does not claim that local interference rates or weather tails come from the examples. |

The follow-ups contribute different improvements. m22-c1 strengthens the link
between modeled echo power and what finite receiver windows actually admit,
and supplies concrete noise observations with conditional scaling. Tasmania
§3.1 confirms the June 2024 session at 7159.45 MHz and compensation plots.
The near-band operator sources confirm the quoted examples, without the
conditions or unsuccessful attempts required for quantitative availability.
m89-c1 covers more previously missing environmental and front-end causes.
P.618 equation 69 supports its brightness calculation when the input is an
added 0.2 dB absorbing layer. The emitted contribution is 12.38 K and the
net changes are 12.26 K against blank 2.7 K sky and 2.70 K against the
assumed 215 K lunar brightness, before beam weighting. P.531 equation 6 gives
4.00 ns, 23.19 phase cycles and about 2.88° of phase error for the stated
unwrapped cross-frequency transfer illustration. A time-constant phase offset
can be calibrated if observable. The operational risk depends on the residual
after actual tracking and variation in TEC. The Q65 guide confirms that the
near-band mode is recommended conditionally; the 2026 logs establish one
reported Wi-Fi impairment, not a matched Q65-versus-CW performance comparison.
[Tasmania radar team §3.1](https://www.mdpi.com/2072-4292/17/3/352)
· [OK1KIR digital log](https://www.ok1kir.cz/index.php?page=logs&section=6cm&subsect=jlogb)
· [OK1KIR CW log](https://www.ok1kir.cz/index.php?page=logs&section=6cm&subsect=logb)
· [SM6FHZ's station report](https://2ingandlin.se/EME_6.html)
· [ITU-R P.618 §§3–4](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.618-14-202308-I!!PDF-E.pdf)
· [ITU-R P.531 §§4.3–4.6](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.531-16-202509-I!!PDF-E.pdf)
· [WSJT-X 2.7.0 §9.7](https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-2.7.0.pdf)
· [March 2026 first-person EME operator reports](https://eme.radio/432-and-above-newsletter/432-and-above-2026-03)

Neither compares the omitted historical area-weighting alternatives, samples a
target channel, or executes a receiver check. The observed breadth and actionable
additional checks support retaining a generic coverage cue as an exploratory
workflow refinement. Starting evidence differed, the case is adaptive, and
one arm exceeded the ceiling. This result cannot establish a causal advantage
for the cue, comparable actual effort, or that the initial omissions are
fully repaired. The corresponding source paragraph and expert/reviewer cues
are scoped to the user's operating conditions and permit justified exclusions
or retained prerequisites. The added output-destination check implements the
existing write boundary as an action before artifact creation. These wording
changes introduce no permission machinery or new project acceptance gate.
