# Native research harness implementation reference

These `.txt` files preserve the kit-authored native lifecycle, access-profile,
archival implementation and synthetic test design for future feature work.
Historical source snapshots, project fixtures, acquisitions and execution records
have been removed. Paths and hashes inside these references describe the old
experiments and are not current runnable inputs.

The files are reference source rather than an executable test suite. Future work
should adapt the needed mechanisms to fresh synthetic fixtures and the then-current
tool/runtime interface. In particular, preserve the lesson that an instruction to
use a mailbox does not disable a separately exposed native web tool. A started
request is not proof of completed acquisition, metering or cancellation.

The smaller self-contained review aggregator, research meter and relay remain
under `../tools/`. Their existing synthetic tests can run without old experiment
data. No live model session or research campaign is needed to check those helpers.
