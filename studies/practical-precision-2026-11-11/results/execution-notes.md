# Retained execution notes

The t01 worker reported five tool invocations. Its initial command was:

```sh
python3 -B - <<'PY'
from studies.practical_precision_2026_11_11.transfer.t01.selector import select_route
PY
```

It failed with `ModuleNotFoundError: No module named 'studies.practical_precision_2026_11_11'`
before assertions (zero assertions). The assigned directory uses hyphens. The
same worker corrected its check to load the actual file with
`importlib.util.spec_from_file_location`; five assertions passed, covering capacity
versus idle latency, precision and error limits, no eligible route, memory and
input preservation. Its selector was not repaired after hidden evaluation.
The original inline corrected script was not separately saved; the protected
evaluator and executed result are retained for independent reproduction.

The t02 worker wrote `transfer/t02/check.py` and reported
`python3 -B check.py` passing. It checked the chosen balancing rule, precision and
error constraints, exclusions, zero latency and input preservation. The original
balancing implementation is retained; it was not repaired after inspection.

Budget compliance beyond visible reports is not independently audited. No token,
quota, active-time, resolved model or cost measurements are claimed. Both arms used
the same requested pinned settings, action allowance and tool families.

Outside the behavioral experiments, the prompt-delivery worker initially tried
the unavailable `python` executable. It used `python3` and passed its checks.
The main agent also had one failed patch-context match that made no file change.
Neither setup failure is a failed behavioral assertion or an erased test result.
