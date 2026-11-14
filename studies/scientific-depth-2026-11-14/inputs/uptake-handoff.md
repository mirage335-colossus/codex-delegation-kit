# Shared research handoff

Start with [the synthesis](../research/lead/synthesis.md) and [paired receiver cost design](../research/lead/receiver-cost.md). They point into the detailed research and calculations. Historical first-pass versions remain available for provenance; the current chapters and explicit continuations carry the corrected conclusions.

| Question | Current detailed material |
|---|---|
| Sub-9 kHz launch, bandwidth and propagation | [Antenna chapter](../research/vlf-antennas/chapter.md), [propagation chapter](../research/vlf-propagation/chapter.md) |
| Approximately 1 and 30 MHz groundwave | [Groundwave chapter](../research/groundwave/chapter.md), its budget and numerical-reference checks |
| HF regimes and planning/measurement references | [Regimes chapter](../research/hf-regimes/chapter.md), [reference chapter](../research/hf-reference/chapter.md) |
| Passive near-5.8 GHz EME | [Initial chapter](../research/eme/chapter.md), [corrected continuation](../research/eme/chapter-continuation.md), [angular/pointing/receiver integration](../research/eme-integration/chapter.md), [endpoint atmosphere](../research/eme-atmosphere/chapter.md), and their executed checks |
| Noise, interference and front end | [Initial chapter](../research/noise/chapter.md), [continuation](../research/noise/chapter-continuation.md), [second continuation](../research/noise/chapter-continuation2.md) |
| Receiver alternatives | [Receiver chapter](../research/receiver/chapter.md), executed discriminators |
| Validation and native capacity | [Validation chapter](../research/validation/chapter.md), [follow-up](../research/validation/followup.md), [native chapter](../research/native/chapter.md) |

Each branch's source ledger records access, source identity, conventions and limitations. Research calculations and public numerical-product analyses are distinct from product or field qualification. The separately supplied observations are deterministic constructed diagnostics with documented inputs, not actual field captures.

For the corrected empirical and quantitative details, the HF branch includes [the original selected midlatitude measurement tables and conditions](../research/hf-regimes/watterson-browser-primary.md) and [their reconstruction](../research/hf-regimes/watterson_reconstruction.txt), alongside its planning, NVIS, polar, disturbed and TEP evidence. The EME branch includes [the current joint delay/Doppler calculation](../research/eme/eme_joint_delay_doppler.py) and [convergence-checked output](../research/eme/eme_joint_delay_doppler.out); its continuation distinguishes measured spectra, predicted footprint gradients, fitted delay profiles and conditional integration choices. Consult the current text for transfer limits before adopting those numbers.
