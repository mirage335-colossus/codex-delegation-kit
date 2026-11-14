"""Generate deterministic desk observations for the fresh-owner exercise."""

import argparse
import cmath
import csv
import math
from pathlib import Path


PROBE_OFFSETS_HZ = (-112.5, -75.0, -37.5, 0.0, 37.5, 75.0, 112.5)
VLF_CENTER_HZ = 8000.0
INPUT_RATE_HZ = 2400.0
DECIMATION = 4
FILTER_TAPS = 101
FILTER_CUTOFF_HZ = 235.0


def tuned_current(frequency_hz, loaded_q):
    """A series RLC's current gain, relative to its own resonant current."""
    ratio = frequency_hz / VLF_CENTER_HZ
    return 1.0 / (1.0 + 1j * loaded_q * (ratio - 1.0 / ratio))


def lowpass_coefficients():
    midpoint = (FILTER_TAPS - 1) // 2
    cutoff = FILTER_CUTOFF_HZ / INPUT_RATE_HZ
    coefficients = []
    for i in range(FILTER_TAPS):
        offset = i - midpoint
        ideal = 2.0 * cutoff if offset == 0 else (
            math.sin(math.tau * cutoff * offset) / (math.pi * offset)
        )
        window = 0.54 - 0.46 * math.cos(math.tau * i / (FILTER_TAPS - 1))
        coefficients.append(ideal * window)
    dc_gain = sum(coefficients)
    return [coefficient / dc_gain for coefficient in coefficients]


def filter_response(coefficients, frequency_hz):
    return sum(
        coefficient * cmath.exp(-1j * math.tau * i * frequency_hz / INPUT_RATE_HZ)
        for i, coefficient in enumerate(coefficients)
    )


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(
                f"{value:.12g}" if isinstance(value, float) else value
                for value in row
            )


def vlf_rows():
    cases = (("V01", 20.0, 200.0), ("V02", 200.0, 20.0))
    for case, upstream_q, downstream_q in cases:
        for state, selected_q in (("S0", downstream_q), ("S1", 20.0)):
            for offset in PROBE_OFFSETS_HZ:
                frequency = VLF_CENTER_HZ + offset
                downstream = tuned_current(frequency, selected_q)
                full_path = tuned_current(frequency, upstream_q) * downstream
                yield (
                    case, state, frequency, offset,
                    full_path.real, full_path.imag,
                    downstream.real, downstream.imag,
                )


def eme_rows():
    coefficients = lowpass_coefficients()
    output_rate_hz = INPUT_RATE_HZ / DECIMATION
    trials = (
        ("L01", 2418.25, 62.5),
        ("L02", 2372.75, -144.0),
        ("L03", 2284.50, 283.0),
    )
    for trial, premix_hz, residual_hz in trials:
        for offset in PROBE_OFFSETS_HZ:
            input_hz = residual_hz + offset
            before_premix_hz = premix_hz + input_hz
            output_hz = (input_hz + output_rate_hz / 2) % output_rate_hz
            output_hz -= output_rate_hz / 2
            gain = filter_response(coefficients, input_hz)
            yield (
                trial, offset, premix_hz, before_premix_hz, input_hz,
                1.0, 0.0, output_hz, gain.real, gain.imag,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    write_csv(
        output / "vlf-transfer.csv",
        (
            "case", "setting", "rf_hz", "probe_offset_hz",
            "end_to_end_re", "end_to_end_im",
            "midpoint_to_output_re", "midpoint_to_output_im",
        ),
        vlf_rows(),
    )
    write_csv(
        output / "eme-probes.csv",
        (
            "trial", "probe_offset_hz", "signed_premix_subtracted_hz",
            "wide_witness_pre_premix_hz", "wide_witness_post_premix_hz",
            "wide_witness_post_re", "wide_witness_post_im",
            "candidate_post_decim_hz", "candidate_post_decim_re",
            "candidate_post_decim_im",
        ),
        eme_rows(),
    )


if __name__ == "__main__":
    main()
