# C2 architecture review

## Decision

The short CPU/CUDA fine comparison is useful as a parity check, but it cannot answer whether GPU assistance improves complete receiver throughput on the local 12-thread CPU. The probe acquires on CPU, samples three fine-work strata, and explicitly reports `complete_receiver_qualification=False` and `local_cpu_service_established=False` (`triad_gpu_workload.py:177-201, 236-247`). The next experiment should be one matched, end-to-end receiver run per device on the same representative capture, with all 12 logical threads assigned to the single stream. Include acquisition, failed candidates, setup/recurrent work, and quiet-slot completion; report total wall time and phase timings. Record output/accuracy and work counters alongside timing. This is a bounded architecture check before any broad GPU campaign.

## Concerns

1. **The probed GPU path does not own acquisition or complete work.** `_case_probe` acquires on CPU before iterating devices; its device runs then sample nominal continuation, a maximum transition, and an erasure branch, and parity compares only these records (`triad_gpu_workload.py:177-201`). The report itself disclaims complete qualification (`:241-247`). Predicted outcome: a CUDA fine checkpoint can pass while full CUDA-assisted service is slower or misses setup, acquisition, failure, or finalization costs. **Cheapest decisive check:** matched CPU and CUDA-assisted end-to-end runs on one same-stream capture, with 12 workers and complete-work counters. **Action:** do not extrapolate checkpoint speedup; use this run to decide which stages, if any, merit offload.

2. **The shown fine path keeps substantial work on CPU and repeatedly crosses the device boundary.** Projection and Gram construction use NumPy (`triad_incremental_receiver.py:247-255, 274-282`); projected observations and basis are then converted to device tensors for scoring (`:285-289`). Predicted outcome: CPU projection/Gram and per-block transfers or synchronization may dominate small scoring kernels, erasing GPU gains and consuming CPU capacity. **Cheapest decisive check:** in the same end-to-end run, time projection/basis/Gram, host-to-device preparation, device scoring, and synchronization separately; compare total time with CPU. **Action:** if boundaries dominate, test a small persistent/device-resident per-stream buffer or batched multi-block scoring experiment before scaling the campaign; retain the existing layout if whole-run measurements show net gain.

## Choice to preserve

Preserve the matched-input parity and work-strata discipline, with accumulated likelihood in FP64 and disclosed short-checkpoint limitations (`triad_incremental_receiver.py:283-289`; `triad_gpu_workload.py:242-247`). It helps keep any throughput result tied to equivalent work and accuracy. Keep inputs and raw captures local; no cloud experiment is needed to answer this architecture question.
