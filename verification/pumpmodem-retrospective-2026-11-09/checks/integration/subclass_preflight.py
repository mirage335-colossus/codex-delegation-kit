from triad_receiver import CompleteBitReceiver
from triad_realtime_fft import FFTScreen

class DeviceFFTScreen(FFTScreen):
    pass

candidate = object.__new__(DeviceFFTScreen)
try:
    CompleteBitReceiver(None, candidate, None, memory_limit_bytes=1)
except TypeError as error:
    print(type(error).__name__ + ": " + str(error))
else:
    raise SystemExit("unexpected subclass acceptance")
