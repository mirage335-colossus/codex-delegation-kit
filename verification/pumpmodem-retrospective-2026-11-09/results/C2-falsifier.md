# C2 executable-falsifier review

## Concrete concerns

1. **A CUDA fine pass may still be dominated by host work and transfer.** In `_score_block`, the observation and basis go through `projection.numpy` (lines 250/278); the Gram matrix is built by NumPy `einsum` (281–282), then wrapped as a Torch tensor (289). Basis generation also enters through a NumPy callback (274). CUDA therefore appears to accelerate only the correlation expression at 288 (plus later Torch work not shown); the excerpts do not establish the fraction of complete fine-checkpoint time spent there. This is an architecture hypothesis, not a measured defect. **Cheapest decisive check:** on one representative prepared block, time basis generation, projection, Gram/einsum, host-to-device conversion, correlation, and synchronized end-to-end `_score_block` separately for CPU and CUDA on identical inputs; compare the actual work counters and scores too. If host stages/transfers dominate or synchronized CUDA end-to-end time fails the useful-speedup threshold, stop the full GPU campaign and first test moving/fusing the dominant work. Do not infer speed from kernel time alone.

2. **The probe’s positive result cannot establish the requested service capacity.** `run_probe` always performs acquisition with a CPU receiver (177–183), then compares only the three short fine strata (190–202); its own report hard-codes `local_cpu_service_established=False` and `complete_receiver_qualification=False` (241), and the success label is only `short_fine_work_parity_observed` (274–276). The packet’s user target includes complete receiver work and productive use of 12 logical CPU threads in one stream. **Cheapest decisive check before any broad campaign:** after the one-block architecture check above passes, run one matched end-to-end receiver capture on the local CPU at the intended 12-thread allocation, including acquisition and completion, while recording wall time, stage timings, thread allocation/utilization, and the complete work counters. If this does not demonstrate the target service rate with coverage intact, fine parity does not justify a GPU campaign; revise the CPU/GPU division or scope first.

## Choice worth preserving

Keep the probe’s explicit status boundary and same-row CPU/CUDA parity comparison. It synchronizes the selected device in the comparison path (223) and reports short fine parity without claiming receiver qualification. That is a useful, inexpensive correctness gate; retain it as a gate, not as throughput evidence.

## Limits

No executable, timing, GPU, numerical, or full-receiver check was run; this is a source-based falsifier plan from the supplied excerpts only. No actual defect is established.
