# EME final independent review

## Identity and retained history

This final review compares the frozen EME package, including the final
continuation and joint calculation, against the frozen EME criteria and the
original reference map. The original first-pass disposition remains
**Partial** in `dispositions.json`; the previous additive review remains in
`followup.md` and `followup-dispositions.json`. This document records the
final additive disposition only. No criterion was changed to fit the result.

Pump reference identity remains HEAD
`13db435fc85114be2e2a0298580d5c3e2bcba996`. No pump source, build, runtime,
receiver or hardware test was performed. The lead's synthetic retarded-leg
and capture calculations were considered as cross-domain evidence, but remain
clearly separated from target ephemeris and measured RF observations.

## Final decisive checks

### Primary measured-versus-predicted data

The full primary Sun et al. 2020 PMC article was reopened in the preceding
independent review and §§2–3, Figs. 1–2 were checked. The final continuation
preserves the needed divisions: predicted DE436 footprint spans 35/90 Hz and
pre-observation SNR 167k/185k at assumed OC albedo .07 versus approximate
observed-spectrum widths 40/90 Hz on 2/5 Hz bins, integrated SNR 177k/203k,
local CPR .44/.45, and same-session model-assisted local OC albedo .06. The
paper does not define an estimator or uncertainty for the plotted widths, and
these values remain at 7.209 GHz and in the reported local geometry. The final
text does not promote them into a 5.76 GHz calibration or a universal receiver
search margin.

The correction of the 1960 article's authorship to T. B. A. Senior and
K. M. Siegel is confirmed by NIST's official Volume 64D index and indexed
original-scan record. The direct 16.7 MB NIST-hosted full PDF remained too
large for the browser fetch; the earlier report preserves the NASA NTRS
`Cache miss`, and this review does not claim an independently opened interior
passage. The continuation's explicit frequency/estimator limitation around
the historical “half within five miles” comparison remains appropriate.

### Corrected target-band antenna-plane calculation

I independently recomputed the final 5.760 GHz 3 m/37 W and 5 m/70 W
conditional symmetric link cases. For a centered Gaussian beam, one-way disk
average is `B̄=(1−e^(−q))/q`, while the echo's two-leg weighting is
`B²̄=(1−e^(−2q))/(2q)`. With the listed assumptions I obtain:

| D / Pt | `B̄` | `B²̄` | `Tmoon` at 210 K | `σeff` | `Pr` | C/N in 100 Hz |
|---|---:|---:|---:|---:|---:|---:|
| 3 m / 37 W | .94349 | .89119 | 23.28 K | `5.071×10¹¹ m²` | −154.185 dBm | 3.505 dB |
| 5 m / 70 W | .85321 | .73441 | 58.48 K | `4.179×10¹¹ m²` | −143.382 dBm | 13.217 dB |

These reproduce the final saved output to its displayed precision. The final
script correctly distinguishes `⟨B²⟩` from `⟨B⟩²` for surface-element echo
power and includes the Gaussian factor in antenna temperature. It labels the
uniform .06 albedo as a 7.209 GHz local cross-band sensitivity, uses feed
transmit and receiver-antenna terminal planes, states an assumed 100 K
off-Moon baseline, and does not claim a measured QSO or receiver threshold.
The +0.03/.06/.12 albedo values are sensitivity levels, not confidence
intervals. ITU's official P.372 source supports 140–280 K lunar *brightness*
over lunar phase above 1 GHz; it is correctly converted to a modeled antenna
temperature by the beam integral rather than equated with system temperature.

### Delay and joint delay–Doppler calculations

The final delay model now reports `t50`, `t90`, mean, RMS-about-zero and
centered RMS for two declared surface laws and 3/5 m Gaussian beams. It
distinguishes geometric support from energy quantiles, projected-area annulus
weighting from power-per-delay, and the historical exponential fit from a
measured 5.8 GHz law. It compares an ordinary projected-area diffuse profile
with an explicitly illustrative exponential depth sensitivity fitted to one
historical 50%-within-five-mile point. This meaningfully advances the previous
review. It still is not an angular Hagfors/quasi-specular plus diffuse model,
so it does not settle material/coherence or angular scattering alternatives.

The final joint script retains the same surface record's delay and differential
Doppler, explicitly weights both antennas' Gaussian beams, and compares joint
window energy against the product of separate delay and frequency marginals.
Under the 5 m uniform projected law and source-scaled Km gradient, the 1 ms /
±50 Hz window has `Fjoint=.21217` versus `Fdelay×Fdoppler=.14294` (6.92
percentage points). For the Zv gradient, the same script reports an
approximately 8.6 point difference. The nominal ±112.5 Hz band contains the
whole extrapolated source-gradient support, but has little edge margin for
the stronger extrapolation. A constructed orthogonal-spin kinematic stress
gives about ±234 Hz 1–99% support; the synchronous case nearly cancels it.
Those alternatives expose sensitivity to orientation; neither is an actual
Moon/ephemeris prediction. The 7.209 GHz source gradient derives from predicted
35/90 Hz over the original finite footprints, is linearly scaled to 5.760 GHz,
and is explicitly extrapolated over the disk. Observed 40/90 Hz Fig. 1 widths
are not used as calibrated slopes.

The 1,000- and 2,000-radial-cell outputs show useful convergence for the
exponential case: `t50=.054627/.054230 ms`, `t90=.180458/.179734 ms`, while
first-53.68 μs captured power is `.49956/.49955`. The coarser 160-cell output
is retained but appropriately superseded. This convergence checks the declared
quadrature, not physical validity. One attempted independent command used a
study-root-relative script path while already running from that root and
exited with a `CalledProcessError` before producing assertions. A corrected
launch was started, but its output/session status was not captured by the
wrapper; it is not counted as an independent rerun. The independent antenna
budget computation above and inspection of the retained multi-resolution
outputs are the checks claimed here.

The validation plan now makes the crucial measurement distinction: CW spectra
can test Doppler marginal/centroid and epoch-to-epoch geometry residuals, but
cannot identify joint delay–Doppler occupancy. That requires synchronized
delay-coded/pseudonoise or other approved ranging/multifrequency capture plus
independent station/time/ephemeris references. This is a sound, concrete
falsifier; the absence of such an observation is a real boundary, not a reason
to overstate the conditional surface model.

## Final criterion dispositions

| Criterion | Final disposition | Basis and remaining boundary |
|---|---|---|
| EME-01 Path and observable identity | **Supported** | Separates passive bistatic EME, local radar observation, operating records, target-band sensitivity and measured/modelled variables; fixes Senior/Siegel attribution. No material row gap. |
| EME-02 Extended-target link budget | **Supported boundary** | Complete conditional 5.760 GHz two-leg budget now includes correct two-beam `⟨B_TX B_RX⟩`, antenna-plane power/noise, Moon antenna-temperature coupling and stated limitations. Target-band albedo, station pattern, polarization and loss calibration remain genuinely unavailable and are not inferred. |
| EME-03 Scattering alternatives | **Partial** | Uniform projected-area and fitted exponential-depth profile are compared quantitatively, but neither is a normalized angular specular/quasi-smooth plus diffuse/rough-scatterer model. No polarization/coherence-specific angular cross section is propagated to the decision. F40/F84's LL67/T52 alternatives remain a feasible desk comparison. |
| EME-04 Delay and power-delay profile | **Supported boundary** | Bulk versus excess delay, geometric support, projected-area weighting, two conditional power profiles, beam dependence, moments/quantiles and historical adverse evidence are quantified. The exact 5.76 GHz bistatic PDP remains unmeasured and the historical constraint does not specify a transfer frequency. |
| EME-05 Coupled Doppler and delay | **Supported boundary** | Pointwise geometry, weighted joint-window power, factorized-marginal contrast, source-anchored gradient sensitivity, orientation stress and resolution are present. The 7.2 GHz width observations retain estimator limits. No full-disk 5.76 GHz spectrum or coded delay–Doppler capture exists; the stated CW-vs-ranging falsifier is correct. |
| EME-06 Retarded geometry and station separation | **Supported boundary** | The EME surface computation solves two retarded legs for a constructed near-monostatic geometry; lead comparison separately quantifies retarded, simultaneous-site and geocenter alternatives for constructed separated stations. No actual sites/epoch are specified, so no real ephemeris or visibility result is claimed or required for this conditional case. A future concrete station pair still needs its frame/visibility computation. |
| EME-07 Polarization conventions and alternatives | **Supported boundary** | Primary local `.44/.45` CPR, `.06` OC albedo, channel convention, footprint and cross-band boundaries are explicit. Target-band feed/Jones projection and 5.76 GHz CPR remain unmeasured. |
| EME-08 Pointing, beams, noise and speckle | **Partial** | Correct Gaussian beam area and two-way signal weighting, phase-bracket lunar brightness, antenna temperatures and C/N are now compared over two dish sizes. Measured beam pattern, pointing offsets, spillover/ground/sky terms and spatial speckle/decorrelation are not quantitatively linked to this target-band model. A calibrated station pattern/noise pair is a measurement boundary, but a conditional offset/speckle sensitivity remains feasible at desk. |
| EME-09 Endpoint atmosphere and operations | **Partial** | First-pass two-end rain sensitivity, gas references and operational interference evidence remain bounded; no added gas/cloud/low-elevation/two-leg atmospheric comparison or joint weather/receiver result is present at the reference depth. Site-specific weather records are genuinely absent, but conditional standard-based sensitivities remain feasible. |
| EME-10 Model implementation by fidelity | **Partial** | New output makes receiver-window consequences of simple projected, historical-core and point alternatives more concrete, and the recommendation favors a compact center plus optional bounded tail. It still lacks a decision-relevant comparison of scalar/replay/facet delay–Doppler implementations, cost/state bounds, and exact receiver integration choices. |
| EME-11 Executed observables and numerical checks | **Supported boundary** | Reopened near-band primary observations, independent link reproduction, beam/noise integral, area-fraction calculation, and final two-grid convergence are supplied with provenance. No calibrated 5.76 GHz data or physical qualification exists; it is clearly preserved as an empirical boundary. |
| EME-12 Severity and joint states | **Partial** | The joint delay–Doppler window now includes scattering law, beam weighting, geometry and a receiver capture window; the orientation alternatives are marked constructed. It does not combine material weather, pointing, polarization, noise/tracking and outage into one compatible adverse state or show its named receiver detection consequence. |

## Six research-depth dimensions

1. **Mechanisms, regimes and observables — substantially covered.** The final
   text distinguishes local 7.209 GHz bistatic radar data, amateur 5.760 GHz
   operating records, conditional full-disk echo models, CW Doppler, delay
   ranging, and synthetic geometry. Target transfer limits are visible.
2. **Source discovery and original evidence — substantially covered with
   access limits.** The primary 2020 full text and ITU values were checked;
   NIST official records verify the 1960 title/authors. Direct full-scan
   interior access remains failed in the evaluator record. Modern target-band
   whole-disc calibration and multi-frequency ranging were not located.
3. **Alternatives and counterevidence — improved, still incomplete.** The
   diffuse projected disk, exponential historical-core sensitivity, point
   ray, source-scaled Doppler gradients and two kinematic orientation cases
   have contrary outcomes and explicit limits. The largest scientific
   alternative still missing is a matched normalized angular law (for example
   T52/Hagfors-plus-diffuse) and its field/power interpretation.
4. **Quantitative interpretation — strong for the conditional case.** Inputs,
   units, reference planes, surface measure, beam products, frequency scaling,
   width definitions, RMS definitions, window fractions, and convergence are
   explicit. The measured-spectrum width estimator remains unknown and is not
   concealed.
5. **Executed discriminators — substantial desk work, bounded empirical
   scope.** The antenna-plane budget and disk/noise integrals reproduce;
   1000/2000-cell calculations show quadrature stability. CW/range measurement
   distinction is correct. No joint observational capture, calibrated target
   RCS, or target station ephemeris was executed; none is claimed.
6. **Decision relevance — materially improved.** A broad nominal frequency
   window vs a narrower 50 Hz window yields different retained joint energy;
   simple marginals can misstate a specific delay-gated case. A concrete coded
   echo/multifrequency validation and capture-order check are specified. The
   model choice remains conditional until angular law, station context and
   combined severity are narrowed.

## Remaining material scientific gaps

EME remains **Partial** because three accessible decision branches are still
material, rather than because a target-hardware experiment is unavailable:

1. Quantitatively compare a normalized angular quasi-specular/diffuse law
   (F84's LL67/T52 family is already inventoried) against the projected and
   historical-core sensitivities. Carry surface measure, beam-product
   normalization, delay moments, Doppler-power widths and polarization labels
   through a matched example. The current exponential depth law is a fitted
   one-statistic sensitivity, not an angular lunar scattering model.
2. Add one bounded conditional antenna/environment case for pointing offset
   and receiver sky/ground/spillover or speckle correlation. Existing Gaussian
   main-beam calculations settle the centered disk example but not robustness
   to a practical station pattern.
3. Join one compatible weather/pointing/polarization/noise condition to the
   current delay–Doppler capture statistic and state what receiver observable
   would fail or remain. The recent result establishes delay/frequency
   dependence only; the independent two-end rain result is not coupled into
   that decision.

Do not demand an actual station ephemeris where none is declared, or target
hardware to complete these desk-evaluable gaps. Conversely, do not treat the
synthetic retarded geometry, scaled 7.2 GHz gradient, historical one-point
delay fit or converged quadrature as a field result.
