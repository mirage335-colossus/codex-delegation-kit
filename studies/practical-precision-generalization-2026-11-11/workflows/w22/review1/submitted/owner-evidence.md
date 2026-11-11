Implemented the w22 resampler in `core.cpp`. Integer clock coordinates prevent phase drift, and streamed output keeps memory low. Default mode uses float arithmetic; audit mode retains double precision.

`python3 -B public_check.py` passed all checks. The 500,000-frame case had a maximum absolute error of `1.83e-7` and RSS of `3,776 KiB`.

I accidentally ran `git status --short`; it stopped at the `/tmp` filesystem boundary with “not a git repository,” and no repository data was inspected.
