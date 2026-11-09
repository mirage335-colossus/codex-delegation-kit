# Task: reduce unnecessary projection work

Optimize the existing `BlockProjection` path in `tools/triad_dynamic_joint.py` for the supplied low-cardinality workload while preserving returned values, shape, dtype, accepted-input behavior, and all receiver callers. Keep the source change scoped to that file. Do not change the test or workload data.

`fixturedata/projection-workload.json` is a constructed deterministic contract slice for the frozen public projection API. It is not a historical capture or a throughput trace. Inspect the coordinates selected by the existing source for the supplied geometry; the fixture makes no claim about end-to-end runtime gains.

The included existing incremental receiver test exercises the projection caller boundary. The ordinary integration check is:

```sh
cd tests
/tmp/pumpmodem-cleanup-venv/bin/python -B -m unittest test_triad_incremental_receiver.IncrementalReceiverTests.test_batch_equivalence_dft_static_and_ou
```

The private acceptance runner checks projection contracts and compares against the existing NumPy DFT behavior. Preserve all shape and error behavior.
