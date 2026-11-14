# Corrected groundwave source and replay checks

## Bounds and source identity

- Follow-up web meter remains `review-ground`, now 10/20. Two new metered opens of raw GitHub source returned a cache-miss error; direct first-party GitHub connector fetch then returned the pinned `src/LFMF.cpp` body. These access outcomes do not establish source unavailability.
- NTIA LFMF repository commit: `57886e9d0a29fd8f04a6416dc3f782322f5a3589`, source project version 1.1. Independent connector inspection confirmed the pinned source. Serialization added one final LF to the inspected source/header bodies; accounting for it recovered their upstream hashes. Source-body identity and byte-for-byte serialization identity must be distinguished.

## Independent compile and output comparison

The reviewer independently compiled the original caller against the pinned external implementation with the upstream library-name/version definitions.


Environment: g++ 14.2.0. The corrected command completed; the resulting `model_sweep.txt` was byte-for-byte identical to the candidate's output. This validates reproducibility of the reported official-library outputs under those declared inputs, not correctness of real-world transfer.

I then compiled `mixed_replay.cpp`, a second caller that independently obtains each homogeneous segment field from the pinned API and applies the documented forward, reverse, reciprocal dB-field and boundary-split equations. Its six output rows match the candidate's forward/reverse/reciprocal/split results to 0.001 dB. Detailed outputs are `mixed_replay.txt`.

The model grid has substantial material sensitivity at the hypothetical inputs: at 100 km dry versus sea fields differ 39.145 dB at 1 MHz and 52.354 dB at 30 MHz; at 1 km the spreads are 4.645 and 31.431 dB. For sea at 10 km, equal 0-to-30-m heights change field 0.026 dB at 1 MHz versus 3.914 dB at 30 MHz. These are LFMF model responses, not confidence limits, true site ranges or hardware measurements. The 1-MHz 1000-km and 30-MHz 100-km rows particularly require the stated no-significant-skywave, homogeneous smooth-earth and antenna assumptions; atmospheric modes, terrain, local material/height errors and receiver sensitivity remain outside this run.

## Failed checks preserved and resolution

1. Candidate's initial compilation omitted `LIBRARY_NAME`/`LIBRARY_VERSION`; the compiler failed before a model call. The author found upstream CMake definitions and reran successfully. Both attempts and the fix are retained in `research/groundwave/acquisition-log.md`.
2. My first replay output diff used an incorrect relative source path after the compile/run; it failed only at diff. Corrected path comparison passed exactly.
3. My first parsing attempt sought 90-km homogeneous values in the candidate's printed homogeneous table, which only displays 1/10/100/1000 km; it raised a missing-key error before calculation. Replaced with a direct LFMF API caller evaluating the needed 10/90-km segment distances; all six mixed outputs reproduced.
4. Direct raw GitHub web opens for the two pinned source paths returned cache misses, but the separately available read-only GitHub connector returned the exact pinned `src/LFMF.cpp`; the source blob hash was independently reproduced from connector content. These were access-path failures, not model failures.

No P.368 site qualification, target-route comparison, antenna-plane/noise budget, rough-sea time process, terrain solver, modem run, or receiver/hardware benchmark was done. Those boundaries remain explicit.
