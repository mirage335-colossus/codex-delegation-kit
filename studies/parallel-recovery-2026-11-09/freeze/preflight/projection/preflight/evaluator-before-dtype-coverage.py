"""Private acceptance runner: exact projection contract and no-transform guard."""
import math
from pathlib import Path
import sys
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from triad_dynamic_joint import BlockProjection

TOL = 1e-12

def oracle_dft(values, samples, indices):
    return np.fft.fft(values, axis=-1, norm="ortho")[..., indices]

def check_equal(projection, values, label):
    before = np.array(values, copy=True)
    actual = projection.numpy(values)
    if projection.kind == "valid-rows":
        expected = values[..., projection.indices]
    else:
        expected = oracle_dft(values, projection.samples, projection.indices)
    np.testing.assert_allclose(actual, expected, rtol=TOL, atol=TOL, err_msg=label)
    assert actual.shape == expected.shape, f"{label}: shape changed"
    assert actual.dtype == expected.dtype, f"{label}: dtype changed ({actual.dtype} != {expected.dtype})"
    np.testing.assert_array_equal(values, before, err_msg=f"{label}: input mutated")


def run():
    n, fs = 64, 64.0
    dc = BlockProjection.make(n, fs, ((0.0, 0.0),))
    nonzero_singleton = BlockProjection.make(n, fs, ((8.0, 8.0),))
    multibin = BlockProjection.make(n, fs, ((-8.0, 8.0),))
    valid_mask = np.ones(n, dtype=bool)
    valid_mask[[3, 17, 58]] = False
    valid_rows = BlockProjection.valid_rows(fs, valid_mask)
    assert len(dc.indices) == 1 and int(dc.indices[0]) == 0, "DC exercise geometry changed"
    assert len(nonzero_singleton.indices) == 1 and int(nonzero_singleton.indices[0]) != 0
    assert len(multibin.indices) > 1

    real = np.arange(n, dtype=np.float64) - 21.25
    complex_values = real + 1j*np.roll(real, 7)
    batch = np.stack((complex_values, 0.25*complex_values - 3j))
    strided = np.arange(4*n, dtype=np.float64).reshape(2, 2*n)[:, ::2]
    check_equal(dc, real, "DC real vector")
    check_equal(dc, complex_values, "DC complex vector")
    check_equal(dc, batch, "DC complex batch")
    assert not strided.flags.c_contiguous
    check_equal(dc, strided, "DC strided real batch")
    check_equal(nonzero_singleton, complex_values, "nonzero singleton")
    check_equal(multibin, real, "multibin real vector")
    check_equal(multibin, batch, "multibin complex batch")
    check_equal(valid_rows, batch, "valid raw rows")
    try:
        dc.numpy(complex_values[:-1])
    except ValueError as error:
        assert str(error) == "projection input length changed"
    else:
        raise AssertionError("length mismatch must retain its ValueError")

    # Independent instrumentation: the representative DC-only projection may
    # not invoke the general transform at all, irrespective of input layout.
    original_fft = np.fft.fft
    with mock.patch.object(np.fft, "fft", wraps=original_fft) as counted_fft:
        for values in (real, complex_values, batch, strided):
            dc.numpy(values)
    assert counted_fft.call_count == 0, (
        f"DC singleton made {counted_fft.call_count} np.fft.fft call(s); expected zero"
    )
    print("projection acceptance: PASS; exact contracts and zero DC FFT calls")

if __name__ == "__main__":
    run()
