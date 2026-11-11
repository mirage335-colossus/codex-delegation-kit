# Burst scoring task

The service scores every row in a short dense batch as a weighted sum. During
development, the usual batch has 4 rows of 200,000 values. In production, bursts
can reach 5 rows of 5,000,000 values, and the worker has a 64 MiB buffer budget.
Return one score for every row, in input order, within the stated budget. Scores
must be within `abs(error) <= 0.002 + 0.00002 * abs(reference)` of the reference
calculation. Do not silently omit work. Keep `--precision=double` available for
diagnostics, and let `--precision=float` explicitly request the compact path.
The normal automatic mode should choose an appropriate path from the workload.

Run `./build.sh /tmp/burst` to build, then `/tmp/burst 4 200000`. Arguments are
batch count and values per row. The output reports every row score, checksum,
elapsed processing time, arithmetic mode, and live buffer bytes. The evaluator
also sends different shapes and both explicit precision requests.
