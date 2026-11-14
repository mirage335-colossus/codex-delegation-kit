# Corrected groundwave source and replay checks

## Bounds and source identity

- Follow-up web meter remains `review-ground`, now 10/20. Two new metered opens of raw GitHub source returned a cache-miss error; direct first-party GitHub connector fetch then returned the pinned `src/LFMF.cpp` body. These access outcomes do not establish source unavailability.
- NTIA LFMF repository commit: `57886e9d0a29fd8f04a6416dc3f782322f5a3589`, source project version 1.1. The acquisition log records official repository metadata, exact paths and expected Git blob IDs. Independently fetched pinned `src/LFMF.cpp` hashes to the expected blob `d3f7fbba729af9d7ae8dcf4d59caa40982c132dc` when framed as a Git blob. Each of the nine locally saved source/header files differs only by a final newline introduced by text serialization; removing exactly that LF yields the advertised upstream blob hash for each file. Source bodies are identical. Do not describe their byte-for-byte serialization as exact.
- API/source review: `include/LFMF.h` declares `Result` field, basic-loss, received-power and method outputs. `src/LFMF.cpp` computes effective earth radius from `Ns`, complex relative dielectric term from `εr`/`σ`, vertical surface impedance, the curve/residue-series switch at `80/f^(1/3)` km, field scaling using 4.77-dBi transmit gain and receive-power scaling using 4.77-dBi receive gain. `src/ValidateInputs.cpp` enforces the broad numerical input limits documented in the corrected report; those limits are not a substitute for P.368 physical validity.
- License file states public-service/as-is use and requests NTIA acknowledgement. Source remains in review scratch only; nothing was added to pumpModem.

## Independent compile and output comparison

Under the review-only directory `evaluation/reviews/ground/replay/LFMF/`, I copied the acquired source to a private review location, then ran:

```sh
g++ -O2 -std=c++11 -DLIBRARY_NAME='"LFMF"' -DLIBRARY_VERSION='"1.1"' -I include model_sweep.cpp src/*.cpp -o model_sweep
./model_sweep > model_sweep.txt
```

Environment: g++ 14.2.0. The corrected command completed; the resulting `model_sweep.txt` was byte-for-byte identical to the candidate's output. This validates reproducibility of the reported official-library outputs under those declared inputs, not correctness of real-world transfer.

I then compiled `mixed_replay.cpp`, a second caller that independently obtains each homogeneous segment field from the pinned API and applies the documented forward, reverse, reciprocal dB-field and boundary-split equations. Its six output rows match the candidate's forward/reverse/reciprocal/split results to 0.001 dB. Detailed outputs are `mixed_replay.txt`.

The model grid has substantial material sensitivity at the hypothetical inputs: at 100 km dry versus sea fields differ 39.145 dB at 1 MHz and 52.354 dB at 30 MHz; at 1 km the spreads are 4.645 and 31.431 dB. For sea at 10 km, equal 0-to-30-m heights change field 0.026 dB at 1 MHz versus 3.914 dB at 30 MHz. These are LFMF model responses, not confidence limits, true site ranges or hardware measurements. The 1-MHz 1000-km and 30-MHz 100-km rows particularly require the stated no-significant-skywave, homogeneous smooth-earth and antenna assumptions; atmospheric modes, terrain, local material/height errors and receiver sensitivity remain outside this run.

## Failed checks preserved and resolution

1. Candidate's initial compilation omitted `LIBRARY_NAME`/`LIBRARY_VERSION`; the compiler failed before a model call. The author found upstream CMake definitions and reran successfully. Both attempts and the fix are retained in `research/groundwave/acquisition-log.md` and `chapter.md:147-157`.
2. My first replay output diff used an incorrect relative source path after the compile/run; it failed only at diff. Corrected path comparison passed exactly.
3. My first parsing attempt sought 90-km homogeneous values in the candidate's printed homogeneous table, which only displays 1/10/100/1000 km; it raised a missing-key error before calculation. Replaced with a direct LFMF API caller evaluating the needed 10/90-km segment distances; all six mixed outputs reproduced.
4. Direct raw GitHub web opens for the two pinned source paths returned cache misses, but the separately available read-only GitHub connector returned the exact pinned `src/LFMF.cpp`; the source blob hash was independently reproduced from connector content. These were access-path failures, not model failures.

No P.368 site qualification, target-route comparison, antenna-plane/noise budget, rough-sea time process, terrain solver, modem run, or receiver/hardware benchmark was done. Those boundaries remain explicit.
