# Original Watterson report: browser retrieval

Coordinator primary-source retrieval, 2026-11-14. This is fresh public-source evidence, not a transcription of the withheld reference corpus or evaluator answers.

Source: Watterson, Juroshek and Bensema, *Experimental Verification of an Ionospheric Channel Model*, ESSA ERL 112-ITS 80 (1969), AD0699486. [Internet Archive full OCR](https://archive.org/stream/DTIC_AD0699486/DTIC_AD0699486_djvu.txt).

The research web reader failed on the stream, download and metadata URLs (three charged operations). The supported in-app browser successfully displayed the original full OCR, title and URL. Browser use: one navigation, one full AX observation (235,418 characters), two local extractions from that observed text; documentation restore and completion summary are separate control calls. No authentication, download, settings change or external write. The eight-action prospective browser allocation was not exceeded. The entire raw OCR was read into the browser tool's observed-state variable, but is not copied into this repository. The selected measurements and source limitations below are transcribed from that actual observation. OCR glyph corruption remains; use the table headings and surrounding prose to interpret microseconds, not OCR's occasional `ns`/`ps` glyphs. No plotted curve was digitized.

## Conditions (printed pp.44–46, section 3.3)

Transmitter Long Branch, Illinois (40°13'N, 90°01'W), receiver Table Mountain near Boulder, Colorado (40°08'N, 105°14'W), great-circle distance 1,294 km. The report explicitly calls it a midlatitude path. Frequencies 9.259 MHz day and 5.864 MHz night, sufficiently below predicted MUF to make one- and two-hop modes probable. Recording totals: 7 November 1967, 9.259 MHz, 12:10–19:07 MST, 5:09 recorded; 9–10 November, 5.864 MHz, 22:05–08:50, 7:18 recorded; 30 November, 9.259 MHz, 07:25–15:40, 4:43 recorded. Hourly calibrations and tape rewinding interrupted recordings. Twelve intervals were selected as most nearly stationary in fading rates, modal delays and powers. Three 10–13 minute cases were analyzed in detail; these are selected model-verification samples, not an unconditional population/outage census. The observed source says typical day/night conditions, not a verified geomagnetic-quiet index classification.

## Tables 4, 6 and 8 (printed pp.62, 70, 78)

Columns in each tuple: path, relative delay in microseconds, relative power in dB, frequency shift in Hz, frequency spread **2 sigma** in Hz. Rows `a/b` are magnetoionic components of the same path and must not also be counted as independent additional power on top of the aggregate path row. Section 2's Gaussian spectrum formulation explicitly defines the component sigmas as standard deviations. Relative delays use an arbitrary 200-Hz receiver reference (section 5.1), not absolute flight time.

Table 4, sample I1: 9.259 MHz, 30 November 1967, 10:15–10:28 MST, 780 s, 3.125 Hz measurement rate, 2,437 values, three paths. Channel mean delay 137 us, channel time spread 478 us, frequency shift 0.0013 Hz, frequency spread 0.123 Hz, estimated individual path time spread 20 us.

```
1a,40,-4.1,0.0022,0.0073
1b,40,-4.3,0.0170,0.0318
1,40,-1.2,0.0094,0.0272
2,290,-7.2,0.0089,0.144
3,1139,-13.5,-0.167,0.340
```

Effective independent counts for paths 1/2/3: 30.3/198.5/469.4, much smaller than the raw sample count. Section 5.1 identifies 1E, 1F and 2F modes. The strongest delay difference is 250 us, reciprocal 4.0 kHz; first/third difference 1,099 us, reciprocal about 0.91 kHz. Seven central tones were fitted, four outer tones checked. Author ratings: excellent to 3 kHz, good to about 6 kHz, adequate to about 12 kHz. Finite intra-mode spread limits the discrete-path approximation; receiver measurement errors were below −30 dB.

Table 6, sample I2: 9.259 MHz, 30 November 1967, 11:10–11:20 MST, 600 s, 6.25 Hz measurement rate, 3,750 values, four paths. Channel mean delay 173 us, time spread 520 us, frequency shift 0.0171 Hz, frequency spread 0.140 Hz, estimated path time spread 30 us.

```
1a,40,-4.1,-0.0008,0.0064
1b,40,-5.5,0.0127,0.0084
1,40,-1.7,0.0071,0.0153
2,290,-5.9,0.0159,0.180
3,590,-17.6,0.108,0.334
4,1126,-12.6,0.118,0.336
```

Effective counts 15.0/191.4/354.7/356.8. Author deterministic fit ratings: excellent to 2 kHz, good to about 4 kHz, adequate to about 8 kHz. A narrow fit's smaller fitting error comes at the cost of greater out-of-band error. Hypothesis tests were conditional on selected samples and their effective counts, not proof of a universal independent Gaussian law.

Table 8, sample I3A: 5.864 MHz, 10 November 1967, 04:17–04:30 MST, 780 s, 3.125 Hz measurement rate, 2,437 values, three paths. Channel mean delay 589 us, time spread 464 us, frequency shift 0.110 Hz, frequency spread 0.0666 Hz, estimated path time spread 100 us.

```
1a,445,-3.8,0.0764,0.0360
1b,445,-5.7,0.134,0.0320
1,445,-1.6,0.0989,0.0658
2a,750,-10.8,0.121,0.0104
2b,750,-10.6,0.141,0.0130
2,750,-7.7,0.131,0.0229
3a,1088,-12.9,0.121,0.0149
3b,1088,-10.4,0.151,0.0206
3,1088,-8.5,0.140,0.0335
```

Effective counts 88.3/30.5/45.4. I3A fits seven central frequencies; I3B uses a different fit to the same underlying observations and is not an independent campaign. Nighttime intra-mode dispersion is larger, reducing the adequate bandwidth to about 2.4 kHz (good about 1.2 kHz). Dominant reciprocal delay scales: 305 us → about 3.3 kHz and 643 us → about 1.55 kHz. The abstract rounds the three adequate widths to 2.5, 8 and 12 kHz and relates them to about one fourth of the reciprocal of intra-mode time spread.

## Use boundary

These selected observations support a scoped ordinary midlatitude baseline and within/between-mode distinction. They cannot establish universal quiet-channel distributions, contemporary occurrence probabilities, long-duration nonstationarity, auroral/trough/TEP behavior, terminal SNR, absolute delay, or receiver performance. Calculations from rounded table values should report rounding discrepancies instead of forcing exact agreement. The browser evidence closes the earlier retrieval failure; those failed accesses remain in the ledger.
