# Facilitator oracle (keep outside participant source)

## Mechanism

`SnapshotLoader` uses the capture timestamp as the entire cache key. Two distinct service files from the same capture batch therefore collide. The second `load()` returns the first service's normalized snapshot. The visible output depends on which file sorts first. State and time normalization are correct; sorting can't restore the discarded service boundary.

## Small discriminating experiment

In one Python process, load the api snapshot and then worker snapshot. Both have the same capture timestamp. Print the two returned `service` values. Baseline returns `api`, `api`; reversing load order returns `worker`, `worker`. This establishes order-dependent cross-service reuse before investigating selection policy.

## Minimal witness correction

In `source/loader.py`, make the cache identity include the source path (resolved path is suitable) as well as the capture timestamp, so repeat reads of one file remain cached and separate service files do not collide. The evaluator runs the actual documented CLI over both files.

## User intervention to inject

“Before changing another normalization or sort rule, can you test whether reading the two service files in opposite orders changes which records appear?”
