Removed the cutoff recalculation guards and updated storage reporting in `core.cpp`. The reported totals now include all live numerical arrays; `persistent_storage_bytes` reports the normal mode’s 32,772-byte static LUT explicitly.

The public checks passed. The 4096×2048 production comparison against audit took **0.052658 s** and met sample, aggregate, and threshold-count limits. The reviewer’s existing guard-free max-size and cutoff checks apply; I did not repeat them during this repair.
