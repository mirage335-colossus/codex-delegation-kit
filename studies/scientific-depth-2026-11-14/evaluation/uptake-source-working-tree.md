# Live source evidence for uptake

The accompanying [patch snapshot](uptake-source-working-tree.patch) preserves the two concurrent pumpModem working-tree edits inspected by the fresh owner and reviewer at HEAD `42798a98bdc0bae32387870ec4aa55179798974c`. This exercise did not author or apply those edits. The snapshot makes the examined source state recoverable after the other work continues.

Before capture, both live files matched the owner's recorded Git blob identities:

- `src/triad_receiver.cpp`: `cddce9bc2b7291bda566abb569cd04a46e0eca5a`
- `src/triad_receiver_driver.hpp`: `1072cc242983e79a2e192e21171b0b7e043ec702`

The 7,190-byte two-path diff has SHA-256 `8f741175ac7d7a2859c14da9fbdf550ea310caf2669cfb53cf76df4aea521c37`, matching the earlier [independent identity follow-up](source-identity-followup.md). The [owner's verification](../results/uptake-checks/verification.txt) records other consequential source identities, actual permitted checks and limits. The scientific/input freeze remains unchanged; the initially recorded one-file dirty status and this later two-file snapshot are different observations in time.
