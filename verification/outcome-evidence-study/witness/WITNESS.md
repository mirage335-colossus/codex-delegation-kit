# Receiver-stage feasibility witness

This scratch-only exercise tests whether a direct, bounded use of the historical
receiver is feasible. It is not a candidate-agent result. `witness_slice.py`
uses the native HF 36 Hz / 10 Added Symbols / 30 MHz / no-Helper / non-FHSS
waveform family (from the list's encrypted GPSDO case) and passes native channel
samples and native templates to the existing `FFTScreen` acquisition stage.
The `hf-worst` mode selects HF worst spread, margin 3, and `each-65` selective
perturbation; `flat` is a simpler contrast. These are both diagnostic samples,
not qualification of the complete listed case.

Each output is based on one fixture-seed source bit, a high 80 dB-Hz simulated
DATA C/N0, one epoch and zero CFO/clock candidates. The window location uses
transmitter truth, narrowed to +/-0.2 seconds. Oscillator effects are disabled.
Only a two-second DATA template and four-second capture are scored. The signal
and templates use the actual native source and native channel; neither the fine
search, complete multi-bit receiver, Helper, streaming workload, statistical
success target, nor saturation of all machine CPU threads is tested. Its wall
times are not capacity evidence and were recorded on a shared busy machine.

Reproduction from this directory requires the scientific Python environment
and compiler/toolchain used by the original fixture. The initial configuration
with GUI and CLI both off failed: `datapump_install_native requires TARGETS`.
Configuration with CLI enabled and the targeted build succeeded:

```
cmake -S . -B build/witness -DDATAPUMP_BUILD_GUI=OFF -DDATAPUMP_BUILD_CLI=ON -DDATAPUMP_PORTABLE=OFF -DDATAPUMP_COMPILER_CACHE=OFF -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build/witness --target triad_helper_export -j 2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/pumpmodem-cleanup-venv/bin/python witness_slice.py 0
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/pumpmodem-cleanup-venv/bin/python witness_slice.py 1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/pumpmodem-cleanup-venv/bin/python witness_slice.py 0 hf-worst
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/pumpmodem-cleanup-venv/bin/python witness_slice.py 1 hf-worst
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /tmp/pumpmodem-cleanup-venv/bin/python -m unittest discover -s tests -p 'test_triad_realtime_fft.py'
```

Both bits had the larger correct score and 0 ms estimated arrival error in both
flat and HF worst runs; these are four single deterministic demonstrations, not
a statistical probability estimate. The existing FFT screen tests passed 9/9.
Outputs are retained as `witness-result-0.json`, `witness-result-1.json`,
`witness-result-worst-0.json`, and `witness-result-worst-1.json`. The first two
were generated before adding the optional scenario argument and have the same
flat numerical inputs. The witness code and results can be copied to an evidence
record; native build artifacts need not be retained.
