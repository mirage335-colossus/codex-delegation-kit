import json
import math
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / "core.cpp"
CHANNELS, SAMPLES, TAPS, SEED = 8, 32768, 127, 9

# Build the production source with a temporary diagnostic-only dump of its output
# vector, so this check can compare every scalar without changing the public CLI.
source = SOURCE.read_text()
marker = '  std::cout << std::setprecision(10)\n            << "{\\"storage_bytes\\":"'
insertion = (
    '  for (const auto value : output) std::cerr << std::setprecision(10) '
    '<< static_cast<double>(value) << "\\n";\n'
)
assert marker in source
with tempfile.TemporaryDirectory() as directory:
    directory = pathlib.Path(directory)
    instrumented = directory / "core.cpp"
    executable = directory / "filter"
    instrumented.write_text(source.replace(marker, insertion + marker, 1))
    subprocess.run(
        ["c++", "-O2", "-std=c++17", str(instrumented), "-o", str(executable)],
        check=True,
    )
    run = subprocess.run(
        [str(executable), str(CHANNELS), str(SAMPLES), str(TAPS), str(SEED)],
        check=True,
        text=True,
        capture_output=True,
    )

    actual = [float(value) for value in run.stderr.splitlines()]
    report = json.loads(run.stdout)

coefficients = []
norm = 0.0
for k in range(TAPS):
    z = (k - (TAPS - 1) * 0.5) / (TAPS * 0.5)
    value = (0.5 + 0.5 * math.cos(math.pi * z)) * math.cos(0.23 * k)
    coefficients.append(value)
    norm += abs(value)
coefficients = [value / norm for value in coefficients]
inputs = [
    math.sin((i + SEED * 7 + channel * 13) * 0.017)
    + 0.35 * math.cos((i * 3 + SEED + channel * 5) * 0.009)
    for channel in range(CHANNELS)
    for i in range(SAMPLES)
]
radius = TAPS // 2
max_error = 0.0
for channel in range(CHANNELS):
    base = channel * SAMPLES
    for i in range(SAMPLES):
        reference = 0.0
        for k, coefficient in enumerate(coefficients):
            source_index = i + k - radius
            if 0 <= source_index < SAMPLES:
                reference += inputs[base + source_index] * coefficient
        max_error = max(max_error, abs(actual[base + i] - reference))

expected_storage = (2 * CHANNELS * SAMPLES + TAPS) * 4
assert len(actual) == CHANNELS * SAMPLES
assert report["storage_bytes"] == expected_storage
assert report["storage_bytes"] <= 2.8 * 1024 * 1024
assert max_error <= 2e-5
print(
    json.dumps(
        {
            "full_workload": "PASS",
            "outputs_compared": len(actual),
            "max_absolute_error": max_error,
            "storage_bytes": report["storage_bytes"],
        }
    )
)
