# HF channel model evidence for a17

**Question.** When does stationary Watterson or common delay/Doppler with independent per-carrier gains stop being adequate for changing HF, and what inexpensive correlated/nonstationary alternatives are supported?

## Findings

1. **Stationarity is an explicit model boundary.** ITU-R F.1487 describes a *stationary Gaussian scatter* HF channel, with one adjustable delay tap per propagation mode/path and a time-varying complex gain at each tap; the recommendation calls it valid for 3 kHz and potentially applicable up to about 12 kHz. See [ITU-R F.1487, §1 and §2, Figure 2](https://www.itu.int/dms_pubrec/itu-r/rec/f/R-REC-F.1487-0-200005-I%21%21PDF-E.pdf). NTIA's retrospective gives the practical restrictions: stable/time- and frequency-stationary channel, negligible delay dispersion, low-ray path, and ≤12 kHz; it quotes the then-current CCIR caveat that zero time-spread discrete paths become less accurate as bandwidth increases. See [NTIA Report 90-255, §1, lines/printed pages 4–5](https://its.ntia.gov/umbraco/surface/download/publication?reportNumber=90-255_ocr.pdf). **Implication:** a single stationary parameter set should not be used across intervals in which modal powers, delays, or Doppler statistics drift materially; neither is it a sound wideband model once dispersion or diffuse delay spread matters.

2. **HF conditions can exceed the narrowband midlatitude envelope sharply.** Measurements over northerly paths report delay spreads and Doppler shifts/spreads significantly beyond midlatitude values, attributed to large-scale ionospheric motion and turbulent plasma irregularities common in auroral/polar-cap regions. See [Warrington, Stocker & Siddle (2006), §1, ¶¶2–4](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005RS003294). Separately, measured mildly disturbed high-latitude 1 MHz channels had reported 90th-percentile RMS (2σ) Doppler spread 13 Hz and delay spread 400 μs; largest values were 16.8 Hz and 780 μs. See [Watterson et al. (2003), “Measured channel parameters for the disturbed wide-bandwidth HF channel,” §5 summary](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2002RS002746). These observations establish that stationary narrowband tap statistics cannot stand in for every disturbed or wideband case; they do not establish thresholds for this receiver or path.

3. **Independent gains at distinct carriers are not a universal physical assumption.** The two-frequency HF correlation study explicitly models/measures the correlation as a function of frequency separation and relates its coherence bandwidth to ray separation near the ionospheric reflection point. See [Fridman et al., “Two-frequency correlation function of the single-path HF channel,” abstract](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/94RS02413); evidence retrieved here is abstract-level, so no numerical threshold or detailed fit is claimed. **Implication:** retain a carrier-correlation parameter (including zero as an option), or drive each carrier from shared latent path/mode variables plus carrier-specific residuals. Do not presume all gains independent or perfectly shared. The appropriate correlation must be measured or swept for the actual frequency spacing and path.

4. **Inexpensive useful upgrade: piecewise/quasi-stationary tap model.** This is a design inference, not a published validated HF standard: keep the Watterson-like tapped-delay structure and its inexpensive Gaussian Doppler gain generation within short blocks, while slowly updating per-mode power, delay, Doppler shift/spread and a measured or parameterized SNR envelope between blocks. Use shared slowly varying mode state across carriers and allow configurable carrier residual correlation. A block should be shortened when observed statistics drift within it. ITU's own description identifies the mode taps and the parameters to set; NTIA describes a deterministic Ionospheric Parameters Model whose time-varying quantities map to physical ionosphere parameters, giving a higher-fidelity next step when frequency-dependent delay/dispersion is material. See [NTIA TR-88-240, §§1.1–1.2 and §2](https://its.ntia.gov/publications/download/TR-88-240.pdf). For wideband/diffuse scattering, NTIA says both dispersion and scattering require representation; a simple delay-varying response alone does not capture diffuse scattering ([NTIA 90-255, §1.2]).

5. **Expensive model is not automatically better-grounded.** Gherm et al.'s 3-D inhomogeneous, time-varying ionosphere simulator generates frequency/time realizations and scattering functions, but its complex-phase/Rytov approximation is limited to not-large log-amplitude variance and authors cite strong scintillation as outside its treatment. See [Gherm et al. (2005), abstract and §§1–2, especially §2.2](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004RS003093). Use this as a possible research model, not a gold oracle for strong scintillation.

## Applicability and counterevidence

- This literature supports *when to promote the model* (nonstationary statistics, high-latitude/disturbed conditions, wide bandwidth/delay dispersion) and a simple experimental extension. It does not identify the actual HF carrier spacing, propagation geometry, ionospheric state, receiver bandwidth, or session duration for the intended run. Those facts determine whether common path state or independent carrier residuals fit.
- ITU F.1487 remains the appropriate low-cost stationary baseline for narrowband modem tests, not a defective model within its intended regime. Its standard parameter sets explicitly include low-, mid-, and high-latitude conditions; high-latitude use alone does not prove the channel is nonstationary in every short interval.
- Multiple modes and magneto-ionic components have distinct shifts/spreads, and their parameters vary by geography, season, and time (ITU F.1487 §1). Thus “one shared Doppler per all carriers” is an additional simplification beyond using shared delay/mode structure.
- The 2006 northerly-path article notes physical models were not yet incorporated into common hardware simulators and that its cited model was not applicable to strong high-latitude scintillation (§1 ¶4). The 2005 Gherm model's approximation limit independently cautions against claiming it resolves that case.

## Model/test choice changed

For the appraisal, keep three carriers as separate observed channels, but add a low-cost controlled comparison: (a) stationary per-carrier Watterson-like gains; (b) shared slowly varying mode state with tunable inter-carrier gain correlation and blockwise parameter updates; and (c) only if bandwidth/delay evidence requires it, a frequency-dependent-delay/dispersion model. Log the measured per-carrier coherence/correlation and within-block drift. Do not infer common gain or independence from equal endpoint outcomes. This is a proposed experiment, not observed performance evidence.

## Search operation log (12 web items; no shell use)

1–3. Search: ITU/NTIA Watterson limitations; nonstationary HF measurements; HF channel measurements.
4. Open ITU-R F.1487 PDF.
5. Open NTIA Report 90-255.
6. Open Warrington et al. 2006 northerly-path measurements.
7. Open Gherm et al. 2005 physical simulator.
8–10. Search: Furman intermediate-duration model; HF interfrequency correlation; simple nonstationary Watterson alternatives.
11. Open NTIA TR-88-240 deterministic model.
12. Open Gunashekar et al. 2010 HF-MIMO measurement study.

No failed web operations. Stopped at the 12-item limit. No source code, pumpModem, withheld `_ref`/`_appraisal`, study results, evaluations, or current kit policy was inspected.
