# Beacon receiver laboratory

This small Python laboratory explores a weak, two-tone signal. A transmitter
emits symbols as real sampled audio; the receiver's job is to recover the bits
from a stream when the arrival time and carrier frequency are not known exactly.
The intended receive pipeline comprises acquisition, timing/frequency refinement,
and symbol decisions. It operates after any reusable preparation and may be run
with independent candidate work in parallel. The laboratory uses only the Python
standard library.

`receiver.py` provides waveform generation and an aligned-symbol discriminator.
The current fast check gives the discriminator the generator's symbol boundaries;
it is useful when comparing changes to the discriminator. The generated data can
also be supplied to a receiver operating on a continuous stream. Synthetic
scenarios live in `cases.json`, which is maintained by hand and may change.
The transmitted bit count and sample rate in a case describe the observation;
noise and frequency offset are applied by the generator.

Run the existing checks with `python3 -m unittest -v`. A basic timing reference is
available with `python3 receiver.py`. These are deliberately inexpensive and run
on the local computer. The waveform is illustrative; it is not a production
modem, and the program makes no claims about hardware capacity.
