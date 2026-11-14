"""Independent desk checks of public CSVs; no pump imports or side effects."""

import cmath
import csv
from pathlib import Path
import math


INPUTS = Path(__file__).resolve().parents[2] / 'inputs' / 'observations'


def rows(name):
    with (INPUTS / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def v(row, name):
    return complex(float(row[name + '_re']), float(row[name + '_im']))


def db(voltage):
    return 20 * math.log10(abs(voltage))


def loaded_q(f, h):
    a = f / 8000
    return (1 / h).imag / (a - 1 / a)


def resonator(f, q):
    a = f / 8000
    return 1 / (1 + 1j * q * (a - 1 / a))


def windowed_sinc_101(cutoff):
    # Build a zero-phase even kernel, then add the causal 50-input-row lag.
    zero_phase = lambda k: (cutoff / 1200 if k == 0 else
                            math.sin(math.pi * cutoff * k / 1200) / (math.pi * k))
    coeff = {k: zero_phase(k) * (0.54 + 0.46 * math.cos(math.pi * k / 50))
             for k in range(-50, 51)}
    z = sum(coeff.values())
    return lambda f: (sum(c * math.cos(math.tau * f * k / 2400)
                         for k, c in coeff.items()) / z * cmath.exp(-1j * math.tau * f * 50 / 2400))


def fold(f, fs):
    return f - fs * math.floor((f + fs / 2) / fs)


def vlf():
    rr = rows('vlf-transfer.csv')
    print('VLF: H_up=H_end/H_down, 20 log10(abs(H)); degrees are relative.')
    for case in ('V01', 'V02'):
        per = {}
        for setting in ('S0', 'S1'):
            selected = [r for r in rr if (r['case'], r['setting']) == (case, setting)]
            assert len(selected) == 7
            end = [v(r, 'end_to_end') for r in selected]
            down = [v(r, 'midpoint_to_output') for r in selected]
            up = [a / b for a, b in zip(end, down)]
            per[setting] = end, down, up
            fits = []
            for port, hs in [('UP', up), ('DOWN', down), ('END', end)]:
                qs = [loaded_q(float(r['rf_hz']), h) for r, h in zip(selected, hs)
                      if float(r['probe_offset_hz']) and port != 'END']
                if qs:
                    q = sum(qs) / len(qs)
                    assert max(abs(q - vq) for vq in qs) < 1e-7
                    assert max(abs(h - resonator(float(r['rf_hz']), q))
                               for r, h in zip(selected, hs)) < 3e-11
                    fits.append(q)
                print(f'{case} {setting} {port:4} worst_gain={min(map(db, hs)):+8.3f} dB'
                      f' edges={db(hs[0]):+.3f},{db(hs[-1]):+.3f} dB'
                      f' phase={math.degrees(cmath.phase(hs[0])):+.3f},'
                      f'{math.degrees(cmath.phase(hs[-1])):+.3f} deg'
                      + (f' loaded_Q={q:.6f}' if qs else ''))
            n_pass = sum(abs(db(h)) <= 3 for h in end)
            print('  nominal probes within 3 dB:', n_pass, '/ 7')
            # Model-conditional symmetric-about-8000 interval, not extra observations.
            lo, hi = 0.0, 8000.0
            for _ in range(60):
                mid = (lo + hi) / 2
                pair = [db(resonator(8000 + k * mid, fits[0]) *
                           resonator(8000 + k * mid, fits[1])) for k in (-1, 1)]
                if min(pair) >= -3:
                    lo = mid
                else:
                    hi = mid
            print(f'  fitted cascade symmetric -3 dB width {2*lo:.3f} Hz')
        up0, up1 = per['S0'][2], per['S1'][2]
        print('  max |S1 upstream - S0 upstream|=', max(abs(a-b) for a,b in zip(up0,up1)))
        assert max(abs(a-b) for a,b in zip(up0,up1)) < 3e-11
    sr = lambda case: [v(r, 'end_to_end') for r in rr if r['case'] == case and r['setting'] == 'S0']
    print('  max |V01 S0 - V02 S0| end-to-end=', max(abs(a-b) for a,b in zip(sr('V01'),sr('V02'))))
    assert sr('V01') == sr('V02')


def eme():
    rr = rows('eme-probes.csv')
    original = windowed_sinc_101(235)
    wide = windowed_sinc_101(500)  # Desk counterfactual only, 2400 -> 1200.
    for trial in ('L01', 'L02', 'L03'):
        selected = [r for r in rr if r['trial'] == trial]
        assert len(selected) == 7
        centers, out_db, wider = [], [], []
        print(f'EME {trial}: offset; pre - mix = post; output; rel gain; folded')
        for r in selected:
            p, m, f, d, y = [float(r[k]) for k in ('wide_witness_pre_premix_hz',
                                                  'signed_premix_subtracted_hz',
                                                  'wide_witness_post_premix_hz', 'probe_offset_hz',
                                                  'candidate_post_decim_hz')]
            g = v(r, 'candidate_post_decim') / v(r, 'wide_witness_post')
            assert p - m == f and y == fold(f, 600) and abs(g - original(f)) < 1e-10
            centers.append(f - d)
            out_db.append(db(g))
            wider.append(db(wide(f)))
            print(f'{d:+6.1f}; {p:+8.2f} - {m:+8.2f} = {f:+7.1f};'
                  f' {y:+7.1f}; {db(g):+8.3f} dB; {y != f}')
        assert len(set(centers)) == 1
        c = centers[0]
        print(f'  center {c:+.1f}; narrow/public: {abs(c)<=100}/{abs(c)<=300};'
              f' candidate min {min(out_db):+.3f} dB; desk 1200 min/max'
              f' {min(wider):+.4f}/{max(wider):+.4f} dB')
    # Filter at unaliased incoming frequency; aliased output coordinate alone
    # cannot say what was lost. 50 input samples = 12.5 candidate output samples.
    print(f'  +320.5 folds to {fold(320.5,600):+.1f}, gain {db(original(320.5)):+.3f} dB;'
          f' an incoming -279.5 has gain {db(original(-279.5)):+.3f} dB')
    print(f'  causal FIR group lag {1e3*50/2400:.6f} ms; memory 100 input samples, {1e3*100/2400:.6f} ms')
    print('  full center+nominal DATA half support 412.5 Hz, Fs > 825 Hz before skirts')
    print(f'  candidate at +212.5 Hz (narrow center edge + DATA edge) {db(original(212.5)):+.3f} dB')
    print(f'  desk 1200: gains at 412.5, 600, 787.5 Hz: '
          + ', '.join(f'{db(wide(f)):+.3f} dB' for f in (412.5, 600, 787.5)))
    pass_db = [db(wide(f / 16)) for f in range(412*16+9)]
    stop_db = [db(wide(f / 16)) for f in range(787*16+8, 1200*16+1)]
    print(f'  desk 1200 sampled nominal pass min/max {min(pass_db):+.4f}/{max(pass_db):+.4f} dB;'
          f' fold-onto-nominal-band stop max {max(stop_db):+.3f} dB (not continuous bounds)')


if __name__ == '__main__':
    vlf()
    eme()
