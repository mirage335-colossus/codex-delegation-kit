**changes_required — one storage-accounting correction remains.**

The numerical repair is accepted: both cutoff guards are removed, and its arithmetic matches the previously qualified guard-free variant. Public checks pass. Independent production timing was **0.050119 s**; sample, mean, and squared-mean errors were `9.334e-8`, `4.699e-8`, and `2.995e-7`, with zero threshold-count difference.

Normal storage now correctly reports **33,636 bytes**, including **32,772 persistent bytes**. Audit still reports `896` total and `0` persistent, although the static LUT remains reserved for the entire process. `nm -S` confirms `_ZZL8run_fastiiiE5table` occupies `0x8004` (32,772) BSS bytes in the executable. This establishes reserved storage, not resident-page usage.

Resolve the existing accounting finding by either:

- Including the persistent LUT in audit reporting: **33,668 total; 32,772 persistent**, or
- Giving the LUT automatic/dynamic lifetime restricted to normal processing, then reporting that actual lifetime accurately.

Also update the stale comment at lines 41–43, which still describes the removed cutoff recalculation.

Executed: public checks, prescribed native build, source comparison against the earlier qualified variant, symbol inspection, and production accuracy/timing comparison. Evidence: `review-scratch/round2/results.json`. Earlier maximum-size and cutoff coverage remains applicable because numerical code is unchanged. No production files modified.
