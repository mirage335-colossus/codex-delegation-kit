# EME reference map and depth criteria

## Assignment and evidence boundary

This is an evaluator map for an EME study that is intended to have breadth and
technical depth comparable to the combined reference corpus. Judge whether a
study supplies equivalent decision-relevant evidence and reasoning, not whether
it copies this bibliography, matches its word count, or follows its exact model.
An alternative source, derivation, or implementation is acceptable when it
supports the same claim at a comparable or better evidence level and its domain
and transfer limits are made explicit.

The read-only source is `/home/user/___quick/p/_cur/dataPump/pumpModem`, pump
HEAD `13db435fc85114be2e2a0298580d5c3e2bcba996`. The available corpus inventory
records pre-existing edits in that checkout; none were changed. This map was
written only to the requested kit study path. The main reference targets are:

- `_ref/highFidelity-triple_Robust_Modem/Fable-5.2/40-eme-lunar-scattering-and-geometry.md`
- `_ref/highFidelity-triple_Robust_Modem/Fable-5.2/41-eme-systems-practice-and-environment.md`
- `_ref/highFidelity-triple_Robust_Modem/Fable-5.2/84-scenarios-eme.md`
- `_ref/highFidelity-triple_Robust_Modem/Astra-6/40-earth-moon-earth-5p8ghz.md`

Section locators below use these short names: **F40**, **F41**, **F84**,
**A40**. Line numbers refer to the inspected source snapshot. Also inventoried
but not substantively read for this task: Fable-5.2 `00`, `55`, `60`, and `90`.
They provide broader corpus context on experiment contracts, front-end effects,
simulation/validation practice, and independent arithmetic; do not treat their
inventory-only headings as additional evidence in this map.

## Read coverage

I inventoried every heading in all four target files. I read the main bodies in
bounded chunks, including the complete F84 scenario and its numerical checks;
the F40 and F41 literature, operator, environment, comparison, unresolved-work,
and completion-pass sections; and the A40 evidence ledger, physical model,
weather/noise, illustrative budget, implementation candidates, validation
limits, and source register. I followed the F40/F41 cross-references into their
source-to-scenario closure, data/calibration, and residual-boundary sections.
The chapter references themselves report mixed access status: full articles,
page images, abstracts/previews, secondary reports, and failed or unavailable
routes are explicitly differentiated. This is a map of those contents, not an
independent re-audit of all cited papers or raw datasets.

Heading inventory for the four requested chapters:

- **F40:** `#` overview; `## Physical mechanisms` (extended-target radar
  equation, components, delay, Doppler, coupling, fading); `## Measured and
  reported values` (cross-section, path loss, scattering/delay, polarization,
  libration, spectrum/coherence, amplitude, beam effects, spatial decorrelation,
  geometry, recent/direct and historical radar); severity table; literature
  models; high-fidelity simulation; preset comparison; contradictions/open
  questions; dated source-decision/completion pass; search coverage; references.
- **F41:** `#` overview; mechanisms; measured values (history and practice,
  modes, fading, receiver noise, weather, ionosphere, polarization/pointing/
  frequency control, link budget); severity table; model/simulation; high-
  fidelity simulation; preset comparison; contradictions/open questions; dated
  public-record, data/calibration and source-disposition pass; search receipt;
  references.
- **F84:** frozen inputs/geometry; deterministic scattering/coupling; budget
  and severity; measurement/acceptance limits; competing branches; frozen kernel,
  polarization and numerics; severity/discrimination controls; reproduced
  arithmetic; executed retarded geometry/surface/thermal checks; source closure
  and remaining boundaries.
- **A40:** evidence ledger; bulk delay and distributed echo; bistatic geometry,
  offset/spread, pointing/aperture; lunar/Galactic/solar/receiver noise;
  ionosphere/troposphere/weather; assumption-labeled link calculation; moderate,
  adverse and outage cases; native implementation candidates; validation and
  unresolved evidence needs; annotated source register.

## Evaluation criteria

Treat each item as a substantive coverage test. A topic is covered only if a
claim, evidence or derivation, applicability boundary, and implication for the
scenario are present. A heading or a list of papers alone is not coverage.

1. **Define the path, observable, and evidence status.** Separate passive
   Earth–Moon–Earth scattering from active lunar-orbiter downlink and orbital
   SAR. Define carrier, polarization channel, geometry, receiver reference
   plane, and the target observables. Distinguish measured values, reported
   practice, standards, model assumptions, and new derivations; preserve source
   access status and do not promote abstracts, local products, or search hits to
   full-text evidence. Locators: F40 lines 1–12, 530 onward; F41 lines 1–10,
   663 onward; F84 lines 1–20; A40 lines 1–32, 149 onward.

2. **Derive an extended-target link budget.** Give the radar equation and
   projected-disc cross-section definition with units, range dependence,
   wavelength, gain and polarization accounting. Explain when whole-disc
   assumptions hold and how finite/different TX/RX beams and ranges change the
   integral. Quantitatively check at least one worked target-band case and
   distinguish isotropic loss, antenna gains, net loss, received power and
   C/N0. F40 lines 16–22, 87–107; F41 lines 14–26, 226–248; F84 lines 161–185,
   537 onward; A40 lines 89–115.

3. **Explain lunar scattering physics and competing shapes.** Cover the
   quasi-specular/Hagfors-like highlight and diffuse/rock or regolith return,
   their angular behavior and the limits of assigning a unique physical
   roughness or coherent component. Compare materially different candidate
   kernels (e.g. measured angular law, Hagfors-plus-diffuse, uniform surface or
   projected disc, or a well-justified alternative). Identify which components
   represent amplitude/power statistics versus deterministic paths. F40 lines
   22–30, 108–174, 336–370; F84 lines 89–160, 242–295; A40 lines 34–72,
   116–135.

4. **Resolve delay support, power-delay profile, and geometry.** Derive bulk
   round-trip delay separately from lunar-disc excess delay. Relate surface
   incidence/ring area to delay and state the full geometric support versus
   power quantiles (t50, t90, RMS, support). Make the area measure explicit;
   show that projected-area and surface-area weighting differ, and avoid calling
   a single median delay the complete response. F40 lines 30–34, 108–159, 276–286,
   385–400; F84 lines 35–88, 186–213, 488–536; A40 lines 34–54.

5. **Resolve Doppler center, spread, and delay–Doppler dependence.** Distinguish
   center shift, rate, limb-to-limb support, central power bands, PSD FWHM,
   PSD-autocorrelation width, visual width, and field-correlation time. Explain
   libration plus Earth-rotation contributions and how separated stations alter
   the vector sum. Show why delay and Doppler are jointly constrained by the
   scattering geometry rather than independent free parameters. F40 lines
   34–48, 175–246, 276–306, 385–400; F84 lines 89–160, 186–213, 396–435,
   537 onward; A40 lines 55–72.

6. **Handle bistatic and retarded geometry at the right fidelity.** State when
   monostatic approximations are used and what changes for two stations: actual
   TX and RX surface angles, mutually visible surface, bistatic angle, retarded
   epochs, path-length derivative, sign convention, and independent geometry
   check. If an ephemeris or station fixture is used, pin its source/version,
   coordinates, time system, frame, and limits. Locators: F40 lines 34–48,
   276–306; F84 lines 19–88, 89–160, 537 onward; A40 lines 34–72.

7. **Quantify polarization and state the convention.** Define circular-sense
   convention in each propagation direction; distinguish selected OC return,
   same-sense/depolarized power, linear mismatch, feed leakage, and antenna
   calibration. Include angle-dependent or competing ratio evidence where
   available; an integrated ratio alone is insufficient if angular dependence
   affects the illuminated region. F40 lines 160–174, 385–400, 439–452; F41
   lines 216–248; F84 lines 242–395, 537 onward; A40 lines 7–8, 64–72.

8. **Couple beam, pointing, gain, lunar noise, and speckle.** Explain that dish
   narrowing changes the echo weighting and delay/spread while also increasing
   gain and lunar thermal-noise fill. Include pointing offsets, beam overlap,
   antenna patterns, spatial speckle scale/decorrelation, and why separated
   receivers or self-echo replays do not automatically provide independent or
   matched two-station realizations. F40 lines 254–275, 347–384; F41 lines
   16–24, 216–248, 350–406, 548 onward; F84 lines 19–34, 89–160, 436 onward;
   A40 lines 67–72, 116–135.

9. **Treat noise at the receiver reference plane.** Include receiver noise,
   sky/celestial and ground pickup, lunar brightness/antenna temperature,
   beam fill, feed loss and receiver temperature. Keep brightness temperature,
   antenna temperature and total system temperature distinct. Show noise
   effects separately from signal loss and preserve nonreciprocity when the two
   receive ends have different beams/noise. F41 lines 130–166, 226–248,
   548 onward; F84 lines 19–34, 396–435; A40 lines 73–88.

10. **Cover terrestrial propagation and weather per endpoint.** Include gas,
    rain attenuation and emission, cloud liquid water, tropospheric
    scintillation/refraction and low-elevation multipath, plus ionospheric
    Faraday rotation, delay/phase and scintillation where relevant. Tie standard
    models to site/elevation/weather inputs; distinguish measured statistics
    from frequency-scaled satellite analogies and explicitly address the two
    legs' dependence instead of silently multiplying independent fade models.
    Locators: F41 lines 167–215, 249–284, 285–329, 407–548; F84 lines 19–34,
    436 onward; A40 lines 83–88, 116–149.

11. **Cover equipment and operator practice with evidence.** Include usable
    transmit power, dish/feed/LNA/noise figure, frequency reference/tracking,
    pointing, polarization practice, and relevant operator reports or actual
    contacts. Separate operational success and reported signal levels from
    calibrated sensitivity, receiver performance, or channel statistics.
    Address solar noise, local RFI (including reported in-band interference),
    wind/pointing, availability windows, and practical mode thresholds with
    evidence quality identified. F41 lines 30–129, 216–248, 350–406, 407–548,
    607 onward; A40 lines 73–88, 116–135.

12. **Make quantitative derivations reproducible and dimensionally checked.**
    Show equations, units, interpolation/weighting, assumptions, and at least
    one independent arithmetic or numerical cross-check for decision-driving
    values. Distinguish sensitivity brackets from confidence intervals and
    state when input data lack coverage. Preserve differing estimators until
    reconciled; do not use agreement between two calculations as evidence that
    the assumed lunar model is true. F40 lines 54–159, 175–246, 385–400;
    F41 lines 226–248, 407–548; F84 lines 242–436, 488–695; A40 lines 89–115.

13. **Compare implementation alternatives and disclose omissions.** At minimum
    compare a low-cost fading/scalar model with a structured delay/Doppler or
    scatterer model and a measurement-replay/hybrid path when data exist. State
    what each loses (delay coupling, frequency selectivity, polarization,
    spatial correlation, nonstationarity, beam dependence); identify a native
    integration path and numerical/cost tradeoffs if implementation is in
    scope. F40 lines 336–370; F41 lines 285–313; F84 lines 214–241, 436–487;
    A40 lines 116–135.

14. **Connect the channel to a named modem/receiver and measurable outcomes.**
    Name waveform bandwidth, symbol/bit/slot duration, tracking assumptions,
    input PSD/reference plane, and receiver observables. Compare literature
    channel numbers to actual receiver requirements without treating a nominal
    “Doppler spread” or delay preset as a complete physical channel. Include
    calibrated waveform captures/replay or a concrete validation plan that
    distinguishes echo absence, search miss, acquisition/tracking loss,
    invalid capture, decoding failure, and true completion. F40 lines 372–384;
    F41 lines 314–329; F84 lines 186–241, 436–537; A40 lines 126–148.

15. **Specify numerical and physical validation separately.** Include geometry,
    path/Doppler sign, units, normalization, convergence, covariance and power
    checks; then separately identify empirical validation needed for the
    scattering/fading model. State actual runtime/check evidence versus
    proposed checks, and do not call numerical agreement, fit to classical
    data, or internal simulation validation a 5.8-GHz field validation. F84
    lines 186–241, 242–395, 488 onward; F40 lines 347–370; A40 lines 136–148.

16. **Use recent sources and empirical contrary evidence correctly.** Search
    current primary/official records by specific band, geometry, observable,
    calibration, and date; report what was actually opened and read. Preserve
    counterevidence: cross-section outliers and uncertainty; disagreement in
    diffuse fractions and delay/width estimators; calibration problems in
    modern maps; local opposition/terrain effects; plus findings that do not
    transfer from SAR, downlink, or 6-m radar. Do not imply exhaustive coverage
    when searches were bounded. F40 lines 287–306, 385–529; F41 lines 330–407,
    407–548, 607–662; F84 lines 214–241, 695 onward; A40 lines 7–32, 149–172.

17. **Expose unresolved evidence needs even when the model is fully specified.**
    Keep external measurements separate from choices that make a simulation
    runnable. In this corpus, material open gaps include calibrated 5–6 cm
    whole-disc cross-section/scattering/polarization and Doppler spectrum,
    matched two-station complex captures, measured joint frequency covariance,
    dish-size/beam validation, echo versus libration state, site-specific
    noise/weather and two-leg scintillation dependence, and modem end-to-end
    field qualification. Local SAR, planetary speckle, amateur visual widths,
    low-frequency IQ, or a detailed retarded-geometry calculation do not close
    those gaps. F40 lines 385–400, 453–529; F41 lines 330–341, 519–662; F84
    lines 214–241, 488 onward; A40 lines 136–148.

18. **Preserve joint dependence and severity provenance.** Specify whether
    scattering, geometry, antenna beams, polarization, phase, noise, weather,
    pointing, and tracking are coupled or conditionally independent. Use matched
    baselines and declared moderate/adverse/outage/discriminator branches; mark
    stress combinations as synthetic unless jointly observed. State that a
    seed set or severity table is not a natural frequency-of-occurrence
    distribution. F40 lines 307–335, 347–370; F41 lines 249–284, 285–313;
    F84 lines 161–241, 242–487; A40 lines 116–135.

## Corpus-specific unresolved claims a comparable study must retain

These are not requirements to reproduce F84's chosen kernel. They are
boundaries against overclaiming unless a new, applicable source or matched
measurement genuinely resolves them:

- The target-band cross-section and angular law are extrapolated from nearby
  wavelengths; the nominal `η=.065` and alternative `.040` are working cases,
  not calibrated coverage intervals.
- The 3.8-cm Hagfors fit is imperfect; diffuse fraction varies by source and
  decomposition. The classical fit is useful as an empirical shape, not a
  unique physical roughness or all-angle electromagnetic law.
- There is no matched calibrated whole-disc 5–6 cm two-station complex echo
  record in the bounded search reported here. Recent Mini-RF X/C data are
  local Earth-to-orbit SAR; ngRadar imaging is local; 433.8-MHz SigMF data are
  self-echo and lack absolute calibration. They offer constrained observations,
  not substitutes for that measurement.
- Width quantities are estimator-dependent. F40's full-table surface-area
  delay reconstruction (~0.75 ms) and F84's sparse T52 value (~0.708 ms) are
  model calculations; F41 also preserves a different K1JT-derived estimate.
  None is a measured 5.76-GHz delay statistic. Visual echo widths near a
  libration minimum are not a calibrated power spectrum.
- The 5.76-GHz polarization ratios, cross-channel correlation, speckle
  independence, opposition-effect multiplier, and terrain-dependent variation
  remain assumed or weakly transferred. Calibration/crosstalk in local orbital
  products further limits polarization transfer.
- Lunar brightness-temperature literature and system-noise accounting differ;
  the 225-K comparator and 80-K total Tsys in F84 are explicit assumptions,
  not independently measured station values. No universal weather, ionosphere,
  solar-noise, or interference margin is established.
- Interstation scintillation dependence and the effect of an extended,
  already-speckled target on point-source scintillation models are unmeasured.
  No availability or success probability follows from a scenario's stress
  cases.
- A fully specified deterministic ephemeris and converged numerical surface
  integral validate implementation consistency only. The reduced renderer,
  full receiver run, completion/quiet-tail behavior, and target-band field
  validation remain separate acceptance questions in the source.

