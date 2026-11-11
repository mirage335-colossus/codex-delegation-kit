**accepted**

Repair round 1 resolves the finding: default sample scaling and interpolation execute in float; audit retains double arithmetic. Assembly confirms this. Exact timestamps, counts, seed handling, and CLI limits remain intact.

Independent validation:

- `python3 -B public_check.py`: all nine checks passed; maximum error `1.8775e-7`, RSS **3,796 KiB**, demanding subprocess time **0.2452 s**.
- Additional maximum-seed full capture: passed, error `1.9125e-7`.
- Maximum-size audit: zero reference error.
- One-frame, exact-period boundary, and invalid-limit/mode checks passed.

Timing wording is corrected. Prior bounded performance evidence remains applicable; no speedup is claimed. Production files were unchanged during review.

Re-review used three tool invocations containing four underlying operations. No remaining acceptance conditions identified within the assigned scope.
