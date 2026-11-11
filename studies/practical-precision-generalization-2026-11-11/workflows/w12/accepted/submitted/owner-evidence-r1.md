Updated default sample scaling to use float arithmetic; audit generation remains double precision. The exact timestamp logic and CLI are unchanged.

`python3 -B public_check.py` passed all checks. The 500,000-frame output’s maximum absolute error was `1.8775e-7`; RSS was `3756 KiB`. The reported `0.24 s` is the measured demanding subprocess time, not the full suite duration. Repair evidence sent for independent re-review.
