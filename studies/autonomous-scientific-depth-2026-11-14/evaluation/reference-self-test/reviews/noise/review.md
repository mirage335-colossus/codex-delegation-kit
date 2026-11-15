> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# NOISE scientific adjudication

The original research meets the scoped comparison on all 11 essential rows and six depth dimensions. Three rows retain supported boundaries. The evidence supports decisions about model selection and calibration. It leaves target-site sub-hertz waveform statistics, the target hardware's blocker response, and complete native receiver outcomes open. All judgments are assessable from the locked originals and relevant available sources. The original research earns attainment credit. The historical snapshot and evaluator checks verify or qualify specific claims.

Numbered chapters below refer to Fable-5.2 (historical locator: `../../submission/_ref/highFidelity-triple_Robust_Modem/Fable-5.2/`; artifact not bundled). Astra-6/50 refers to the original noise chapter (historical locator: `../../submission/_ref/highFidelity-triple_Robust_Modem/Astra-6/50-noise-interference-and-frontends.md`; artifact not bundled). The JSON includes exact packet-relative locators. The historical production source is `13db435fc85114be2e2a0298580d5c3e2bcba996`.

## Disagreements and boundary checks

- **Background planning versus survey floors.** The 2019 Dutch methods describe 54 amateur premises and five other locations, with two atypical sites excluded, while its conclusion says 54. Astra-6/50:25 condenses this to 54 sites. Fable/50:194–207 preserves the site categories and campaign-method distinction. Its preliminary and follow-up Dutch items carry common-site provenance, and its German entries need not be independent. The German regulator's Table 4 at 20 MHz gives residential 27.1 versus 36.2 dB, a −9.1 dB difference, with preliminary uncertainty about ±5 dB. The report's city pair is 35.2 versus 40.5 dB. The contrast changes the decision about a shared offset despite unmatched apertures and selection. Fable/50 gives detailed edition and equation/figure locators showing which sections it inspected. Astra-6/50 explicitly used the status page alone. The official reader verifies in-force date and scope independently. [Fockens et al., Methods and Conclusions](https://ris.utwente.nl/ws/portalfiles/portal/88065162/Fockens.pdf), [ITU-R SM.2155, Table 4](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-SM.2155-2009-PDF-E.pdf), [ITU-R P.372-18 edition record](https://www.itu.int/rec/R-REC-P.372-18-202609-I/en).
- **Aperture and impulse-scale corrections.** Fable/50:178, 85:38 and 80:226 call the 1962 figure a measured 0.64 Hz APD. Figure 1 contains the plotted `Ld,Vd` moment pair from a measured distribution at 0.64 Hz. Those observations establish marginal moments at that aperture. The displayed APD families are modeled, and the authors' conclusion on p. 720 emphasizes changing noise during successive bandwidth measurements. The 1985 fit's 6 Hz limit remains a separate boundary. Fable/50:190 gives 0.25 s as a 250 Hz filter response, without a defined filter. The characteristic inverse-bandwidth scale used in 50:24 is 4 ms. Specific impulse tails require the actual filter. C1 specifies its own pulse/filter and neither challenged claim calibrates its arrivals. [Spaulding, Roubique & Crichlow, Fig. 1 and Conclusions](https://nvlpubs.nist.gov/nistpubs/jres/66D/jresv66Dn6p713_A1b.pdf).
- **Censoring and observational identity.** Cyprus interference `Q` counts threshold crossings in 1 kHz samples on a 2 kHz grid, using 100 ms dwells. The companion directional field-floor study averages the lowest 10% across each scan, with 1 s dwells and sequential azimuths and allocations. The studies share a region, some authors and receiver model. Their observables are distinct and neither supplies calibrated modem-aperture joint records. McMurdo numbers are published external-noise figures transcribed by the original author, with partial intervals, overload rejection and antenna uncertainty. The grader accessed the official identity/abstract, and did not directly inspect its figures or Table G-1. The selected Bedford cases likewise remain original report-based statistics rather than new waveform reanalysis. [Cyprus interference, §2](https://www.mdpi.com/2076-3417/12/22/11808), [Cyprus noise, §2](https://www.mdpi.com/2072-4292/14/23/6040), [NTIA TR-25-579 publication record](https://its.ntia.gov/publications/details?pub=4563).
- **A measured event versus a constructed stress.** Fable/50:280 records earlier failure to obtain precipitation static evidence. Its later 50:418 gives Brown & Flagg's 20.1 MHz event, so the locked chapter contains one conditioned observation. The primary p. 3 excerpt confirms the paired readings of 38.76/27.29 dB for the two calibration settings and 60.7/840 kK for the sky-referred means. The 11.47 dB attenuation difference and 11.41 dB temperature ratio agree near 11.5 dB. The printed expression incorrectly adds the baseline to a number already including it. This case supports a separate source/transfer discriminator without providing occurrence weights. The original ENAMS arrays and LMA parsing are completed original checks with explicit processed observables. The grader did not re-download their exact inputs or treat their aggregates as voltage traces. [Brown & Flagg, primary report pp. 2–3](https://radiojove.net/SUG/Pubs/A%20Measurement%20of%20Precipitation%20Static%2C%20Brown%20%28SUG%2C%202018%29.pdf).
- **Equipment threshold and noise units.** Two IC-7300 measurements both show large preamp-state sensitivity. Their close but different thresholds use different radio samples/settings and nominal tuning and cannot settle weak-data recovery after a short pulse. Fable/55:405 gives −178.2 to −176.4 dBm/Hz for 110–264 K. Exact `kT` gives −178.1852 to −174.3831 dBm/Hz, so the upper comparison is about 10.4 dB below the −164 dBm/Hz software default. Fable/84:31 independently uses approximately −179.57 dBm/Hz for its assumed total 80 K. The correction does not change the chosen accounting branch. [Farson, Test 1a/Table 3](https://www.qsl.net/ab4oj/icom/ic7300/7300notes.pdf), [Schnorrenberg, OVF/Table 3](https://www.qsl.net/ab4oj/icom/ic7300/ic7300_dc4ku.pdf), [Sardinia C-band survey, §3](https://www.mdpi.com/1424-8220/24/19/6481).
- **Adverse computational case and actual scope.** The Python desk check reproduced 17.91611535 dB for the chapter's N1 approximation on the pinned exogenous medians and deciles. It obtained 19.45049989 dB for the explicitly independent positive sum on a 256-panel grid, within 0.00036 dB of the more refined reported result. The code-style approximation is below its 18.02621114 dB Galactic component, which a pointwise nonnegative sum cannot do. C0 gave 0.681612 dB and 14.065402 dB of degradation at fixed wanted input in the default and cold synthetic cases. The C4 filter-change gate still fails by construction at relative MSE 0.000228531838154. The original team's successful fixed-filter interpolation check answers a different numerical question. There are no fresh ITU builds, native C3/C4 runs or target qualification in this review. Standalone case inputs and equations (historical locator: `verify_noise.py`; artifact not bundled), Recorded results (historical locator: `verification.txt`; artifact not bundled).

## Row judgments

### NOISE-01 · Supported

The submission separates lightning, cumulative man-made, Galactic, solar, receiver and co-/adjacent-channel terms. It traces low-HF diurnal absorption, environment and antenna selection. The assumed solar-burst flux is a sensitivity input, and the seasonal curves exclude local storms.

- **Original evidence type.** Source observation for background classes, band, time and propagation (50:14–24, 50:410–420). Derived for assumed solar/Jovian flux (50:281–282).
- **Obligation provenance.** Explicit task requirement for noise, interference and actual front-end impacts (task.md:5–10). Demonstrated reference attainment for source-class, directional and temporal distinctions (50:14–24, map-noise.md items 1–2).

### NOISE-02 · Supported

The quantitative background curves carry P.372-18 equation, table or figure locators and their historical bases; older editions supply Vd explicitly. Measured contrasts change the recommendation: Dutch selected signal-clear daytime 500 Hz readings converted under a Gaussian assumption can be above the class curves, whereas the distinct 100 Hz German lowest-20% survey includes below-curve medians. The author's Antarctic 7.647 kHz ENBW site contrast includes natural noise and overload censoring, so it supports a separate external-noise sensitivity rather than a pure MMN correction. ENAMS and the directional studies constrain other, defined observables. The 54 Dutch amateur premises are reused across the main and habitation-correlation papers. Possible German campaign overlap and shared Cyprus instrumentation preclude multiplying independent corroborations. Neither a universal offset nor a causal historical trend is identified.

- **Original evidence type.** Source observation for recommendation edition/content and original surveys (50:32–44, 50:192–234). Performed pinned P.372 outputs and ENAMS dependence (50:116–143, 50:373–404).
- **Obligation provenance.** Demonstrated reference attainment for curves, contrary measurements and estimator discipline (map-noise.md items 3–5, 50:354–367). The 'each quantitative curve' and distinct decision-relevant empirical contrast tests extend the engineering scope under rules.md:7–9. Site-conditioned interpretation serves task.md:10.

### NOISE-03 · Supported

The field and link conventions preserve antenna aperture, available port power, antenna and receiver thermal terms, RF loss, ENBW, real versus complex scaling and the distinct ADC plane. The 6 dB grounded-field versus transmit-directivity discrepancy and the below-component reference approximation are consequential, reproduced controls. The positive-sum alternative is conditional on its stated independent asymmetric dB marginals.

- **Original evidence type.** Derived and performed for antenna/plane and C0 scaling and P.372 versus literal power sum (90:453, 86:305–309, 50:116–145).
- **Obligation provenance.** Demonstrated reference attainment for dependence, combination and calibration math (map-noise.md items 9–10). Explicit task requirement for received levels and artifacts (task.md:10).

### NOISE-04 · Supported boundary

The original compares APD-only, Gaussian/mixture, empirical heavy-tail, clustered filtered pulse and replay approaches by estimator and transfer limits. Performed APD, finite-state and ENAMS checks plus inspected selected pulse-statistic cases establish that equal power or a marginal does not identify event timing, waveform covariance, or duration. Correct the near-sub-Hz figure description and the 250 Hz time-scale sentence. The implementation controls use an explicit pulse and filter and leave target sub-Hz tails, calibrated HF arrivals and long joint statistics conditional.

- **Original evidence type.** Source observation for APD/spacing cases and bandwidth limits (50:147–190). Performed finite-state and ENAMS diagnostics (86:389–398, 50:373–404). Proposed for matched target replay and holdouts (85:68–76).
- **Obligation provenance.** Demonstrated reference attainment for marginal versus joint separation and constructed counterexamples (map-noise.md items 5–9, 86:389–398). Mapping to target bandwidth and receiver integration interprets task.md:10–12 and comparison/acceptance.md:19–24.
- **Remaining scientific action.** Compare matched calibrated continuous records at the intended bandwidths, with excision, clipping and gaps retained, on APD, interarrival survival, marks and envelope covariance.

### NOISE-05 · Supported

The N3 congestion and N4 floor observables remain distinct from interferer power and the denominator of configured modem attempts. The worked sweep-crossing and allocation-threshold examples, structured broadcaster model omissions, nearby coupling/blocking concerns and need for observation-aperture matching support C2 and paired near/far cases. None licenses a 250 Hz packet loss probability.

- **Original evidence type.** Source observation for thresholded occupancy, field-floor and emitter mechanisms (50:244–266). Derived for sweep and slot-aperture comparisons (50:262–266, 50:373–391). Proposed for modem attempt outcomes (86:122–126).
- **Obligation provenance.** Demonstrated reference attainment for congestion, named emission classes and limitations (map-noise.md items 1, 8, 11). Explicit task requirement for interference and outages (task.md:10).

### NOISE-06 · Supported

The proposed representative order runs from antenna and passive network through selection, LNA and susceptible nonlinear stages, mixing, IF/gain and converter to calibrated digital samples. The as-built topology controls actual stage order. C3 deliberately freezes a different constructed chain, finite prehistory and comparative burn-in state, while the native historical model can supply only the simpler post-noise/filter/converter controls.

- **Original evidence type.** Source observation for measured device stages and available modem components (55:40–46, 55:405). Derived and proposed for ordered C3, settled approximation and target state checks (85:213–254).
- **Obligation provenance.** Explicit task/project requirement for actual front-end limitations, continuous receiver and existing native capability (task.md:10–12). Demonstrated reference attainment for physical order and stage-specific calibration (map-noise.md items 10 and 12).

### NOISE-07 · Supported boundary

The independent device reports and executed level convention explain why gain, reference and overload stage change the observable. A linear reciprocal-mixing estimate is confined to the relevant phase-noise offset and blocker regime. Static-carrier tolerance and a brief overload report do not establish post-burst coherent recovery. This supports the choice to place blockers upstream and compare matched steady and pulsed cases, with recovery and close-in noise bounded by actual device records.

- **Original evidence type.** Source observation for conditioned bench thresholds, device differences and scope (55:216–233, 55:461–468). Derived for reciprocal mixing and per-tone/PEP (55:476). Proposed for the matched target pulse and coupled burn-in (85:245–254).
- **Obligation provenance.** Demonstrated reference attainment for device thresholds, gain recovery, observables and reference arithmetic (map-noise.md items 12–13, 16). Actual front-end limitations are explicit under task.md:10. Universal device calibration would extend that scope and is unclaimed.
- **Remaining scientific action.** Measure summed-port input, per-state thresholds, wanted complex gain and overrange through matched blockers and quiet recovery on the target device.

### NOISE-08 · Supported

The research separates LO residuals, phase/fractional-frequency conventions, sample timing, jitter and invalid intervals, band edges/group delay, filtering and ADC behavior. It chooses tone, PPS/timestamps, phase spectrum and calibrated gain/clip checks appropriate to each plane and band. Its C4 failure distinguishes changes to the actual filter from changes to the interpolation method. Manufacturer spot spectra and stability limits are kept separate from target close-in spectra and PLL transfer.

- **Original evidence type.** Source observation for band/device/standards comparisons (55:187, 55:442–459). Performed and derived for C3 ENBW and failed/refined C4 comparisons (86:307, 86:339–362). Proposed for moving-clock handling and actual mask behavior (85:274–286).
- **Obligation provenance.** Demonstrated reference attainment for separates tests of clock, response and converter (map-noise.md items 12–14). Explicit task/project requirement for actual front-end limitations and implementation boundaries (task.md:10–12).

### NOISE-09 · Supported

Sub-9 kHz magnetic/electric sensor axes, lightning and mains evidence are coupled to instrument transfer without importing MF/HF class curves. EME budgets distinguish beam-weighted lunar excess, direction-dependent sky, spillover, feed and receiver contributions; on-Moon total Tsys includes each once. The scenario's correct 80 K conversion and mechanism survive the incorrect 264 K comparative endpoint in 55:405. C-band survey occupancy warrants a local blocker branch and gives no target EME compression threshold.

- **Original evidence type.** Source observation for sub-9 kHz sensors and C-band RFI/radiometry (55:282–285, Astra-6/50:29–36). Derived for beam filling, noise planes and system-temperature conversion (41:531–563, 84:31, 84:475–488).
- **Obligation provenance.** Explicit task requirement for both frequency regimes and actual limitations (task.md:5–10). Demonstrated reference attainment for common accounting with band-specific effects (map-noise.md item 14).

### NOISE-10 · Supported

The original compares standardized background, record-conditioned inputs and constructed controls. It specifies equal-power impulse alternatives, matched linear versus nonlinear blocker treatment, noise/wrong-key false DATA, masked samples, resumed DATA and final physical quiet. Completed arithmetic and filter discriminators earn credit. Full receiver ablations are an implementation plan and contain no measured false-DATA, completion or natural-occurrence rates.

- **Original evidence type.** Performed and derived for equal-energy, power-plane and filter discriminators (86:301–311, 86:339–362). Proposed for paired complete receiver, noise-only and physical completion outcomes (86:128–145).
- **Obligation provenance.** Demonstrated reference attainment for conditional synthetic versus calibrated scenarios (map-noise.md item 15). Public hypotheses, calendar and continuous native receiver explicitly required (task.md:12). The specific false-DATA/quiet controls implement those requirements (85:307–309).

### NOISE-11 · Supported boundary

The original actually analyzed two-site 24-hour ENAMS floor observables and a selected LMA quality product, transcribed explicitly scoped NTIA published statistics, and computed noise and filter/transfer contrasts. The 20.1 MHz precipitation event provides a second primary-statistic discriminator: the attenuator and calibrated temperatures agree on approximately 11.5 dB even though the printed ratio adds the baseline twice. These discriminate baseline/combination and physical filter or estimator changes while giving no calibrated target waveform or receiver result. The matched-observable protocol specifies separate site, device, physical-holdout and native modem dependencies.

- **Original evidence type.** Performed for ENAMS and LMA product checks and noise/filter comparisons (50:373–424, 86:339–362). Source observation and derived for NTIA statistics and one precipitation event (50:222–234, 50:418). Proposed for target physical practice and modem checks (85:68–78, 85:305–318).
- **Obligation provenance.** Demonstrated reference attainment for primary-statistic interpretation and scoped calculations (map-noise.md item 16). Executed discrimination, evidence-level precision and distinct holds are explicit frozen rubric obligations (rules.md:11–13). The actual device and implementation linkage serves task.md:10–12. Joint target qualification goes beyond the completed original comparisons.
- **Remaining scientific action.** Acquire matched calibrated site/antenna voltage and exogenous state, target device gain/phase/blocker/AGC logs, and independent physical episode/site/device holdouts. Verify native C0–C4 and paired receiver outcomes separately when in scope.

## Depth dimensions

### 1 · Supported

Source mechanisms, spectral and time windows, direction, instrument floor and overload, and propagation-dependent absences are mapped to distinct scopes. Solar events and device behavior retain explicit calibration limits.

- **Original evidence type.** Source observation and derived for mechanism and finite-band sensitivities (50:12–26, 50:276–283, 55:14–58).
- **Obligation provenance.** Explicit task environment and observables (task.md:5–10). Demonstrated reference attainment for source/domain separation (map-noise.md items 1–2, 10–14; comparison/acceptance.md:19).

### 2 · Supported

Original search terms, exact DOI/title follow-ups, foundational methods and recent distinct studies are recorded with access grades and excluded evidence. Separate extracts, documents and full figures carry distinct evidential weight. The NBS figure overstatement and study counts were independently corrected or bounded. No unique unread thesis content is required for the selected comparison.

- **Original evidence type.** Performed explicit literature retrieval and source observation for relevant sections/tables (50:345–351, 50:426–454, 55:425–427). Unavailable original source details noted for unused alternatives (55:436).
- **Obligation provenance.** Demonstrated reference attainment for traceable literature discovery (50:345–351, 55:425–427). Explicit frozen depth requirement for queries, source passages, date/exclusion/access trail (comparison/acceptance.md:20).

### 3 · Supported

A simple planning level versus physical sum, memoryless APD versus measured/constructed event timing, statistical occupancy versus explicit co-channel signals, and passive/noise versus ordered nonlinear equipment are genuine alternatives. Author examples preserve contrary trials and observability/cost before tying each choice to its simplest useful branch.

- **Original evidence type.** Source observation and performed for retained polarity of alternatives and empirical evidence (50:133–145, 50:410–414). Proposed for integrated native routes (70:129–131, 70:160–181).
- **Obligation provenance.** Explicit task requirement to choose simplest useful representations, reuse capability and distinguish artifacts (task.md:10–12). Demonstrated reference comparison of alternatives (comparison/acceptance.md:21, map-noise.md items 7, 9, 11–13).

### 4 · Supported

The original supplies explicit input values, units, estimator/aperture, assumptions, numerical uncertainty and quantitative alternatives. Inspectors can reconstruct the large distinctions without assuming universal calibration. The independent corrections are localized to a reported observational scope and two numerical sentences, with valid alternative conventions and target tests in the original work.

- **Original evidence type.** Performed and derived for pinned and independent calculations (50:116–143, 86:301–311, 86:339–362); source observation for reported measurement definitions and uncertainty (50:222–234).
- **Obligation provenance.** Demonstrated reference attainment for checkable values/conventions and estimates (map-noise.md items 5, 9–10, 16; comparison/acceptance.md:22). Noise and measured/model artifact distinction explicit (task.md:10).

### 5 · Supported

The original performed independent N1 comparison including a failed convergence grid, analyzed primary processed site and event products, and executed adverse/full-transfer C4 and fixed-filter interpolation comparisons. The useful desk work settles which interpretation can enter a model, while matched recordings and native receiver execution remain outside these verified outputs.

- **Original evidence type.** Performed on defined inputs with results and failures (50:116–145, 50:373–424, 86:339–398). Proposed for actual C3 nonlinear convergence and production trials (85:245–254, 86:422–433).
- **Obligation provenance.** Demonstrated reference attainment for executed, decision-changing desk tests (comparison/acceptance.md:23; map-noise.md item 16). Implementation/hardware limits follow task.md:10–12 and comparison/acceptance.md:36, 44.

### 6 · Supported

The original synthesis stages scalar, standardized, and independently measured observables before receiver outcomes. It links results to the ambient model branch, ADC/front-end intervention, native state and observation calendar, paired outcomes and residual measurements, retaining what would falsify a claimed physical transfer.

- **Original evidence type.** Proposed for staged native changes, target recordings and physical holdouts (85:68–78, 85:305–318). Performed results supporting branch decisions, with original failed filter gate retained (80:218–243).
- **Obligation provenance.** Explicit task requirement for concrete implementation boundaries, observable checks and priority order (task.md:12). Demonstrated reference attainment for conditional decisions and concrete discriminators (comparison/acceptance.md:24; map-noise.md items 15–16).

## Access and execution

- P.372-18 and -17 full PDF opens failed content length, and the -18 ToC returned 404. Verified official -18 status and scope, and original author's detailed versioned locators. Pinned reference-source GitHub tag page was readable but the tool did not expose usable source code in the inspected view; the raw URL was rejected as octet-stream. Independently reran the published formula at matched inputs without claiming a fresh code build.
- NTIA TR-25-579 full PDF and the NTIA 93-293 scan were unavailable through this web reader. TR-25-579's official record/date was verified. The original author's auditable page/table descriptions were assessed with accessible primary equivalents. Exact ENAMS HTML was unavailable through this reader; no raw plot decode or hash reproduction was claimed.
- Direct Brown & Flagg 2018 URL returned a cache miss; exact primary p. 3 text was available via an indexed result and assessed as excerpt evidence. A C-BASS publisher-route attempt was unavailable. None of these optional verifier limits holds any assessment.

- No independent grader rerun of the pinned ITU C library, reconstruction of the APD port, live ENAMS Bokeh arrays, raw NTIA waveforms or target-installation measurements.
- No native C0–C4 rendering, nonlinear C3 coupled burn-in, acquisition/false-DATA/physical completion trials, formal standard-conformance testing, product build or intended-hardware capacity qualification.

- 48 metered web items in 12 returned batches of four for run noise, including unsuccessful item-level accesses. 0 browser content actions and 0 other acquisitions. Cooperative receipts do not certify activity beyond the wrapped calls.
- One unintended and unrelated Michigan State URL lookup was included in a metered batch; access failed and it supplied no evidence. No additional allowance was requested or used.

The numeric reviewer rerun used `/usr/bin/python3 -B verify_noise.py`, with exit 0. Prior to running, I inspected the standalone script and the supported Python entry point. The exact five missing appraisal files are context-only and unnecessary for these scientific dispositions. The site, device, physical and native modem gates in NOISE-11 are scientific/qualification prerequisites for later claims, not adjudication input holds.
