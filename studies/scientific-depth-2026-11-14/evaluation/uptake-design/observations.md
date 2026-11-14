# Constructed transfer and frequency observations

These are deterministic bench calculations for this planning exercise. No captured field data, equipment observations, modem outputs or runtime performance results are included. All complex amplitudes are dimensionless and use the positive-frequency convention `exp(+j 2π f t)`. Each row is a separate single-tone probe. Frequencies in the tables are in hertz. No randomness, noise, pulse shaping, acquisition or decoder model was used.

## Sub-9 kHz transfer

The two cases `V01` and `V02` represent separate linear, single-port fixture conditions centered at 8,000 Hz, with the same 225 Hz nominal DATA interval. The intermediate port is between an upstream path and a downstream response. At that port, compare independently calibrated injection and output readings. The intermediary probe and full-chain probe use the same voltage/gain normalization, output reference and phase origin. Offset 0 has unit complex response in each fixture. Absolute gain, radiated power and noise are outside these measurements.

Setting `S0` is the installed fixture configuration. Setting `S1` commands the same available downstream broadband setting in both cases. Everything upstream stays unchanged across the two settings within a case. The provisional bench objective is to retain relative voltage magnitude within 3 dB of the center response at the seven nominal DATA probe offsets. This objective only compares these fixture states and frequencies. It gives no coverage between or outside the probes, including any Helper, guard band or spectral skirt.

[VLF complex observations](vlf-transfer.csv)

## Passive EME receive-frequency chain

The three trial labels `L01` through `L03` represent separate generated conditions for passive EME near 5.8 GHz. A modeled common frequency term is available from geometry and is subtracted in each trial. The wide witness reports calibrated tones immediately before and after this pre-mix. Its pre-mix complex sample rate is 12,000 samples/s and covers all listed before-mix tones. Its normalized unit complex response after pre-mix is the phase/gain reference. The candidate chain sees the same post-mix tones at 2,400 complex samples/s, after ideal reduction that passes these probe frequencies without changing gain or phase. It uses a 101-tap Hamming-windowed sinc with 235 Hz nominal cutoff and unity DC gain, then decimates by four to 600 complex samples/s. Candidate reading frequencies use the interval `[-300, 300)` Hz and include any remaining folded component. The candidate complex values retain the filter phase. Use 20 log10 of the complex magnitude for relative voltage gain in dB.

The proposed narrow detector center-frequency interval after pre-mix is ±100 Hz. This proposal is a computational choice for comparison. For these trials the engineering owner retains a declared public residual center-frequency prior of ±300 Hz and a nominal DATA interval of ±112.5 Hz relative to the received center. The probes separate offset from received center and do not characterize additional scatter, jitter, acquisition, missed detections or behavior beyond the DATA probes. Neither wide witness nor exact trial residual is supplied to the candidate detector.

[EME signed frequencies and complex observations](eme-probes.csv)

Both CSV files can be regenerated with `python3 -I build_observations.py <empty scratch directory>`. The generator defines the synthetic inputs and exact filter. It does not implement the modem or prescribe a development decision.
