# Prospective study packet: HelperCarrier frequency measurement and acquisition

## Identity and evidence boundary

This is a hypothetical NEW engineering request prepared from source at `unbundled-home/___quick/p/_cur/dataPump/pumpModem`, HEAD `dae58eaccfd68cbf2366b85fd746b56fde089cd3`. The source worktree already had these dirty paths when inspected: `docs/helper-carrier.md`, `docs/validation.md`, `src/live_helper_presence.hpp`, `src/signal_view.cpp`, `src/signal_view.hpp`, `tests/test_live_helper_presence.cpp`, and `tests/test_signal_view.cpp`. They were left untouched. No source, tests, build, hardware, or campaign were run for this packet. The files in this directory are planning artifacts only.

The excerpts H01–H12 are concise, line-numbered source/test/documentation evidence. They intentionally exclude local-evidence and historical-validation narratives. Source is current code, not an assertion that any proposed study has been executed. The hypothetical developments in `developments.json` are fabricated future messages for a prospective decision exercise; they are neither records nor reports of actual runs. The packet does not reconstruct a prior campaign or presume a diagnosis, repair, successful execution, or preferred implementation.

## New request

A user asks: “Please assess whether HelperCarrier can provide useful frequency estimates soon enough after a new tone appears over a known operating offset range. Use captures with known generated truth, representative payload and metadata activity, and realistic chunking/noise. Report acquisition delay and error/uncertainty tradeoffs, identify any contract risk, and give me evidence to decide whether a focused implementation investigation is worthwhile.”

Decision objective: establish measured tradeoffs and feasibility limits for obtaining frequency-only evidence from helper captures. Keep multiple explanations open: estimator design, evidence/measurement model, source waveform or interference, capture/chunk behavior, resource/latency limits, and user tolerance for delay or uncertainty. No algorithm or code change is assigned by this request. The relevant source entry points/contracts include `helper::Tracker` (`include/datapump/helper_carrier.hpp`), `helper::Receiver` (`include/datapump/helper_receiver.hpp`), `helper::ToneTracker` (`include/datapump/helper_tone_tracker.hpp`), and the live capture adapter (`src/main.cpp::observe_helper_capture`).

## Invented study proposal, pending coordinator freeze

All figures below are hypothetical acceptance targets, not promises or values implied by the implementation. They are selected to give the two planning arms identical, concrete questions and may be revised by the coordinator before the exercise begins. Frequency truth is known from a generated signal; time starts at first captured sample of the tone. Test generated pilot offsets of −12, −3, +3, +12 Hz around a declared nominal, inside the code's nominal ±20 Hz constructor search example. Cross those offsets with two synthetic reference levels (24 and 30 dB-Hz), clean/noisy conditions, and representative payload/auxiliary metadata activity. Use multiple seeded realizations and both small irregular chunks (137 samples, as a current fixture uses) and larger batches (4096 samples). Ensure test cases include truth exactly at requested offsets; no actual runs are performed here.

Example decision targets: for every tone-present condition, (a) at least 95% of captures publish a finite frequency estimate whose absolute truth error is ≤0.10 Hz within 6.0 s, and (b) every estimate presented with a finite uncertainty interval covers truth; report coverage and time-to-first-covered estimate separately. For a tone-absent control, no accepted frequency publication may be attributed to the absent tone. These are deliberately strict and unvalidated hypothetical targets. Do not infer mathematical confidence coverage from a field named uncertainty, a source comment, or a model. Report empirical coverage with sample counts and the estimator's stated semantics. Also report median and 95th-percentile acquisition time, worst observed absolute error, work/memory, and declines/no-publication.

Keep frequency-only evidence distinct from phase, timing, metadata authentication, presence admission, payload recovery or completion. Preserve the current payload path, exact endpoint/END behavior, PCM progress, and retune invalidation phase. Do not fabricate a phase from frequency. Do not loosen any gate, uncertainty definition, age bound, presence/absence rule, or payload contract to meet the hypothetical targets. If a target conflicts with source contracts, surface the conflict instead of altering it.

## Matched arms and resources

Both planning arms receive exactly this scenario, H01–H12, and the same sealed `developments.json`; there are no arm-specific clues, data, priorities, deadlines, evaluation rubrics, or hidden source files. Start from current HEAD and the stated dirty baseline. Hypothetical resource envelope for the later exercise: six reasoning agents total including coordinator/reviewer; four concurrent test slots; shared ceiling 8 CPU cores and 16 GiB RAM; one already-ready synthetic fixture if the coordinator elects to use it. These are planning assumptions, not current allocations or actual resource availability. The prepared artifacts require no campaign execution. No model, routing, effort, token budget, cost ratio, or alternate arm plan is prescribed here.

## Contract and practical constraints established by source

- Helper tones use a 90% pilot / 10% auxiliary power split and 400 Hz spacing (H01). That is waveform geometry, not a receiver precision guarantee.
- The simple independent presence tracker publishes bounded observations; its comments define detection and absence behavior (H02). Do not conflate detection with precision.
- ToneTracker declares dated frequency knowledge separately from current presence, phase and qualification, and invalidates phase at explicit retunes (H03). Frequency-only observations do not grant broader authority.
- Receiver references carry independent dates and validity flags; frequency and phase observation dates may differ (H04). Optional frequency work is explicitly separately funded, bounded, and may decline; recent-presence confirmation is required before it publishes and commit changes only frequency provenance (H05, H12).
- Existing synthetic tests exercise known-frequency/noise/payload captures, chunk sizes, truth error and uncertainty (H06–H07). Those source tests identify useful coverage, not results for this prospective exercise.
- Live capture calls the presence tracker and metadata receiver independently (H08). A helper presence row is bit-free and pending; interruptions, rate changes and EOF do not count as observed absence, and the same row is completed only after captured absence (H09).
- General development contract requires decoding after physical completion and six seconds of observed absent symbols; EOF, cancellation and other events cannot manufacture completion (H10).
- Relevant component test registrations are visible in H11. Registration is not proof that these tests passed in this checkout.

## Acceptance of a planning result

A useful result states the measured question, source predictions separately from any runtime observations, a matched reproducible dataset and environment if subsequently authorized, all target results and failures, contract boundaries, uncertainties and the narrow next decision. This packet itself satisfies no implementation, runtime, build, hardware or qualification acceptance condition.
