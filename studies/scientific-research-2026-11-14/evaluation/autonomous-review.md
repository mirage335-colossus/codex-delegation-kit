# Independent review of automatic initiation, depth, and uptake

The ordinary development request produced actual, substantial scientific
research with v3. The owner requested a dedicated lead before finishing its
native code audit, the lead and two scouts actually investigated both domains,
and the owner applied their findings to the renderer contract and receiver
checks. The baseline also initiated scientific research. The observed
difference is the requested depth and cross-source synthesis, not the presence
of research at all. Both EME branches exceeded their individual limits, and
v3's team exceeded its shared web limit. The scientific outcome is useful
evidence of the requested behavior, with the matched resource comparison
nonconforming.

The [frozen task](../inputs/autonomous-task.md) contains no instruction to do
research or delegate. The [shared contract](../inputs/autonomous-contract.md)
does offer both owners the same assistance mechanism and ceiling. I used the
[prior criteria](autonomous-criteria.md) and [native routing record](autonomous-routing.md)
and checked decisive support against original publications and current code.
The comparison varies the appended generic policy text. It does not compare
two separately installed kit versions or verify their provider settings. The
fresh owners and lead were denied access to the curated answer-bearing reports.

| Observed dimension | Baseline a17 | v3 a84 |
| --- | --- | --- |
| Initiation and overlap | Requested two bounded primary-source searches before completing the code audit. Then requested a focused expert ablation with two code reads. Continued mapping the renderer and receiver while waiting. | Requested a dedicated synthesis lead and two discovery branches before completing the audit. Requested coverage of relevant operating conditions, alternatives, counterevidence and implications for both regimes. Continued the production audit while they worked. Actual native request/dispatch and interim work are recorded for both. |
| Reusable evidence | Separate HF and EME reports establish a stationary benchmark, plausible departure conditions, two-leg EME timing, and evidence gaps. The independent expert adds a strong same-IQ and then fixed-candidate comparison. | The lead produced about 5,000 words including its access log, in addition to discovery notes. It compares shared trajectory, common support, diffuse/time–frequency and state-based alternatives, links conditional measurements to observable failure modes, and specifies what to keep or defer. It verifies several original papers directly, retains abstract and inaccessible-source limits, and excludes late EME-only evidence. |
| Reuse and engineering uptake | The owner keeps the native composite stream, reuses delay/gain branches, uses a concrete 75 Hz/two-ray covariance counterexample, and separates Helper search loss from DATA-basis loss under fixed proposals. This is substantive design uptake. | The owner also reuses the renderer and public DATA basis. It explicitly separates HF group-delay movement from phase-rate/Doppler, retains the geometric coupling for EME, and prioritizes a confidently wrong but accepted Helper interval even if narrow search returns a plausible candidate. The latter uses the lead's direct receiver trace. |
| Execution and limits | Owner finishes the scoped source audit and recommendation. Code changes, modem tests and qualification were outside this exercise. | Same execution boundary. Production results are outcomes to measure in a continuation, and neither arm supplies an executed receiver comparison. |

[a17 handoff](../results/a17-owner.md) · [a17 focused expert](../results/a17-expert.md)
· [a84 synthesis](../results/a84-synthesis.md) · [a84 handoff](../results/a84-owner.md)

### Decisive findings and corrections

1. **An actual renderer assumption changed.** The baseline handoff uses one
   nondispersive trajectory to retime the envelope and produce geometric carrier
   phase. The v3 lead uses the measured HF counterexample to make the low-order
   group delay and frequency residual separately configurable around the chosen
   carriers. This is more than a phrasing change. It admits a matched test where
   the group-arrival trajectories agree while the frequency forecasts diverge.
   Nickisch et al. §§3–5 support group-to-phase path-rate factors above one,
   up to 2.55 in the inspected 1999 fixed-beacon examples with traveling
   ionospheric disturbances. The values around 3–5 are ray-tracing results.
   These observations refute a universal one-to-one relation without implying
   statistical independence or a universal alternative factor. A physical
   smooth phase surface still constrains local group delay and frequency shift.
   The lead makes that compatibility explicit in its alternatives section.
   [Nickisch et al., §§3–5](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005RS003358)

2. **HF case provenance needs a correction.** The original Table 3 paper is
   by Warrington, Stocker and Siddle, in that order. Its 5.8 **MHz** Svalbard–
   Kiruna 2003 column supports composite/effective multipath widths of
   12.0/1.5 ms and composite Doppler width of 2 Hz. The 20 MHz Kirkenes–Kiruna
   values of 5.3/0.4 ms and 39.2 Hz are in **2004**, not 2005 as the lead's
   report says. The owner's final report gives the supported values without a
   year but preserves the inaccurate author order. These are marginal 95th
   percentile summaries of each selected condition at peak-to-mean power
   ratio above 3.5, not jointly measured triples. Use the numbers as
   explicit synthetic stratum anchors without assigning a joint probability.
   The composite and effective widths have different definitions, and the
   80%-power Doppler width is not F.1487's per-tap 2σ width. The owner's NBS
   correlation claim is supported by 56 reported observations. The median
   half-correlation spacing is about 4 kHz for **envelopes** and was exceeded
   90% of the time at about 1 kHz on that transauroral link. The NBS statistics
   supply neither complex covariance nor transfer to this modem.
   The [owner's reviewed amendment](../results/a84-owner-reviewed.md) corrects
   the author order, year and marginal-versus-joint interpretation. It preserves
   the original receiver discriminator and resource-limit failure. Apply it
   together with the original handoff. [Source erratum](source-errata.md)
   · [Warrington et al., Table 3 and §§3.1–3.3](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005RS003294)
   · [Auterman, NBS Technical Note 165, §§2–3.2](https://www.govinfo.gov/content/pkg/GOVPUB-C13-152cf80d492665dd7ee599c97d850018/pdf/GOVPUB-C13-152cf80d492665dd7ee599c97d850018.pdf)

3. **Receiver source supports the new discriminator.** I checked
   `src/triad_receiver.cpp:385–444` and
   `src/triad_simulation_stream.cpp:839–913` in the assigned pumpModem checkout.
   The renderer shares the delayed composite and its varying gains. Both
   receiver scheduling modes pass Helper-derived public intervals into coarse
   search; with no coarse coordinates the checked path exits. Fine scores
   coordinates derived from coarse results. The owner therefore checks both
   exclusion and candidate competition using identical I/Q, public geometry
   and Helper-band exclusion. Testing only an empty narrowed search would miss
   the wrong-but-plausible result. The baseline already proposed full-prior
   replay and distinguishing excluded support from ranking, so the new point
   is the distinct confidence/acceptance case and control, not discovery of
   same-I/Q replay itself. The planned build and probe entry points are in
   `docs/robust-current.md:347–385`. No pumpModem check ran here.

4. **The EME evidence supports the bulk/residual split.** The lead directly read
   the 2025 report of the June 2024 7159.45 MHz, 20 kW CW experiment. Its before
   and after plots support removing visible bulk drift from that observation
   using predicted geometry. It provides no quantitative remaining drift,
   weak-link threshold, 5.8 GHz delay profile or matched multi-carrier
   covariance. The eligible branch prefix separately supplies the modeled
   Taylor 5760 MHz self-echo widths and geometry-conditioned power spread.
   Independent EME review already checked those values and their distinct
   estimators. The synthesis gives the right reason to run a sparse shared
   model first, with a geometry-aware teacher and a weak tail. It does not
   recover the combined exemplar's breadth on operational near-band cases,
   polarization parameters, weather and local RF conditions, competing area
   weighting or measured/estimated calibration. Its HF scope similarly leaves
   current field coverage and spectral/regime uncertainty unresolved. This is
   broad reusable research across these decisions with a defensible native
   handoff, rather than a measured match to the entire historic corpus.
   [Tasmania radar team, §3.1](https://www.mdpi.com/2072-4292/17/3/352)
   · [Independent EME verification](eme-primary-verification.md)

### Resource accounting

- Baseline support used 12/12 HF operations and 23/12 EME operations, plus
  the expert's two shell-only reads. The baseline owner used 12 shell and
  eight web operations. I credit only the first 12 EME operations and owner
  evidence. The later Chalmers Doppler result is outside that branch prefix.
  [a17 EME correction](../results/a17-eme.md#eligibility-correction-evidence-inspected-within-operations-112)
- V3 support used 14/14 HF, 32/14 EME and 21/24 lead web operations. Total 67
  exceeded the requested 52 and shared 60. EME also used two shell invocations
  against one. The fourth lead shell read was prospectively authorized under
  the common shell ceiling, and does not cure that branch overrun. The v3 owner
  used 12 shell and eight web operations. Credit early EME evidence only
  where the correction establishes access in operations 1–14. The lead's own
  original-source contributions and cross-source derivations remain substantive.
  Neither apparent verification nor useful output retroactively authorizes extra
  operations. Equal offered resources do not imply equal use or cost.
  [a84 EME correction](../results/a84-eme.md#budget-correction-reporting-only-audit)
  · [Lead accounting](../results/a84-synthesis.md#ordered-lead-access-log)

### Separate prospective handoff and runtime acceptance

The [new-research uptake audit](../results/new-research-uptake.md) demonstrates a
different link in the workflow. A fresh scout consumed an actual newly produced
HF report and the delivered policy, read the current production code and mapped
each relevant finding to reuse, adaptation, rejection or a bounded check.
Examples include retaining the composite renderer, distinguishing the existing
GUI center separation from Gaussian PSD width, and reusing stochastic per-ray
controls instead of proposing a duplicate generator. It identifies the missing
general mode-transition capability and a matched receiver decision to test.
Credit this as an independent read-only source mapping. The audit's source
observations are not newly verified empirical claims or executed runtime
checks. The exercise is unpaired and cannot establish a prompt effect.

The final runtime diff carries the initiative through the main policy and
active roles. The trigger is proportionate to consequential decisions and
missing grounding even when the user says nothing about research. It reuses
adequate existing work, asks the coordinator for sustained depth, holds only
dependent commitments, and preserves tool/access and model boundaries.
The controller requests outside evidence through the existing result path
and retains its engineering no-network and supplied-context no-tools
instructions. No new role, selector, installer entry, dispatch mechanism or
permission grant entered the patch. The recorded full suite passed 313 tests
in 48.587 s. The later policy-only clarification distinguishes marginal
statistics from joint observations. `git diff --check` passed on the final
diff. These checks cover code and prompt delivery. Live model adherence
remains unmeasured. [Kit test log](kit-tests.txt)

I accept the source change and the task-scoped demonstration of automatic
substantial research. The baseline also activated and produced a useful
handoff, the comparison was adaptive in a familiar domain, and the resource
limit failures remain. Neither breadth comparable across all historical
research nor an improvement in cost, product performance or live deployment
adherence was measured.
