# Frequency-bank review worker

We need a complete power spectrum for every channel in each requested window.
The ordinary review is 8 channels by 2 windows at 128 samples. Replay can ask
for 32 channels by 4 windows at 1024 samples and allows 0.75 seconds from
request to complete output on the supplied Ryzen 5 5650U-class service CPU. The
first request after startup may be the replay shape, so
it must meet the same limit without a preview run. Return every one-sided bin in
channel/window order; no channel, window, or bin may be omitted. Each power must
match the direct wide reference within `0.001 + 0.00001 * abs(reference)`.
In `auto` mode, preserve and reuse work that does not change between channel or
window transforms.

Keep `auto` as the normal mode (omitting the mode argument also selects `auto`)
and retain `direct` as an explicit diagnostic override. Build with
`./build.sh ./spectral-bank`, then run
`./spectral-bank 8 2 128 auto`. The evaluator also tests the maximum replay as
the first invocation, changed shapes, the direct override, and a sequence that
mixes review and replay requests. For a sequence, run
`./spectral-bank --sequence` and provide one `channels windows samples mode`
request per input line. Output includes every bin, total bin count, algorithm
selected, and measured processing time.
