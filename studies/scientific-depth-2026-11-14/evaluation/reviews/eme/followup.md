# EME independent follow-up review

## Identity, scope, and preserved disposition

This is an additive review of the first-pass EME package and the participant's
`research/eme/chapter-continuation.md`, `source-ledger-continuation.md`, and
`eme_5760_sensitivity.py/.out`. The initial review and
`dispositions.json` remain unchanged: initial domain status **Partial**, with
EME-01 Supported and EME-02 through EME-12 Partial. Frozen criteria were not
edited. The current pump reference is the same read-only snapshot, HEAD
`13db435fc85114be2e2a0298580d5c3e2bcba996`; no pump source, build, receiver, or
hardware was accessed. The follow-up matrix is in `followup-dispositions.json`.

The review also considered the cross-domain EME evidence in `research/lead/`.
Those desk checks are useful engineering context, not measured lunar-channel
data. In particular, the lead's synthetic retarded-leg geometry and 960
complex-sample/s capture arithmetic must stay distinct from ephemeris results
and actual receiver behavior.

## Independently checked sources and computations

### 7.209 GHz observed versus predicted

I reopened the full primary Sun et al. 2020 article and inspected §§2–3 and
Figs. 1–2. The new continuation reports the categories correctly:

- The 35/90 Hz widths and 167k/185k 10-second SNR values are pre-observation
  calculations at 7.209125 GHz, based on 49 DE436 surface points, 0.07 assumed
  OC albedo, and 503/1,118 km footprints. The article explicitly says these
  widths exclude topography.
- The 60-minute detection is observed. The 10-second plots use 2/5 Hz bins;
  their visually estimated widths are about 40/90 Hz. The paper gives no
  thresholded edge rule or uncertainty for these approximate widths, so the
  continuation is right not to call them FWHM, RMS, or measured quantile
  widths.
- The paper reports integrated SC+OC SNR of 177k/203k, local
  `μC=σSC/σOC=.44/.45`, and OC albedo .06 for the Mare Imbrium footprints.
  These local estimates depend on the observed data and the authors' stated
  spectral integration/noise conventions; .06 is not a global or 5.76 GHz
  calibration.
- Peak deviations of −15/−10 Hz are not width estimates. The roughly 7 Hz
  standard deviation is the Km session's computed-minus-measured residual,
  not a generic microwave receiver search margin.

The participant's model-to-observation comparison is a material improvement
over the frozen first pass. It is appropriately cautious about estimator
ambiguity, correlated data conventions, and band transfer.

### Senior and Siegel source identity and historical delay observation

The corrected attribution is verified. NIST's official Volume 64D index lists
“A theory of radar scattering by the moon,” p. 217, by T. B. A. Senior and
K. M. Siegel. A metered search returned the NIST-hosted original scan's title,
byline, date, and abstract, which describes the quasi-smooth single-scattering-
area theory. Direct opening of that 16,741,766-byte PDF still failed with
`(400) Content length is too large: 16741766`; the DOI resolver was inaccessible
to the browser tool. Thus I independently verify the identity and the
abstract-level theory, but not the continuation's quoted interior delay
passage from an independently opened full scan. Preserve that distinction.

The continuation's geometric comparison itself checks: for a spherical
projected disk, `F(u)=2u−u²` with `u=τ/τmax`; 5 miles is 53.68 μs of two-way
delay, versus 11.591 ms full near-surface-to-limb support, giving 0.924% under
uniform projected-area power. Comparing that with the participant-reported
historical 50% within five miles gives 54.1× (17.33 dB). This is a useful
adverse comparison, but the continuation properly says its source does not
identify the radar frequency and it is not a 5.76 GHz profile.

There is a more directly comparable, source-available desk check still
unperformed: frozen reference F84 reports a normalized LL67 Table II T52
interpolation with the stated MEAN bistatic extension, yielding `t50=.70796
ms`, `t90=5.08696 ms`, `t99=9.02085 ms`, mean `1.70952 ms`, RMS `2.18263 ms`,
and 11.590685 ms support. Its independent Simpson quadrature agrees to the
reported precision. F84 also reports beam/finite-distance surface integration,
delay and power-Doppler quantiles across dish sizes; e.g. its 3 m case gives
`t50/t90=.6148/4.6703 ms` and central 50/90% power Doppler widths
15.218/51.349 Hz. These are model-dependent checks, not lunar truth, and the
source marks the interpolation as a sensitivity rather than a 5.76 GHz
measurement. They nevertheless answer an accessible modeling/decision
question beyond geometric support and the single historical early-energy
comparison. The new delay section therefore remains Partial.

### Conditional 5.760 GHz link, antenna noise, and reference-plane check

I independently recomputed the participant's declared symmetric 3 m/37 W and
5 m/70 W lossless budgets from the stated aperture, range, albedo and
Gaussian-beam assumptions. The received powers reproduce to rounding:
−154.190 and −143.420 dBm. The script's echo-side mean disk gain is applied to
both legs, correctly producing the squared factor in `σeff` under its uniform
albedo and co-pointed symmetric-station assumptions. The antenna-terminal
signal plane, feed-referenced transmit power, off-Moon 100 K receiver baseline,
and illustrative 100 Hz noise bandwidth are declared; this is not a measured
QSO or calibrated station budget.

There is one small, correctable coupling inconsistency. For a centered uniform
lunar disk of angular radius `a` in the stated ideal Gaussian power beam, the
main-beam antenna temperature is

`Tmoon = Tb (Ωmoon/Ωbeam) [(1−exp(−q))/q]`,

where `q=4 ln(2)(a/θHPBW)^2` and the bracket is the disk-average Gaussian gain.
The script uses only `Ωmoon/Ωbeam` for noise temperature while it uses the
Gaussian-average factor for echo illumination/reception. Recomputing with the
script's unrounded beam widths gives couplings 0.111 and 0.278 (not .118 and
.326), or about 23.3 K and 58.5 K at 210 K brightness (not 24.7 K and 68.5 K).
The corresponding ideal C/N values are about 3.50 dB and 13.18 dB in 100 Hz,
about 0.04 dB and 0.27 dB higher than the printed results. This does not
change the qualitative scale, but the source text currently overstates that
the same Gaussian convolution has been applied to lunar noise. Also preserve
the distinction between ITU lunar *brightness* temperature and dish antenna
temperature.

The paper's observed local albedo .06 is explicitly only a sensitivity input
here; ±3 dB values are sensitivity cases rather than uncertainty bounds.
The computed ideal beam/noise check is a viable, useful desk case despite
unknown target hardware. No whole-disc 5.76 GHz calibration follows from it.

### Primary standards and access accounting

ITU-R P.372-15 was not fetched as a PDF because the browser returned
`(400) Content length is too large: 30966212`, but a metered official ITU
search result exposed the body text that lunar brightness above 1 GHz is
approximately 140 K at new Moon to 280 K at full Moon. That supports the
continuation's cited bracket; P.372-17 independently returned the same
statement. The 210 K midpoint is a declared convenience, not a station
measurement.

The fresh web meter run `review-eme` now records 16 operations total (the six
from the initial review plus ten follow-up operations); eight of the 24
allocated operations remain. Follow-up requests included the PMC full text,
NIST source/index, ITU PDF/search, exact-text delay searches, and DOI opening.
Recorded access failures are retained above; no source failure was re-labeled
as a scientific falsification.

## Additive row dispositions

| Criterion | Follow-up disposition | What changed; remaining reason |
|---|---|---|
| EME-01 | **Supported** | Continuation fixes Senior/Siegel attribution and strengthens evidence-status distinctions. The indexed original/official record is sufficient to settle authorship; the prior Partial concern is removed. |
| EME-02 | **Partial** | Conditional target-band extended-target budgets, feed/antenna reference planes, beam factors and signal/noise terms are now present and independently reproduce. The Gaussian lunar-noise integral is not consistent with the stated beam model; correct it. More importantly, the assumed 7.209 GHz local albedo is not a target-band calibration, and the output remains a deliberately simplified lossless symmetric case. Do not demand target hardware to repair the mathematical coupling. |
| EME-03 | **Partial** | Additional measured local OC albedo provides a useful constraint, and the historical delay result counters a uniformly bright-disk default. There is still no quantitative, normalized angular scattering-law comparison (e.g. T52/Hagfors-plus-diffuse vs uniform) showing how aperture, cross-section, polarization and observable change under matched normalization. F84 makes an accessible sensitivity calculation available. |
| EME-04 | **Partial** | Correct projected-area geometry and an adverse historical cumulative-energy comparison are now executed and bounded. F84's source-matched `t50/t90/RMS` and finite-distance/beamsize-conditioned quantiles remain an accessible desk comparison; the historical source's frequency and estimator are not specified. |
| EME-05 | **Partial** | The continuation now cleanly distinguishes predicted 35/90 from approximate observed 40/90 Hz, bins, offsets, estimator limits, and 7 Hz session residual. It still lacks a delay-conditioned Doppler/profile calculation and a target-band spectrum. The lead capture arithmetic does not supply these physical observations. |
| EME-06 | **Partial** | The lead's synthetic comparison shows why retarded two-leg geometry, separated stations and receiver correction order matter; its own ledger labels it an idealized geometry, not ephemeris validation. No cited-epoch actual station/DE436 retarded calculation or bounded error was added. |
| EME-07 | **Supported boundary** | The measured .44/.45 local CPR and .06 albedo, channel convention and footprint transfer limits are now carried through. Unknown 5.76 GHz target-band scatter/feed projection remains an honestly declared empirical boundary. |
| EME-08 | **Partial** | Conditional disk gain and lunar noise calculations across two apertures now quantify aperture-dependent echo and noise. Apply the exact same Gaussian disk weighting to antenna temperature. Speckle/spatial decorrelation and comparison to a defined dish-specific measured noise protocol remain unresolved. Lead synthesis also supplies general noise-plane and correction-order distinctions but not an EME station measurement. |
| EME-09 | **Partial** | First-pass two-end rain sensitivity and operational reports stand. The continuation does not add the source-based gas/cloud/low-elevation cases or measured per-end timing/pointing qualification from the reference; unavailable site data do not prevent conditional desk cases. |
| EME-10 | **Partial** | The continuation improves the simplest physical recommendation (strong central cluster plus optional, bounded weaker tail) and keeps geometry support from power distribution. It still does not compare scalar/replay versus delay–Doppler/facet models by receiver observable, implementation cost and failure mode at comparable depth. |
| EME-11 | **Supported boundary** | Conditional 5.76 GHz arithmetic is independently reproduced; the 7.209 GHz primary spectra and reported measurements are now actually reported and independently reopened; the historical contrary profile is used with explicit limits. The remaining whole-disc 5.76 GHz calibration/IQ gap is genuine and stated. The antenna-noise quadrature correction is small but should be made for numerical accuracy. No hardware trial is required to earn this row. |
| EME-12 | **Partial** | Albedo and Moon-brightness sensitivities plus the first-pass weather and interference cases improve the conditional severity evidence. There remains no matched joint adverse/outage case linking scattering/pointing/polarization/noise/weather/tracking to a named receiver observable and falsifier. Lead synthesis identifies capture-before-decimation and actual measurement needs, but does not execute that joint EME case. |

## Six depth dimensions and material next work

1. **Regimes/observables:** substantially improved. The report now keeps local
   7.209 GHz radar observations separate from conditional 5.760 GHz EME and
   from the amateur operating records.
2. **Discovery/source inspection:** improved with the reopened 2020 primary
   article, current official ITU search result, NIST author check, and explicit
   unsuccessful full-PDF routes. The NIST original's interior delay passage was
   not independently opened in this review.
3. **Alternatives/counterevidence:** improved by the early-return adverse
   historical comparison and explicit warning against uniform full-disk
   channel power. It still lacks quantitative comparison of normalized
   scattering laws and their joint delay/Doppler effects.
4. **Quantitative interpretation:** substantially improved. Width estimator,
   spectral resolution, SNR definition, observed albedo/CPR, link reference
   planes, albedo sensitivities and delay area measure are explicit. Fix the
   small Gaussian temperature-coupling inconsistency above; retain the target
   albedo and calibration as conditional.
5. **Executed discriminators:** improved by independent conditional budget
   reproduction and actual primary-observable extraction. One material
   accessible discriminator remains: reuse/reproduce F84's T52+MEAN weighted
   delay/delay–Doppler quantiles and finite two-beam cases at the declared
   target geometry, with its nonmeasurement boundary retained. This is a
   desk computation and does not depend on target hardware.
6. **Decision relevance:** clearer: a strong center with optional weaker tail
   is more defensible than uniform full-disc power, and a 5.76 GHz receiver
   needs station-specific beam/noise calibration. To turn this into a model
   choice, connect a normalized angular-law sensitivity to the measured
   delay/Doppler observables and one named receiver capture/search decision.

The real remaining scientific gap is not merely the unavailable target-band
hardware/calibration. At least one meaningful cross-check is still feasible
with the already-inspected F84 table/model and supplied receiver envelope:
quantify how T52+MEAN versus a matched uniform/projected-area law changes
weighted `t50/t90/RMS`, received power and central 50/90% Doppler widths across
beam/aperture cases; preserve the measured-vs-historical source provenance and
compare the consequences with the receiver's pre-decimation capture/search
margin. Also correct the Gaussian noise integration. These are the prioritized
remaining items before EME can be considered covered; no target-hardware trial
should be imposed for the desk-evaluable portion.
