Independent verification covered only opaque cases r733, r672 and r806. Their original reports were preserved. The group used 21/24 logical web operations; the reports themselves each stayed within the 16 total, 8 query and 10 open contract limits.

| Case | Qualified findings | Unresolved | Main verified evidence |
|---|---:|---:|---|
| r733 | 5 | 0 | Threshold/outlier caveat; Kay-style and generalized-lag estimators; low-SNR estimator lead; supplied receiver-contract caveat |
| r672 | 3 | 1 | Periodogram/ML coarse-to-fine method; Kay branch-point correction; threshold/outlier validation; frequency-rate paper claim remains unresolved |
| r806 | 3 | 0 | Threshold-bound caveat; Quinn three-bin interpolation; Kay estimator under its stated model |

Quinn 1994 is the only inspected source whose institutional record explicitly marks it peer-reviewed. Other journal or conference publication records were verified, but their review status was not established. Rife–Boorstyn's low-SNR outlier claim is supported by a third-party scan; r733's own operation log did not record opening that scan, so its locator/access claim exceeds the logged evidence. The reviewer checked the passage independently; this does not retroactively improve the original record.

Every academic result remains conditional on its single-tone/stationary AWGN model. None establishes the proposed `<=0.10 Hz by 6 s at >=95%` target, or maps the task's dB-Hz reference levels to the papers' SNR conventions. Phase coherence, real-signal ambiguity, envelope/payload activity, and false-publication performance still need matched receiver captures. No winner or Terra/expert stage outcome was assessed.

See [carrier-1.json](carrier-1.json) for per-finding decisions, source locations, operation log, deduplicated origins and limitations.
