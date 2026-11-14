# NTIA LFMF source and acquisition lessons

The external reference is [NTIA/LFMF revision 57886e9d0a29fd8f04a6416dc3f782322f5a3589](https://github.com/NTIA/LFMF/tree/57886e9d0a29fd8f04a6416dc3f782322f5a3589), committed 2025-01-23. Its source project version is 1.1; the ITU software inventory identifies the P.368 product as version 10. These version identifiers describe different things.

## Access and processing lessons

- The bounded acquisition used 25 read-only GitHub connector calls. Repository identity, the pinned tree and standalone build metadata were checked. No upstream build system, package installation or pumpModem changes were involved.
- An initial artifact-write loop failed with `TextEncoder is not defined`. This was a local serialization failure, not a failed source retrieval; the subsequent unnecessary refetch illustrates why returned content should be reused after a local write failure.
- The ITU ZIP link returned an unsupported-content-type error, a P.368 PDF request timed out, and the documentation site was inaccessible through one tool. These access-path failures did not establish source unavailability: the official repository was accessible through the connector.
- Text serialization added a final LF. Reviewer checks confirmed identical source bodies after accounting for that LF; a claim of byte-for-byte identity would have been inaccurate.
- The first standalone compilation omitted `LIBRARY_NAME` and `LIBRARY_VERSION` and failed before any model call. Using the upstream CMake definitions resolved it. The study used g++ 14.2.0 and C++11.
- Groundwave web accounting reached 78/140 operations. Error-shaped responses returned normally through the meter and must still be classified as access failures.

## Calculation evidence

The original callers and text outputs under `tmp/LFMF/` document the inputs and conditional model results. They are research evidence, not a self-contained build or a measured path qualification. Any new execution requires a separately obtained, appropriately licensed external implementation. The scientific interpretations and transfer limits are in [chapter.md](chapter.md) and [source-ledger.md](source-ledger.md).
