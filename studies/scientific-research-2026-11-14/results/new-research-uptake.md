# New research uptake: pumpModem source audit

## Scope and evidence identity

This is a prospective source audit of report `m74.md`, not an independent
literature verification, benchmark, or runtime check. The report itself states
that its research session did not inspect implementation or run the simulator.
Its claims below are therefore conditional evidence for deciding what to check
in code and channel experiments, not newly verified primary-source truth.

- Kit checkout: `/home/user/___quick/p/_cur/codex-delegation-kit`, HEAD
  `08fc5207af39b9dd728d83ffeaadd4d1b4815653`; dirty at start. `policy.md`
  was modified (SHA-256 `94eec8cb162fe44d01fe251093d23da72e85dd72aed0f9d5bed089f366ac1b37`);
  report SHA-256
  `1cba220d0823118fec02795660160a57fd97b2f2c395354950bd1c0c418af3d2`.
- Source checkout: `/home/user/___quick/p/_cur/dataPump/pumpModem`, HEAD
  `13db435fc85114be2e2a0298580d5c3e2bcba996`. It had unrelated dirty files
  under `_appraisal/highFidelity-triple_Robust_Modem`; they were not read or
  changed. Audited-file SHA-256: `AGENTS.md`
  `e567818daad429c024c60b0191fc0f8f98b181183d97df2f2de9d63a102fb309`,
  `docs/channel-models.md`
  `cf3a7c5f63ace28931866f08db5a0efb28a93e4b6607755023a9009932f64acd`,
  `include/datapump/triad_modem_v3.hpp`
  `0a2ae5cdffb5901d8ee3ce355dffd5333d8ee60a96365b961f39370d37155cef`,
  `src/triad_simulation_stream.cpp`
  `211b8b5e2396c9f1b7a39c33858ea8cfa9a1c74d5d8aa9377641533532146bf1`.

## Current-code mapping and bounded decisions

| Report finding and disposition | Source evidence / remaining condition | Next bounded check and observable discriminator |
|---|---|---|
| **Reuse** the native streaming propagation path for controlled reference channels. | `StreamingChannel` accepts a composed `EmittedSource`; `read()` advances a stateful channel over the complete composite. `triad_simulation_stream.cpp:815-935` applies delayed sampling, per-path phase/gain, summation, common wander, outage and selective response before receiver noise/frontend. The public channel config/report is in `triad_modem_v3.hpp:179-350`. This matches the report's requirement to propagate the composite before separating DATA/Helper. | With one fixed seed and a small impulse/composite input, compare current two-ray settings against a channel-free baseline; inspect the impulse response and report diagnostics. Require delay, phase and stream-chunk continuity to match configured values; this is not yet observed. |
| **Adapt/test** a stationary Gaussian-scatter reference while preserving differential Doppler centers as a separate axis. | `PathEvolutionConfig` already exposes `gaussian_doppler_width_hz` (documented as `B=2σ`, independent of `SpreadRay` center separation), fixed-time `random_doppler_width_hz`, OU `ray_coherence_seconds`, and common `common_doppler_wander_hz` (`triad_modem_v3.hpp:179-238`). Source setup creates the Gaussian path and common-wander processes (`triad_simulation_stream.cpp:617-721`); validation makes the three stochastic gain laws mutually exclusive, but does not state that Gaussian spread and `SpreadRay` centers cannot coexist (`:84-109`). Thus several ingredients appear reusable, but a full F.1487 reference and its convention have not been runtime-verified. | In a bounded calibration, run clean, common-shift-only, fixed two-ray differential-center-only, then single-tap Gaussian-width-only and combined Gaussian-width plus center cases. Measure per-ray PSD width and gain autocorrelation, centroid separation, and common offset independently. At `B=30 Hz`, check the stated `2σ` convention and expected half-correlation lag (~12.5 ms); do not label a 30 Hz center separation as 30 Hz spread. |
| **Reject** equating the GUI's 7 ms/30 Hz `HF Worst` label with a complete environmental reference or 30 Hz diffuse width. | `docs/channel-models.md` says `HF Worst` represents 7 ms excess-delay support and 30 Hz differential-Doppler support; its echo power and instantaneous frequency vary, while direct remains present. It explicitly calls the model non-calibrated and identifies the two-path family gaps. The report also says equal numeric 7 ms/30 Hz labels do not prove matching delays, powers, spectra or metric definitions. | Hold total power and realization seeds fixed; compare fixed 7 ms/30 Hz differential-center case with 7 ms plus 30 Hz-per-ray Gaussian spread. Inspect separate center/width/autocorrelation metrics and receiver acquisition. A material difference in these observables establishes that the labels are not interchangeable. |
| **Adapt/test** cross-carrier and DATA/Helper response as one channel realization; do not infer independent carrier fading or transfer Helper estimates directly. | The simulator receives one composite waveform and has delay-dependent phase; docs state it does not identify carrier streams. Report's correlation formula is derived only for independent stationary taps and requires actual carrier spacing, powers and phases. The current report has neither those waveform parameters nor measured covariance. `SelectiveModelConfig::correlation_spacing_hz` is explicitly a synthetic dispersive stress, not a physical multipath replacement (`triad_modem_v3.hpp:225-240`). | Using actual DATA/Helper offsets and a shared seed, sweep relative path phase/delay and power; record complex gain per carrier plus Helper-conditioned DATA fades. Compare measured covariance to the independent-tap prediction. Do not use synthetic selective perturbation as evidence of physically calibrated frequency correlation. |
| **Defer / unresolved** arbitrary mode transitions, diffuse clusters and direct-path disappearance. | Current explicit evolution offers two-path bounded echo variation (which keeps direct present), OU or Gaussian per-ray gain, moving delay and a single whole-signal outage (`triad_modem_v3.hpp:179-238`; `docs/channel-models.md`, “Robust GUI changing-channel realization”). These do not represent arbitrary multi-tap delay–Doppler ridges or path-specific mode availability/transitions. The literature report makes such scenarios conditional on route/regime and acknowledges that rates/joint tails are not established. | First compare stationary two-ray and one explicitly parameterized mode-replacement case, matched in power and receiver configuration. Track acquisition, false locks, packet delivery including outages, longest loss run and reacquisition. Add a richer model only if ranking or a required receiver decision changes; source evidence alone does not justify a universal preset. |
| **Reuse with qualification limits** current stream noise, impairment and report plumbing; **defer** field calibration and environmental weighting. | The source separates receiver noise from path processing and supports oscillator/front-end effects and reports. `docs/channel-models.md` explicitly says these are synthetic assumptions, not named-path measurements. The report's claimed ITU values are conditional reference settings; marginal exceedances do not establish joint outage probability. It says no target route, composite channel, DATA/Helper spacing, tracking budget or receiver parameters were supplied. | Before any environmentally weighted choice, provide target geometry, waveform offsets/bandwidth, receiver timing/tracking and calibrated simultaneous channel response. Compare predicted delay/Doppler/cross-band statistics to that capture with definitions and resolution stated. Until then retain explicit scenarios and do not claim operational coverage. |

## Read log and limits

Read only the assigned kit inputs: `studies/scientific-research-2026-11-14/results/m74.md`
and the relevant policy section “Scientific literature research and development
uptake.” In pumpModem read only `AGENTS.md`, `docs/channel-models.md`,
`include/datapump/triad_modem_v3.hpp`, and `src/triad_simulation_stream.cpp`.
Searches were confined to those assigned source files. No tests, curated
`_ref/`/`_appraisal/`, other study artifacts, dependent implementation files,
builds, tests, network sources or runtime logs were consulted. Eight shell
invocations were used for identity, reading and output-path verification. No
assertions or runtime checks were run.

Still unverified: source-level predictions about exact generated PSD, tap
independence, fractional-delay accuracy and cross-carrier response; actual
waveform DATA/Helper spacing and bandwidth; receiver behavior under any proposed
scenario; scientific claims beyond what `m74.md` reports; and modern joint
delay–Doppler–SNR distributions. Any follow-up should use the bounded checks
above with matched seeds, power and receiver configuration, then record actual
commands and observations separately from these recommendations.
