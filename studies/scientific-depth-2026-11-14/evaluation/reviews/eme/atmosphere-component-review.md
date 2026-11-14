# Independent check: conditional EME atmosphere component

## Scope and preserved status

Reviewed the stable component files `research/eme-atmosphere/chapter.md`,
`source-ledger.md`, `endpoint_case.py`, and `endpoint_case.out`. Did not inspect
or score the changing `research/eme-integration/` artifact. This component
does not replace or revise the prior/final EME domain disposition: EME remains
**Partial** pending the full integration review.

## Standards, versions, units, and arithmetic

I inspected official ITU-R PDFs and current official status pages:

- **P.838-3** remains in force. The official PDF Eq. (1) defines
  `γR=kR^α` in dB/km for rain rate R in mm/h. Eqs. (4)–(5) define mixed
  polarization, with tilt τ=45° for circular polarization; Table 5 supplies
  the 5.5 and 6 GHz H/V coefficients. The component linearly interpolates
  Table 5 `k` and `α` to 5.760 GHz, applies the circular `τ=45°` expression,
  and gives `k=.00047886`, `α=1.602519`, `γR=.767798 dB/km` at 100 mm/h.
  This is dimensionally and numerically consistent. P.838 does not make the
  chosen 100 mm/h value a climatological or exceedance rate.
- **P.840-9 (08/2023)** remains in force. The official PDF §§2–3.1 states
  `γc=Kl(f,T)ρl`, with `Kl` in `(dB/km)/(g/m³)`, `ρl` in g/m³, and path
  length in km; it gives the double-Debye equations used by the script and
  says the instantaneous rule uses known local/integrated cloud-liquid data.
  Recalculation at 5.760 GHz and 273.15 K gives `Kl=.030916521` in the
  declared units. With `ρl=.20 g/m³` and a 1 km vertical slab, vertical cloud
  attenuation is `.0061833 dB`; the endpoint secant paths produce `.035608
  dB` at 10° and zero in the declared clear case. `0.20 g/m³ × 1 km` is a
  prescribed column of `0.20 kg/m²` (0.20 mm), not a measured cloud product.
- **P.676-13 (08/2022)** remains in force. The official PDF says Annex 2's
  approximate slant-gas methods apply at elevations ≥5° and its instantaneous
  oxygen and water-vapour expressions scale by `1/sin θ`; the standard
  Figure 4 is zenith gas attenuation for a P.835 standard atmosphere. The
  component uses a rounded `0.040 dB` Figure 4 chart read and scales it by
  `1/sin θ`, yielding `.046188 dB` at 60° and `.230351 dB` at 10°. This is
  correctly labeled a coarse sensitivity input, not a site calculation.
  The extracted figure text specifies a 1 GHz plotting grid but does not give
  a tabular 5.760 GHz value. I did not independently digitize the graphic; the
  `.040 dB` chart read therefore remains an author-supplied approximate input.
  No numeric chart-reading error interval is stated. Its round-trip effect is
  `2 δAzenith/sin θ`; at 10° this is 11.52 times the zenith-read error. The
  report should keep that uncertainty explicit; it cannot claim a numeric
  low-elevation error bound from the current inputs.
- **P.618-14 (08/2023)** remains in force. The official PDF §2 gives
  `Ls=(hR−hs)/sin θ` for `θ≥5°` and a curvature-adjusted expression below
  5°. Its rain-height geometry is not directly used here: the example is a
  finite 1 km thick, uniform slab, extended by the same straight slant factor.
  At both 10° and 60°, the chosen ≥5° cosecant geometry applies. No annual
  exceedance prediction is represented as an instantaneous storm.

An independent standard-library calculation reproduces the script's inputs
and output values:

| Endpoint | Slant path | Gas | Cloud | Rain | Total one way | Transmission | Layer emission | Echo after 2 legs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clear, 60° | 1.15470 km | .046188 dB | 0 | 0 | .046188 dB | .9894212 | 2.8896 K | −143.4724 dBm |
| wet slab, 10° | 5.75877 km | .230351 dB | .035608 dB | 4.421573 dB | 4.687532 dB | .3398184 | 180.3286 K | −152.7551 dBm |

The 10° slab needs a horizontal extent `1/tan(10°)=5.6713 km`, consistent
with the report's 5.67 km. Applying the one-way attenuation once to outbound
transmitter power and once to inbound echo signal gives `2×4.687532 dB` in
the wet case; the clear case similarly uses two `0.046188 dB` legs. Wet-minus-
clear path/weather loss is about `9.283 dB` round trip (the prose's 9.29 dB
comes from subtracting displayed powers rounded to hundredths).

The exact command `python3 -I research/eme-atmosphere/endpoint_case.py`, run
from the study root, exited 0 and reproduced `endpoint_case.out` exactly
(1,558 stdout bytes). The script is appropriately labeled as a conditional
case; it is not a site-availability calculation.

## Geometry and signal/noise accounting

The selected elevations are above the horizon, and the slab extents make the
plane-parallel secant construction geometrically feasible. A 1 km vertical
slab at 10° yields 5.759 km ray length and 5.671 km horizontal traverse. The
chapter explicitly uses **apparent** elevation, does not claim refraction
correction or ray bending, and preserves reciprocal co-located TX/RX as a
simple endpoint example. This is internally consistent for the declared
case. A real bistatic pair may have different elevations, path columns,
weather cells and antenna temperatures; both one-way paths must then be
calculated separately. No such site pair is provided.

For a homogeneous isothermal layer at `Tlayer=273.15 K`, the radiative
transfer is correctly written `Tout=η Tin+(1−η)Tlayer`, with
`η=10^(−A/10)`. Thus 180.33 K is the **layer-emission term**, not total
receiver noise or final Moon brightness. It must be added to the attenuated
main-beam sky/Moon input once. Receiver noise and ground spillover bypass
this line-of-sight transform; separate them before transforming instead of
attenuating an aggregate 100 K system-temperature assumption. The chapter
states these distinctions and does not silently add the atmospheric emission
to the −143.38 dBm signal or present a post-weather C/N as if fully known.

The modeled layer emission is consistent in scale with a warm, optically
lossy 10° path: wet transmission .3398 moves incoming beam brightness toward
273.15 K, while the clearer 60° layer emits only 2.89 K. A 5 m dish's
off-atmosphere lunar antenna-temperature increment from the main-beam disk
must itself be attenuated by the layer, while atmospheric emission fills the
main beam. Ground/sky/receiver decomposition and a weathered total C/N are
not calculated because those station components were not supplied. That is
an appropriate limit for this endpoint component, not evidence that the
signal attenuation is only a one-way effect.

## Delay estimate and remaining component limit

The coarse exponential refractivity illustration is dimensionally sound if
refractivity is converted by `N×10⁻⁶`: `315×10⁻⁶ × 7.35 km ≈ 2.315 m`
zenith excess path. Secant scaling gives about 13.33 m / 44.5 ns one way at
10°, and 2.67 m / 8.9 ns at 60°; the reciprocal round-trip increments are
about 89 ns and 18 ns. These are explicitly not operational corrections or
P.676 profile outputs. A site profile is the appropriate next input.

The central remaining numerical-quality limitation is the unquantified
`0.040 dB` chart-read uncertainty. P.676's actual approximate Annex 2 method
accepts pressure, temperature and water-vapour density/content, but the script
has only the global Figure 4 chart read. It should either carry a declared
numeric chart-read bracket into the two-leg sensitivity or replace it with a
computed P.676 reference-atmosphere case; the present text already prevents
mistaking it for site truth. This matters more in the clear comparison than
the 100 mm/h stress, where rain contributes 4.42 dB one way and the gas term
is .23 dB.

## Disposition for this fixed component

The standards methods, units, interpolations, secant geometry, independent
arithmetic, and thermal-transfer bookkeeping are materially sound for the
explicit co-located finite-slab scenarios. The .040 dB gas chart read is a
reasonable **coarse declared sensitivity**, but its error is not numerically
bounded; no exact/site-specific gas result should be inferred. These findings
support the atmosphere component at the method/sensitivity level with that
specific limit. They do not change the preserved overall EME **Partial**
disposition and do not score the still-changing integration chapter.

## Access and budget record

Meter run `review-eme` was at 35/40 web operations after this focused check;
five operations remain reserved for final combined review. The official PDFs
and current ITU status pages were accessed. A screenshot request for P.676
Figure 4 returned no inspectable image through the web interface, so the
chart-read value was not independently digitized. No new request was made to
the pump repository and no pump code was built or run.
