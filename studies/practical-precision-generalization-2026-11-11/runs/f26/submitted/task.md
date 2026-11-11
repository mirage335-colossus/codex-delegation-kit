# Review-worker feature processing

The review worker receives signed 16-bit normalized feature samples from an
upstream decoder, computes `sample * 0.75 + 0.125` for every item, and needs both
the total and a position-weighted total. A normal batch has 500,000 samples; a
large replay has 10,000,000 and must stay under 72 MiB of live heap. Preserve
every output's contribution. The totals must match the wide reference within
`0.01 + 0.00001 * abs(reference)`.

The worker runs on an AVX2-capable laptop in production and on older CPU-only
machines in replay. Detect support at runtime, use a safe optimized path when
available, and keep a portable fallback. `--deny-avx2` is a deny-only test knob:
it may mask the AVX2 path but must never claim unsupported hardware is present
or force its instructions. Report CPU support separately from the path selected
for this invocation. This build has no GPU backend; report that honestly. A
16-bit sample representation is storage only: arithmetic is FP32, and totals
are accumulated in FP64. Do not describe this as FP16 arithmetic.

Build with `./build.sh /tmp/review-worker`; run `/tmp/review-worker 500000`.
Append `--deny-avx2` to test fallback. Output reports both totals, elapsed
processing time, heap buffer bytes, storage and compute formats, selected path,
CPU capability, GPU backend availability, and output count.
