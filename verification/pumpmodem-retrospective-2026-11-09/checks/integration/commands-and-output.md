# Integration preflight evidence

Evidence source: prior tool outputs from the expanded-integration follow-up. Nothing in this record was rerun. Wrapper contents are preserved verbatim in `subclass_preflight.py`.

## Initial command failure

Command issued:

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=/tmp/pump-review-baseline28/tools /tmp/pumpmodem-cleanup-venv/bin/python -c 'from triad_receiver import CompleteBitReceiver; from triad_realtime_fft import FFTScreen; class_src="class DeviceFFTScreen(FFTScreen): pass"; exec(class_src); candidate=object.__new__(DeviceFFTScreen);\ntry: CompleteBitReceiver(None,candidate,None,memory_limit_bytes=1)\nexcept TypeError as error: print(type(error).__name__+": "+str(error))\nelse: raise SystemExit("unexpected subclass acceptance")'
```

Original stdout/stderr:

```text
  File "<string>", line 1
    from triad_receiver import CompleteBitReceiver; from triad_realtime_fft import FFTScreen; class_src="class DeviceFFTScreen(FFTScreen): pass"; exec(class_src); candidate=object.__new__(DeviceFFTScreen);\ntry: CompleteBitReceiver(None,candidate,None,memory_limit_bytes=1)\nexcept TypeError as error: print(type(error).__name__+": "+str(error))\nelse: raise SystemExit("unexpected subclass acceptance")
                                                                                                                                                                                                              ^
SyntaxError: unexpected character after line continuation character
```

This failed during Python command parsing, before imports/assertions: zero assertions.

## Corrected run

The wrapper was written to `/tmp/pump-review-expanded-integration/subclass_preflight.py` with the exact contents preserved in this directory's `subclass_preflight.py`. The executed command was:

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=/tmp/pump-review-baseline28/tools /tmp/pumpmodem-cleanup-venv/bin/python /tmp/pump-review-expanded-integration/subclass_preflight.py
```

Original stdout:

```text
TypeError: complete bit backend currently requires the canonical whole FFTScreen
```

Tool result: completed, 2.0 seconds wall time. One constructor-guard assertion passed: an `FFTScreen` subclass is rejected by `CompleteBitReceiver`.

## Snapshot reconstruction recipe

From a verified project Git checkout where commit `28f08825` resolves to the assigned baseline, recreate the source directory needed by this wrapper with:

```sh
mkdir -p /tmp/pump-review-baseline28
git archive --format=tar 28f08825 -- tools | tar -xf - -C /tmp/pump-review-baseline28
```

This is a reconstruction recipe only; it was not executed during the preflight. It extracts only the `tools/` tree needed by the wrapper and does not reconstruct tests, docs, or build artifacts.
