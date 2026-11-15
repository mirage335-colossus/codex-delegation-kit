> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Earth–Moon–Earth scientific adjudication

The frozen EME comparison is met with a supported empirical boundary. Eleven essential rows are Supported, EME-11 is Supported boundary, and all six depth dimensions are Supported. No necessary-input judgment is held. The original evidence supports a conditional 5.76 GHz channel design and establishes neither target-band field calibration nor receiver or capacity qualification.

## Decisions carried by the original research

- Use a public, retarded two-station bulk delay and correction reference and preserve continuous receiver state. The author's selected centre path is 2.4836116705 s with +2,919.428095 Hz offset, while the nearest-surface reference used for the waveform contract is 2.4720213723 s. Their first large-absolute-time finite-difference method disagreed by up to 0.118 Hz. The corrected relative-time method and independent ephemeris comparison bound that numerical issue. F84:537–627.
- Compare a reduced joint delay–Doppler operator against the bounded retarded surface integral, holding signal and public conditions fixed. The full-disc law has 11.590685 ms monostatic excess support and much shorter power quantiles. Its complex field covariance at 75 Hz is neither zero nor one. Equal link budgets or one named width cannot settle the receiver-equivalence question. Preserve beam-dependent thermal noise and its input reference plane alongside signal weighting. F84:186–240,488–535,629–671 and F70:224–271.
- Use the original public-observable checks to limit transfer. F41's Dwingeloo self-echo result is 2.43632 s and −253.0 Hz relative to the direct copy, supported by split windows and displaced controls. Its positive-only search initially found a chirp ambiguity. The two split windows share one packet. Local Mini-RF CPR is a reproducible Stokes-product observable on 548,573 usable pixels, with 6.619×10⁻⁸ maximum formula residual. The local footprint, instrument calibration and H/V leakage prevent whole-disc or Earth-received voltage inference. F41:407–517. [Dwingeloo archive](https://zenodo.org/records/5832579), [Mini-RF PDS4 observation](https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_minirf_bistatic/data_derived/2026_164_1/), [Chan et al. calibration study](https://www.hou.usra.edu/meetings/lpsc2025/pdf/2294.pdf).
- Treat visual 5.7 GHz widths, PSD-autocorrelation widths and central power widths as different estimators. F41:110 offers an approximate Q65 comparison across unlike widths, and F41:623,652–661 expressly retain the uncertain simulator version and estimator mismatch. That early numeric threshold comparison cannot establish a median target-band transfer or a Robust threshold. F40:226–245,385–388 and F90:355–411 supply comparable, separate quantities. [Taylor's original methods and observation account](https://www.dxmaps.com/emelibration.html), [Suckling's 5.7 GHz visual comparison](https://bobatkins.com/radio/data/G3WDG_libration_paper_revised.pdf).

## Independent verification

The evaluator reran an inspected, standalone Python calculation with the supplied inputs. After correcting an inaccurate rounded projected-disc reference in the evaluator’s first assertion, the final run passed 22 assertions. The original failed assertion and corrected output are retained in desk_check_initial.log (historical locator: `desk_check_initial.log`; artifact not bundled) and desk_check.log (historical locator: `desk_check.log`; artifact not bundled). At 5.76 GHz the check gives T52 t50/t90 of 0.707954/5.086941 ms. An unintended extra cosine for the same per-surface-area law shifts those to 0.486417/3.626442 ms and raises |R(75 Hz)| from about 0.676 to 0.788. With the original coupling and retarded vectors it gives 26.855 dB-Hz for 3 m. The 7 m noise-plane calculation reproduces 142.490 K and the two-ended rain calculation gives 5.943 dB C/N0 degradation. These are checks of stated inputs and methods. [Lincoln Laboratory report, Table II and §III.A.1](https://ntrs.nasa.gov/api/citations/19670030824/downloads/19670030824.pdf), [ITU-R P.838-3](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.838-3-200503-I%21%21PDF-E.pdf).

The independent primary literature check confirms how misleading nominal frequency proximity can be. Sun et al. used a 7,209.125 MHz source and two Earth radio telescopes, reporting 0.06 OC reflectivity and CPR 0.44–0.45 for a constrained Mare Imbrium footprint. Peters et al. used DSS-13 and LRO for local imaging and reported polarimetric channel leakage. The archive relationship is meaningful at its processed-product plane. The original paired-source conclusions keep both distinct from calibrated two-station whole-disc 5.76 GHz observations. [Sun et al., §§2–4](https://pmc.ncbi.nlm.nih.gov/articles/PMC7180880/), [Peters et al., abstract and §II.B](https://www.researchgate.net/publication/399711673_Mini-RF_XC-Band_Bistatic_Synthetic_Aperture_Radar_Architecture_Polarimetric_Observations_and_Implications_for_Future_Systems).

The historical source used for read-only context is `13db435fc85114be2e2a0298580d5c3e2bcba996`. SHA-256 values matched the packet for `src/tuning_presets.cpp`, `src/triad_stream_receiver.cpp`, `src/triad_receiver_fine.cpp`, `include/datapump/triad_receiver.hpp`, and `include/datapump/triad_stream_receiver.hpp`. The 6 Hz/0.5 ms existing control and public profile bindings are present. The 350 Hz public fixture bound also exceeds the historical coherent-gain-block branch's centre-grid limit if that branch is attempted, since its minimum interval is 0.25 s and the gate is a product greater than 8. Other paths have different admission rules. That static observation is an implementation discriminator, with no production run or conclusion about complete receiver performance. `historical-project/src/tuning_presets.cpp:20–30`, `historical-project/src/triad_stream_receiver.cpp:166–177`, `historical-project/src/triad_receiver_fine.cpp:2035–2054`.

## Row findings

Locators below use these names for the original, credited submission files.

- A40 `submission/_ref/highFidelity-triple_Robust_Modem/Astra-6/40-earth-moon-earth-5p8ghz.md`
- F40 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/40-eme-lunar-scattering-and-geometry.md`
- F41 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/41-eme-systems-practice-and-environment.md`
- F55 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/55-equipment-and-front-end-effects.md`
- F70 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/70-implementation-options.md`
- F80 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/80-completion-plan.md`
- F84 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/84-scenarios-eme.md`
- F86 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/86-statistics-and-calculation-checks.md`
- F90 `submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/90-cross-check-calculations.md`

### EME-01 · Supported

Defines the 5.760 GHz two-Earth-station geometry, reference planes, polarization and measured or calculated observables. Same-band or nearby-frequency imagery and an active downlink are differentiated from a passive communications echo.

- Original represented evidence. Derived and proposed path and receiver-plane definition, F84:3–33 and 186–212. Source observations with geometry and transfer limits, A40:7–31 and F40:287–297,410–430.
- Consequential obligation provenance. Explicit task requirement for passive EME near 5.8 GHz and received levels/polarization, task.md:8–14. Demonstrated reference attainment for distinguishing orbital, downlink and passive radio observables, comparison/map-eme.md:76–83.
- Independent check. Sun et al. (2020), §§2–4 and Table 1, documents Earth-based receivers, 7,209.125 MHz and a localized Mare Imbrium footprint. Peters et al. (2026), abstract and §II.B, documents DSS-13 to LRO and calibration-dependent focused Stokes products.

### EME-02 · Supported

Status and assumptions of albedo are explicit. The fixed whole-disc normalization, two ranges, two power beams, port gains, carrier power and receiver input noise are independently accounted for. The original executes surface-weighted coupling and refinement, beyond scalar budget substitution.

- Original represented evidence. Derived link equations, F40:16–20 and F84:89–122,161–179. Performed budget and fixed-normalization finite-beam sweep, F84:629–671 and F90:317–334,413–425. Source observations and cross-section spread, F40:54–85.
- Consequential obligation provenance. Explicit task requirement to represent received levels and front-end/noise, task.md:10–14. Demonstrated reference attainment for independent arithmetic and separate finite-overlap integral, comparison/map-eme.md:85–92,174–181.
- Independent check. desk_check.log:13–17 reproduces the 284.141 dB wide-beam case and 26.855 dB-Hz selected-epoch case using supplied retarded vectors and coupling factor. Sun et al. (2020), §§2–3, distinguishes footprint area and polarization-specific cross section.

### EME-03 · Supported

Compares endpoint and interpolated angular laws, normalized Hagfors-plus-diffuse alternatives, uniform surface/projected comparators and conditional bistatic-law branches. Retains the poor short-wavelength fit, nonunique roughness, and distinction between a mean-power highlight and a coherent specular path.

- Original represented evidence. Source observations of empirical laws, conflicting diffuse fractions and fit limits, F40:108–174,410–447. Derived and proposed matched-power families, F84:242–296. Performed multi-law quadrature, F90:355–411.
- Consequential obligation provenance. Demonstrated reference attainment for comparing the angular shapes, normalization, material and coherence limits, comparison/map-eme.md:94–102 and 174–181. Explicit task requirement to choose the simplest useful representation, task.md:10–15.
- Independent check. LL67 Table II printed p. 6 (PDF index 8) confirms the surface-area convention and selected 3.8/23 cm entries. desk_check.log:4–10 reproduces the sparse interpolated kernel. The extra cosine lowers raw albedo and moves the delay quantiles.

### EME-04 · Supported

Separates seconds of travel from milliseconds of geometric echo support and from weighted power-delay statistics. The original compares alternate area weights and a measured historical pulse-length curve, and keeps scalar, retarded and literature estimators distinct.

- Original represented evidence. Derived bulk/excess definitions and area Jacobian, F40:30–32 and F84:124–148. Performed source-area/alternate-area and waveform-independent checks, F40:142–157 and F84:488–518,629–639. Source observation of the 68 cm pulse-length curve, F40:156–157.
- Consequential obligation provenance. Explicit task requirement for delay behavior, task.md:10–14. Demonstrated reference attainment for geometric versus power support, area comparison and observed limits, comparison/map-eme.md:104–111.
- Independent check. desk_check.log:1–10 reproduces 11.590685 ms support, T52 t50 0.707954 ms and t90 5.086941 ms. A duplicated cosine gives 0.486417 and 3.626442 ms. LL67 Table II and §III.A.1 specify the surface-area quantity.

### EME-05 · Supported

The same path supplies offset, rate, ring delay and residual surface Doppler. The original reports an approximately 86.74 Hz extent, 16.05/53.77 Hz central 50%/90% power widths and 13.04 ms to half field correlation in one executed fixture. Its reconciled treatment preserves why those estimators differ.

- Original represented evidence. Derived ring/Doppler, vector-sum and width relationships, F40:34–48,226–246. Performed finite difference, surface/frequency and multi-width checks, F84:506–529,605–638 and F90:355–411. Source observations of visual and autocorrelation widths, F41:120–129,652–661.
- Consequential obligation provenance. Explicit task requirement for frequency/time behavior, task.md:10–14. Demonstrated reference attainment for coupled geometry, materially distinct widths and coherence, comparison/map-eme.md:112–119. Transfer of unrelated threshold curves would be an interpretation extending that evidence, comparison/map-eme.md:194–200.
- Independent check. Taylor’s author text, Amateur Libration Measurements, defines widths from PSD autocorrelation and separately describes full extent. Suckling’s primary operator report table lists 35/20 Hz apparent widths against 38/25 Hz predictions at 5.7 GHz. desk_check.log:8–10 verifies an intermediate 75 Hz covariance magnitude under the stated delay law.

### EME-06 · Supported

Compares geocentric and station-dependent delay/rates with the retarded bistatic fixture. Includes joint visibility, time and frame handling, independent DE441 plausibility comparison, a surface bulk reference and a corrected floating-epoch finite-difference failure. Reported numerical precision is bounded.

- Original represented evidence. Derived geocentric versus topocentric and reception-epoch sensitivities, F40:276–285. Performed visibility, retarded reference, station-reversal and Horizons checks, F84:537–627,673–693.
- Consequential obligation provenance. Demonstrated reference attainment for comparing the practical geometry choices with framed and timed evidence, comparison/map-eme.md:121–127,174–181. Pinning the selected solver and ephemeris follows from traceability when those inputs are used, comparison/acceptance.md:23–29.
- Independent check. JPL Horizons API VEC_CORR documentation confirms geometric NONE versus light-time-corrected output. desk_check.log:11–14 recomputes the two centre-leg times from the reported vectors. CSPICE itself was not independently rerun.

### EME-07 · Supported

Defines propagation-direction circular sense and distinguishes lunar OC/SC, antenna projection, crosstalk and port noise. Ratio-versus-angle and integrated-only alternatives have different footprint sensitivities. Local PDS CPR recomputation and the primary calibration caveat support the decision to retain a sensitivity bracket for 5.76 GHz polarization. For ideal circular propagation, F41 and A40 account for linear-basis Faraday rotation without charging linear projection loss to an ideal circular port. They retain a full calibrated Jones transfer as open.

- Original represented evidence. Source observations of angular ratios, calibration and unmatched equipment, F40:160–174,410–430 and F41:216–224. Derived/performed angular and integrated ratio comparisons plus local product reanalysis, F40:439–443, F41:482–517 and F84:315–328. Proposed port mixing, F84:298–313. Derived and source-supported mismatched linear projection and circular limit, F41:195–224 and A40:83–87. A calibrated general Jones transport is absent, F84:298–328.
- Consequential obligation provenance. Explicit task requirement for relevant polarization, task.md:10–14. Demonstrated reference attainment for convention, angle weighting and calibration-limited transfer, comparison/map-eme.md:129–135. Demanding fitted general Jones statistics for the ideal OC branch would extend the criterion. The frozen map explicitly preserves unmatched station and image transfer limits, comparison/map-eme.md:129–135,263–266.
- Independent check. Chan et al. (2025), pp. 1–2, and Peters et al. (2026), §II.B, document receive-channel leakage and corrections in local orbital products. Sun et al. (2020), §§2–4, reports simultaneous selected opposite/same circular channels and CPR 0.44–0.45 from limited local footprints, and documents the footprint conditions for their transfer.

### EME-08 · Supported

Compares beam narrowing and pointing through gain, finite overlap, delay and Doppler changes, plus lunar beam filling. Noise accounting keeps sky, Moon, ground, spillover, feeder and receiver at a named plane. Speckle-scale predictions and matched/no-matched replay implications are qualified.

- Original represented evidence. Derived beam and speckle weighting, F40:254–274,443–449. Source observations of beam/pointing and site noise, F41:130–166,216–224,603. Performed antenna/thermal sweep, F84:629–671. Site calibration remains absent, F41:558–574.
- Consequential obligation provenance. Explicit task requirement for noise, levels and front-end effects, task.md:10–14. Demonstrated reference attainment for a coupled beam/noise/speckle comparison and plane accounting, comparison/map-eme.md:137–152.
- Independent check. desk_check.log:18–20 independently reproduces 20.334 K lunar increment at 3 m and the 142.490 K beam-consistent result at 7 m. The SM6FHZ primary 5760 MHz station page reports on-Moon versus cold-sky noise and identifies the specific observation and hardware.

### EME-09 · Supported

Conditions paths on each endpoint and receiver emission, separates ground/masks, weather, solar noise, interference and lunar fading, and connects operational pointing and correction to a 26.4 s bit. Formal analogies and single-station reports do not establish an EME weather or clock population.

- Original represented evidence. Source observations of band-specific practice, interference, calibration and satellite limits, F41:69–84,216–224,519–532,601–605 and F55:288–312. Derived/performed rain, loss/emission, correlation and clock comparisons, F41:167–215,576–599 and F55:381–405. Proposed native correction and separate weather branches, F84:364–394,448–472.
- Consequential obligation provenance. Explicit task requirement for front ends, interference and severe/outage states, task.md:10–14. Demonstrated reference attainment for endpoint atmosphere and operational evidence with transfer limits, comparison/map-eme.md:154–172. Site-specific distributions are scientific transfer inputs, never supplied by an assumed weather case, comparison/map-eme.md:220–230.
- Independent check. Official ITU-R P.838-3 Eq. 4–5 defines polarization-dependent rain coefficients. desk_check.log:21–23 reproduces the 5.943 dB two-ended C/N0 sensitivity. Fang–Pontes (1981), pp. 293–320, reports strong satellite scintillation events and limits of weak frequency scaling. Moncur and Taylor’s report, pp. 1–2,7, links GPS locking and automatic correction with actual 10/24 GHz JT4 operating conditions.

### EME-10 · Supported

Ranks cheap scalar controls, coupled annular/tapped representations, explicit surface geometry, and calibrated replay by the observables each retains. Names receivers, native integration, bandwidth and timing, reference and public/private planes, cost scaling and a same-stream discriminator. No renderer execution is claimed.

- Original represented evidence. Proposed fidelity alternatives and native boundaries, A40:126–148, F40:336–384 and F70:42–85,117–159,224–271. Source observation of existing model and receiver interfaces, F70:61–85, F41:314–326. Derived scale and performed mathematical checks feeding the choice, F70:233–249 and F84:488–535.
- Consequential obligation provenance. Explicit task requirement to preserve native reception, public hypotheses, calendar and capacity, task.md:15–20. Demonstrated reference attainment for fidelity, cost, equivalence limits and decision/validation specification, comparison/map-eme.md:183–201. An executed production-renderer or capacity qualification would extend this research criterion, comparison/acceptance.md:56–75 and 95–103.
- Independent check. Historical production at 13db435fc85114be2e2a0298580d5c3e2bcba996: src/tuning_presets.cpp:20–30, src/triad_stream_receiver.cpp:166–177 and include/datapump/triad_receiver.hpp:43–50 show the 6 Hz/0.5 ms control and public receiver/configuration admission. historical-project/src/triad_receiver_fine.cpp:2035–2054 shows a separate coherent-work admission boundary. This is a source-only check of the historical receiver.

### EME-11 · Supported boundary

Original execution covers robust target-band numerical checks and two primary observable types. The 433.8 MHz echo establishes relative delay and sign. The local 7.147 GHz orbital products establish a processed polarization identity. Both preserve observed failures and limits. They conditionally support a geometry-coupled diagnostic and withhold whole-disc calibration.

- Original represented evidence. Performed target-band arithmetic, DE440 and multi-law convergence, F84:488–535,537–693 and F90:355–411. Performed raw LoRa and derived local Stokes/CPR reanalysis with rejected and adverse cases, F41:407–517. Absent calibrated target-band whole-disc interstation complex observations, F41:400–405 and F84:695–716.
- Consequential obligation provenance. Demonstrated reference attainment for a target-band numerical and suitably bounded primary-observable discriminator, comparison/map-eme.md:202–230 and 241–278. Empirical calibration is an explicit conditional scientific boundary in comparison/coverage-matrix.json EME-11. Treating it as a required field trial would extend the frozen criterion, comparison/acceptance.md:40–49.
- Independent check. Desk arithmetic passed 22 assertions, including area-weighting adverse case and side-by-side link/noise scales. Zenodo record confirms the original 96 MB LoRa file identity/advertised MD5 and clock warning. The PDS4 observation directory confirms exact product stem, 3,579,756-byte entries and locality in the archive. Peters/Chan independently bound instrumental transfer. F41’s archived-sample and image recipes were inspected. Their original values are credited as performed original research. The evaluator verified the source identity, relevant methods and limits.
- Remaining action. For physical transfer, obtain calibrated 5.76–5.8 GHz whole-disc two-Earth-station complex records with measured received power/noise, matched timing, both patterns and polarization, and acquisition coverage adequate for joint delay, Doppler and carrier covariance. Qualify the eventual native renderer separately.

### EME-12 · Supported

Defines compatible physical conditions, a decomposable synthetic combined stress, same-input sensitivity controls, and distinct valid-sample interior absence, invalid capture and terminal silence. Dependence is declared, resume-after-outage is specified, and no prevalence is inferred from fixed controls.

- Original represented evidence. Source observations and transfer limits for physically adverse states, F41:249–283,576–605. Derived and performed weather and attenuation/noise discriminators, F41:576–599 and F84:474–485,649–671. Proposed paired, valid/invalid/final sample conditions and outcomes, F84:436–472. End-to-end outcomes absent, F84:515–518,695–716.
- Consequential obligation provenance. Explicit task requirement for physical severe conditions, outages and preserved calendar, task.md:10–20. Demonstrated reference attainment for matched controls, coupled dependencies and scope of severity inference, comparison/map-eme.md:232–239. A natural probability would require distinct evidence under rules.md:5–10.
- Independent check. desk_check.log:21–23 confirms that a joint endpoint rain sensitivity changes both signal and receiver noise. The model computes roughly 3.108 dB signal loss and 5.943 dB total C/N0 degradation. Historical stream profile uses the declared calendar (src/triad_stream_receiver.cpp:166–177). The outage/completion result remains an implementation test.

## Depth findings

### Depth 1 · Supported

Maps passive scattering, station/lunar geometry, beam and noise, port polarization, local equipment, temporal scale and adverse absence to defined observables. Reports conditions under which self echo, orbital SAR and the simplified native control transfer poorly.

- Original represented evidence. Derived/observed physical mechanism map and proposed station/outage controls, F40:16–50,254–306, F41:130–224 and F84:19–33,436–487.
- Consequential obligation provenance. Explicit ordinary task operating, environmental and receiver envelope, task.md:8–20. Demonstrated reference attainment for mechanism-to-observable mapping, comparison/acceptance.md:25–30 and comparison/map-eme.md:76–172.
- Original locators. F40:16–50,254–306, F41:130–224,548–605, F84:19–33,186–212,436–487.
- Independent check. Sun et al. (2020), §§2–4, and Peters et al. (2026), §II.B, verify the different Earth–Earth and Earth-to-orbit geometries and their local-footprint limits.

### Depth 2 · Supported

The original records actual direct and backward source routes, primary passages, specific products and date/case/access statuses, with useful foundation and 2025–2026 calibration contrasts. The targeted search is bounded. Independent primary inspection supports decisive conventions and exclusions, with evaluator access gaps separately recorded.

- Original represented evidence. Performed source discovery and source observations with explicit accession failures/exclusions, F40:410–526, F41:350–405,607–650 and A40:149–172.
- Consequential obligation provenance. Demonstrated reference attainment for dated discovery and inspected primary evidence with exclusion and failed-access records, comparison/acceptance.md:31–33 and comparison/map-eme.md:210–218.
- Original locators. F40:410–526,530–586, F41:350–405,607–661, A40:149–172.
- Independent check. Reopened LL67 Table II and primary Peters/Chan passages from 2025–2026. Catalogue review confirmed the Zenodo observation/version and June 2026 PDS4 collection. Access results are recorded below.

### Depth 3 · Supported

The original compares viable kernel and implementation choices under common normalization. It tests area/width non-equivalence, alternatives for bistatic visibility and polarization, weather dependence, and reduced versus literal cost and retains real counterexamples and transfer inputs.

- Original represented evidence. Derived and performed estimator/area, kernel, thermal and polarization contrasts, F40:142–174,226–246,439–449, F84:242–328 and F90:355–411. Proposed implementation options and next tests, F84:214–240 and F70:117–159,233–249.
- Consequential obligation provenance. Explicit task requirement for simplest useful choices and reuse, task.md:11–20. Demonstrated reference attainment for viable alternatives, cost, applicability and counterevidence, comparison/acceptance.md:34–36 and comparison/map-eme.md:94–119,183–190.
- Original locators. F40:142–174,226–246,336–400,439–449, F84:214–240,242–328, F90:355–411, F70:117–159,233–249.
- Independent check. reviews/eme/desk_check.log:1–10 independently discriminates the correct area Jacobian and the extra-cosine alternative. Taylor’s and Suckling’s original accounts preserve different estimators.

### Depth 4 · Supported

Supplies reproducible calculations and clearly names power, delay, time scale, width, polarization and noise conventions. Retains sensitivity brackets, source dependence, archive selection, hashes and observed numerical precision separately from calibration and observational uncertainty. Independent arithmetic ties to the declared constants and vectors.

- Original represented evidence. Derived methods and performed results with inputs, limits and observed failure, F41:407–517,548–599,652–661, F84:488–534,537–693 and F90:355–411. Calibrated station inputs absent, F84:695–716.
- Consequential obligation provenance. Demonstrated reference attainment for checkable observables, units, planes, provenance and uncertainty, comparison/acceptance.md:37–39 and comparison/map-eme.md:174–181.
- Original locators. F41:407–517,548–599,652–661, F84:19–33,242–328,488–534,537–693, F90:355–411.
- Independent check. reviews/eme/desk_check.log:1–23 reproduces key delay, covariance, finite-range power/noise and rain calculations using the disclosed constants and coupling.

### Depth 5 · Supported

The original executes useful discrimination against material model and empirical ambiguity, including signed versus positive-only echo search, local CPR reproduction, repeated quadrature, extra-area factor, accepted relative-time geometry and bounded phase/beam checks. Available desk science resolves modeling decisions despite the explicit field-transfer boundary.

- Original represented evidence. Performed raw observation, processed-data and model checks with original comparison/failure details, F41:407–517, F84:488–535,537–693 and F90:355–411. Full renderer/receiver and target-band measurement absent, F84:695–716.
- Consequential obligation provenance. Demonstrated reference attainment for actual bounded independent desk checks, comparison/acceptance.md:40–46 and comparison/map-eme.md:202–230. Field calibration and full modem operation are separate scope, comparison/acceptance.md:45–46 and 95–103.
- Original locators. F41:407–517, F84:488–535,537–693, F86:193–201,239–255, F90:355–411.
- Independent check. Inspected F41:444–479,482–517 and matched the exact public catalogue entries. The independently executed 22-assertion arithmetic check is in reviews/eme/desk_check.log.

### Depth 6 · Supported

The original connects the 75 Hz spacing and geometry/clock/width results to channel selection and a native paired decision with public bounds, tail, valid/invalid and erasure/completion observables. The worked schedule and same-input alternatives make the next discriminator concrete. The integrated plan preserves the difference between research observables and native qualification.

- Original represented evidence. Derived and performed results driving staged adoption, F80:192–216 and F84:488–693. Proposed native matching, projections, comparisons, falsifiers, outcomes and work budgets, F84:186–240,396–487 and F70:42–85,117–159,224–271. Receiver performance and true field transfer remain absent, F84:695–716.
- Consequential obligation provenance. Explicit task requirement for concrete native implementation decisions, observable checks and priorities, task.md:15–20. Demonstrated reference attainment for tracing effects to a next development discriminator, comparison/acceptance.md:47–49 and comparison/map-eme.md:183–209.
- Original locators. F84:186–240,396–487,695–716, F70:42–85,117–159,224–271, F80:192–216,260–269, A40:126–148.
- Independent check. historical-project/src/triad_stream_receiver.cpp:166–177 and historical-project/src/triad_receiver_fine.cpp:2035–2054 confirm the public-config handshake and a distinct work gate by source inspection.

## Source access, execution and availability

- The direct Taylor 2010 PDF timed out. The author text published on DXMaps was inspected for its spectral-width definitions and older-band observations. A failed G3WDG HTML mirror was replaced by the original Suckling PDF.
- LL67 Table II and the report text were inspected. The page-index-8 screenshot returned a cache miss. Several selected values and the surface-area label were available in the PDF text. The NIST Evans 1965 PDF exceeded the web tool size limit.
- The Mini-RF PDS4 observation directory and Peters/Chan primary calibration passages were readable. The exact S4 XML click returned a cache miss and the PDS processing-document fetch timed out. Image bytes and H/V channels were not acquired. The original F41 reports its three-image analysis, exact hashes and limitations.
- Zenodo returned the exact 433.8 MHz record listing, advertised MD5, 626-byte metadata entry and unsynchronized-clock warning. The 96 MB complex data file was not downloaded or independently decoded in this review.
- The Li–Qian–Hu 2026 journal direct open returned HTTP 403. Its publisher search result was retained as a model-paper lead, independent of the decisive recent Peters and Chan primary evidence.
- One initially guessed PMC article identifier resolved to an unrelated paper and was excluded. The correct original Sun et al. article was inspected as PMC7180880.
- No calibrated whole-disc two-station 5.76–5.8 GHz complex record is in the original research. The reported searches and source-conditioned alternatives support conditional research conclusions with that field transfer still open.

- Evaluator did not rerun the original full CSPICE fixture, 96 MB 433.8 MHz I/Q replay or Mini-RF image reanalysis. Inspected reported observables, reproducible methods, published source boundaries and alternate arithmetic.
- No original target-band calibrated whole-disc two-station field verification, calibrated feed/Jones or station weather/noise distribution, native reduced renderer/replay waveform run, end-to-end capture/outage/completion, or demanding-case capacity qualification.

- context/missing-inputs.json lists five exact-version appraisal files. All are context only. The unavailable files are the high-fidelity appraisal README, three HF appraisal documents and the comprehensive receiver-controls report. The original research and supplied source resolve the EME criteria.
- The historical export records exact committed production bytes, with the original dirty/untracked appraisal state and optional root entries excluded. The supplied production files resolve the public profile, preset and receiver-source comparisons.
- No matching target-band field capture appears in the original studies. That is a scientific conditional validation gap adjudicated in EME-11, with no missing input required to assess the authors' performance under the frozen comparison.

- Meter run eme: 48 admitted and returned web items of 50 authorized, across five finished reservations (9 + 10 + 11 + 11 + 7). Six search queries, 24 opens, 15 finds, two clicks and one screenshot. Errors returned as content counted as returned items.
- Zero browser content actions and zero other external acquisitions. No extra allowance, shell network, external private source, product execution, or hardware qualification.
- Exact historical source 13db435fc85114be2e2a0298580d5c3e2bcba996 used for read-only verification. No later source requested.
