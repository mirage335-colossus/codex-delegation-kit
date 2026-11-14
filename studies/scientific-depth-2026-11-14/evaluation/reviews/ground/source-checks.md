# Groundwave review source and calculation checks

## Identity and limits

- Review run: `review-ground`; metered use 8 of 20 operations. Receipts are in `../../receipts/` and `meter.json` records the 8 use.
- Report checked: live `research/groundwave/chapter.md` (143 lines). First-pass/live chapter and source-ledger hashes match (`ea5ff482…bccf925`, `19a9a3e1…db9f7`). Only the phrase “three independent source-backed checks”/“four…” differs at chapter line 136. No substantive research change was present.
- Independent source/calculation allowance: 20 bounded calls; work remained within that allowance. No source or production edits and no pump execution.

## Primary / official evidence inspected

1. **ITU-R P.368-10** official recommendation, direct search result from the assigned metered run, with scope and reference excerpts. It is in force (2022), covers 10 kHz–30 MHz, and limits the method to smooth homogeneous spherical Earth, short near-surface vertical monopole reference, negligible ionospheric reflection and a receiver not well above the surface. This supports the candidate's conditions and excludes a terrain/complex-channel reading. Recommendation: [P.368-10 official PDF](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.368-10-202208-I%21%21PDF-E.pdf).
2. **NTIA TR-84-151**, complete official 152-page PDF opened, with relevant sections/tables reopened. Tables 2–3 (around pp. 69–70 in extracted pagination) substantiate the 28-MHz path median examples (East/East-snow/South/Mountain at 5 km: 100/100/103/120 dB; at 20 km: 131/129/138/140 dB where present) and 3–13 dB decile spans. Text around pp.67–68 states typical ~20-dB path-median spread; §§8–9 show up to 15-dB smooth-vs-WAGNER difference and up to 25-dB WAGNER residual against selected 28-MHz observations, with attribution caveats. Candidate's bounded interpretation is supported. [Official NTIA PDF](https://www.its.ntia.gov/publications/download/84-151_ocr.pdf).
3. **Aono & Muramatsu (1955)**, original NICT article PDF, entire 8-page article inspected. It reports 1.85, 2.5, 4-MHz mixed land/sea field measurements. Its discussion explicitly credits Millington over older one-way methods but notes overprediction in some measured sections where Furutsu fit well; another route's sea-to-land change remains poorly explained. This validates the report's conditional disagreement but shows why an executed same-input comparison is still useful. [Original NICT article PDF](https://www.nict.go.jp/publication/journal/02/007/Journal_Vol02_No007_pp051-058.pdf).
4. **ITU-R P.832-4**, official metered search returned Annex 1 §§3.2–3.4: MF maps are “standardized to 1 MHz”; they contain no seasonal allowance and have country-dependent inputs, including provisional areas. This falsifies chapter line 59's direction-of-frequency caveat, while retaining a sound need to check local/site representativeness. [Official P.832-4 PDF](https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.832-4-201507-I%21%21PDF-E.pdf).
5. **ITU-R P.527-6** direct official PDF open was metered and returned an internal error/timeout (receipt `726074ee7c734af1ae6f076c8075cb8d.json`; only 307 serialized characters). This is a failed access check, not evidence that the recommendation is unavailable or that the candidate's P.527 summary is wrong. P.832 search also surfaced the official P.527-6 summary explaining current complex-permittivity scope and retained below-30-MHz σ/ε attachment, but I did not use that as independent full-text verification.

Metered web receipts: `de15f492…` P.368 official search; `a8585877…` NTIA PDF open; `ec99f3a6…` NTIA section opens (2 operations); `9cea3a3b…` NICT original open; `726074ee…` failed P.527 open; `c831e631…` P.832 official search; final P.832 follow-up search receipt is in `meter.json`/`receipts/` (`review-ground`, 1 operation). Total 8 operations, including the failed source open.

## Independent arithmetic

Recomputed from the P.368 reference equation, `Lb = 142 + 20 log10(f_MHz) - E_dBµV/m`, with `300 mV/m = 109.5424 dBµV/m` at 1 km:

| Frequency | Basic loss | 1-km free-space loss | Difference |
|---:|---:|---:|---:|
| 1 MHz | 32.4576 dB | 32.4500 dB | 0.0076 dB |
| 30 MHz | 62.0000 dB | 61.9924 dB | 0.0076 dB |

Other checks in `groundwave_checks.py/.txt` were independently reviewed/recomputed: 20 dB power loss gives complex amplitude ×0.1 and power ×0.01; `σ/(2πε₀ f εr)` ratios agree with the stated representative values; k=4/3 horizons (2m/2m: 11.653 km; 10m/2m: 18.855 km); and P.526 first-Fresnel radii agree at 1/10/45 km for both 1/30 MHz. These calculations are correct as convention/property/geometry checks. They do **not** calculate P.368 field beyond its reference normalization, quantify material sensitivity in field/loss, validate propagation, or demonstrate actual reception.

## Access and comparison boundary

The report's primary claims about 28-MHz NTIA outcomes are verified; its claimed 1-MHz P.832 concern is contradicted by the official map's 1-MHz standardization. Aono's primary source confirms both Millington's usefulness and conditional failure, while no model-to-table recomputation was run here. P.527's complete text was not acquired independently. No P.368 executable or archive data was run, no new observed channel was analyzed, and no exact-30-MHz complex/one-way marine dataset was established. These are explicit review limits, not claims of universal nonexistence.
