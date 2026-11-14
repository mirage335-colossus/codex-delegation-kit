# Reviewed amendment to the native Robust channel appraisal

Use the [original engineering handoff](a84-owner.md) with this amendment to its HF calibration examples. The [independent source erratum](../evaluation/source-errata.md) records the reviewer’s check.

Table 3 is by Warrington, Stocker and Siddle. At the 95th percentile under the table's peak-to-mean ratio >3.5 criterion, Svalbard–Kiruna at 5.8 MHz in 2003 reports 12.0 ms composite delay spread, 1.5 ms effective delay spread and 2 Hz Doppler spread. Kirkenes–Kiruna at 20 MHz in **2004** reports 5.3 ms, 0.4 ms and 39.2 Hz, respectively. Each number summarizes a separate marginal distribution within its stratum. [Warrington, Stocker and Siddle, Table 3](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2005RS003294).

Use the reported values to anchor separate delay and Doppler checks for each path. A case combining the three settings from one row is a synthetic stress case. Obtain paired delay and Doppler observations before assigning probabilities to joint stress or calibrating a joint HF model. The first receiver comparison remains the current Helper-narrowed search against the full public search on identical I/Q, followed by held-out DATA prediction checks before transferring shared tap gains.

This amendment follows independent review of the original handoff. It adds no receiver or hardware validation. The research assistance count remains 67 web operations against a shared ceiling of 60.
