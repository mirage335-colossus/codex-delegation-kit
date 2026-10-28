# Carrier domain: blinded screen

Expert review remains pending. No architecture or winner is selected. Each original case is credited for its own retained findings; unresolved candidates contribute only to upper bounds. The two verification records cover all 23 original IDs. No new web operations or project execution were performed.

| Case | Full qualified + unresolved (bounds) | Strict-prefix qualified + unresolved (bounds) | Research operations | Report bytes |
|---|---:|---:|---:|---:|
| r733 | 5 + 0 (5–5) | 5 + 0 (5–5) | 13 | 15310 |
| r672 | 3 + 1 (3–4) | 3 + 1 (3–4) | 16 | 15001 |
| r806 | 3 + 0 (3–3) | 3 + 0 (3–3) | 10 | 11401 |
| r842 | 4 + 0 (4–4) | 4 + 0 (4–4) | 13 | 12468 |
| r698 | 4 + 0 (4–4) | 3 + 1 (3–4) | 20 | 15566 |
| r147 | 3 + 0 (3–3) | 3 + 0 (3–3) | 16 | 15141 |

R698 operations 17–20 exceed the 16-operation limit; Baluev full text was opened at 19. F4 is retained for the full report but unresolved for the strict prefix. R672 F4 remains unresolved in both. Counts are descriptive. Arm-pair means and arm unions require the blinded mapping and are deferred; no missing data is treated as zero.

## r733

**Decision:** Test early frequency-only evidence; 6 s, 0.10 Hz/95% are prospective targets.  
**Evidence and options:** Rife threshold versus local bounds; Kay 1989 abstract supports a simple comparator; generalized Kay supports a bounded lag sweep under coherence. H03/H05 distinguish uncertainty, presence and authority. Kay 1984 is a retrieval lead, not an implementable result.  
**Limits:** Rife is stationary single-tone Gaussian; its original page locator exceeds logged access although the verifier independently confirmed the passage. No C/N0 conversion or accuracy is established.  
**Expert question:** Does a cheap matched Kay/lag/profile comparison separate acquisition tails from mismatch?  
**Cheapest discriminator:** Replay matched present/absent PCM with a small coherent lag set, report tail error, declines and false admissions; retunes invalidate coherence.  
**Rejected/deferred:** Reject CRB or finite uncertainty as proof; defer repeated tuning and ranking.  

## r672

**Decision:** Choose a next frequency-only acquisition discriminator under the hypothetical deadline.  
**Evidence and options:** Clarkson full text supports coarse/fine periodogram ML and O(N)/O(1) phase estimation with branch-point correction; model-specific threshold motivates tail checks.  
**Limits:** Complex stationary AWGN and phase assumptions do not establish real helper performance; H05 does not certify phase across native hops. Joint frequency/rate F4 has only secondary snippets and remains unresolved.  
**Expert question:** Does branch correction or coarse/fine search reduce tails at equal support and cost?  
**Cheapest discriminator:** Compare both on matched PCM, sweep branch boundaries and report declines, absent admissions and coverage.  
**Rejected/deferred:** Do not adopt a frequency-rate model without primary evidence and observed residual curvature; multi-tone paper inaccessible.  

## r806

**Decision:** Decide which cheap frequency-only comparators merit a bounded measurement.  
**Evidence and options:** Quinn abstract supplies three-Fourier-coefficient asymptotic comparator; Kay abstract supplies a simpler comparator; Knockaert abstract gives model-bound threshold caution. Quinn peer-review label is independently documented.  
**Limits:** Asymptotic single-tone results do not establish finite-sample tails or shaped/payload interference. SNR*T/ln(T) is not mapped from the given dB-Hz levels.  
**Expert question:** Do three-bin interpolation and Kay beat the existing method on the same short apertures?  
**Cheapest discriminator:** Compare identical PCM and search bands, compute and error tails with no-tone controls.  
**Rejected/deferred:** Reject threshold numerical transfer and broad multi-tone/subspace expansion as first step.  

## r842

**Decision:** Choose a next acquisition comparison while retaining frequency-only authority.  
**Evidence and options:** Rife/Barankin threshold caution, Kay block estimate, lag tradeoff and Doppler-spread abstract motivate stationary versus time-varying comparisons.  
**Limits:** Doppler multiplicative noise is not proven equivalent to oscillator drift; peer-review labels S1–S5 are unverified despite publication metadata.  
**Expert question:** Does time variation negate longer coherent support, and is lag range adequate?  
**Cheapest discriminator:** Use matched stationary/time-varying PCM with reset controls and measure error tails and absence admissions.  
**Rejected/deferred:** Do not treat invented planning targets as measured requirements or immediately expand to ESPRIT/MUSIC/EKF.  

## r698

**Decision:** Investigate causal frequency acquisition and absent-tone control at the prospective deadline.  
**Evidence and options:** Kay abstract supports a block comparator; J-STAGE abstract supports a phase/frequency Kalman candidate in its own digital-carrier setting. Full Baluev preprint supports scan-level significance as a limited analogy.  
**Limits:** Baluev full text was operation 19, outside the 16-operation prefix; strict-prefix F4 is unresolved. Rife full mirror was separately verified, while original access was abstract/metadata. No source proves receiver-specific false-alarm rate.  
**Expert question:** Does sequential filtering survive resets, and does full-search repeated-look calibration prevent false admissions?  
**Cheapest discriminator:** Compare phase-continuous versus reset captures and run no-tone controls over the actual search/look schedule.  
**Rejected/deferred:** Do not select a winner or transfer digital-symbol acquisition timing or analytical false-alarm formulas.  

## r147

**Decision:** Select a discriminator for six-second frequency-only precision, preserving nonpublication.  
**Evidence and options:** Rife mirror supports finite-record outlier/global-search caveats; Tretter and MAP/ML abstracts motivate phase versus magnitude comparisons.  
**Limits:** The mirror is third-party; high-SNR complex-tone premises and actual chunk/phase continuity remain unverified. Chunk invariance is a proposed test, not a paper or runtime result.  
**Expert question:** Is performance driven by phase/magnitude weighting or by genuine signal discontinuities rather than delivery partition?  
**Cheapest discriminator:** Replay identical PCM/timestamps in 137 and 4096 chunks, plus a gap/reset control; compare support endpoints, tails and coverage.  
**Rejected/deferred:** Defer sparse instantaneous-frequency and inaccessible nonsinusoidal EKF leads; neither establishes task fit.  

## Deduplicated cross-case catalog

This catalog is descriptive across all blinded cases, not an arm-level union. Every ID remains credited to its original case.
- **Acquisition threshold and outlier tails versus local variance:** r733:F1, r672:F3, r806:F1, r842:F1, r698:F1, r147:outliers
- **Simple Kay-family block comparator:** r733:F2, r806:F3, r842:F2, r698:F2
- **Differential-phase lag and ambiguity tradeoff:** r733:F3, r842:F3
- **Low-SNR Kay 1984 retrieval/control lead:** r733:F4
- **Separate frequency uncertainty, presence and authority:** r733:F5
- **Coarse-to-fine periodogram/ML acquisition comparator:** r672:F1
- **Kay weighted-phase branch-point bias and recursive correction:** r672:F2
- **Joint frequency/rate candidate (academic support unresolved):** r672:F4 (unresolved)
- **Three-Fourier-coefficient interpolation comparator:** r806:F2
- **Time variation or multiplicative-noise mismatch to stationary models:** r842:F4
- **Sequential phase/frequency Kalman candidate:** r698:F3
- **Search-maximum and repeated-look false-admission calibration:** r698:F4 (r698:F4 unresolved in strict prefix)
- **Phase-only versus magnitude-weighted observations:** r147:phase-vs-magnitude
- **Observation aperture versus delivery partition:** r147:information-duration

## Provenance and handoff

Per-finding stages, source IDs, URLs, original locators, individual verifier findings, all original rejected candidates and follow-ups are in the companion JSON. All expert stages are not individually assessed. R733 F1 cites page-specific Rife content beyond its logged original access; the independent verifier opened and confirmed the passage separately. R842 labels sources peer-reviewed without establishing that status; publication and peer-review are separate. Quinn is the one source with explicit peer-review evidence in the reviewed records. Other unknown review status is not a negative finding.

No source verifies performance for these hypothetical levels, offsets, deadline, chunk geometry or target. A practical handoff needs the signal/noise bandwidth convention, sample rate, envelope, continuity, dynamics, uncertainty semantics and capture ground truth. These questions need not delay expert judgment on the next discriminator. No universal added research gate is proposed. Source-only code excerpts establish contracts, not measured runtime behavior. Native model, token and weekly-usage telemetry is unavailable; no usage or savings conclusion is supported.
