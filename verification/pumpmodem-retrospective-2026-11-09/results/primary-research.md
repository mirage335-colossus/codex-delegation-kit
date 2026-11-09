# Primary-source research: pumpModem retrospective

**Sources read:** 2026-11-09. This note records source-based principles and proposed falsifiers; it contains no project measurements or executed checks.

## Findings and cheap falsifiers

1. **Compare complete CPU and GPU paths.** NVIDIA's CUDA C++ Best Practices Guide recommends minimizing host/device transfers, keeping intermediate data on the device, and batching small transfers even when packing is needed. A GPU kernel may be useful despite not beating the CPU for an isolated operation if it avoids transfers elsewhere in the pipeline.
   - **Falsifier:** On identical representative inputs, time an already-resident kernel, H2D + kernel + D2H, and the complete receive-to-result path. Report these separately.
   - Source: [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) (guide page identifies release 13.4; transfer principle is general, while its bandwidth examples are hardware-specific).

2. **Test actual matrix shapes and packing costs.** NVIDIA's matrix multiplication guide explains that small GEMMs can underuse GPU tiles or have too little parallelism. Tensor Core performance depends on dimensions, alignment, data type, and library version; its guidance distinguishes older cuBLAS releases from cuBLAS 11.0 and later.
   - **Falsifier:** Sweep the observed M/N/K sizes, batch sizes, dtypes, strides/alignment, and packing cost. Do not infer application speed from peak FLOPS.
   - Sources: [NVIDIA matrix multiplication performance guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html); [cuBLAS 13.0 documentation](https://docs.nvidia.com/cuda/archive/13.0.0/cublas/index.html) (documents Tensor Core selection and alignment conditions).

3. **Check algorithm choice before accelerating the current algorithm.** FFTW documents O(N log N) algorithms for DFTs of arbitrary lengths, with small-factor lengths generally more efficient. Its pruned-FFT note says reductions for selected outputs can be modest and are not guaranteed to translate into speedups.
   - **Falsifier:** For representative lengths and requested bins, compare the current dense DFT, a full FFT plus selection, and a pruned or specialized method. Check identical output and tolerance, then compare complete receiver cost.
   - Sources: [FFTW 3.3.10 manual](https://fftw.org/fftw3.pdf); [FFTW pruned FFT note](https://ftp.fftw.org/pruned.html).

4. **Bound CPU parallelism under receiver load.** PyTorch's multiprocessing guidance warns that CPU oversubscription can lower efficiency and gives `floor(N/M)` as a general per-process thread guideline for N CPU cores and M processes. Treat this as a starting point, especially if BLAS or OpenMP also creates threads.
   - **Falsifier:** Under the same concurrent receiver load, compare a single-process path with a small grid of process/thread counts. Measure completed throughput and latency.
   - Source: [PyTorch multiprocessing best practices](https://docs.pytorch.org/docs/stable/notes/multiprocessing.html) (the precise heuristic is framework guidance; oversubscription is the broader principle).

5. **Measure elapsed time and CPU use; synchronize GPU timing.** Python documents `perf_counter()` as elapsed time including sleep and `process_time()` as current-process user + system CPU time excluding sleep. `process_time()` is not aggregate CPU time across child processes. CUDA work is asynchronous: NVIDIA documents CUDA events for stream-operation timing and synchronization for accurate CPU-timer measurements.
   - **Falsifier:** For matched repeated receiver workloads, record wall time, CPU time (including worker CPU separately when applicable), synchronized event kernel time, and transfer/setup components. A host timer around an unsynchronized launch is not a kernel measurement.
   - Sources: [Python `time` documentation](https://docs.python.org/3/library/time.html) (source result identified Python 3.15.2); [CUDA C++ Best Practices Guide, timing section](https://docs.nvidia.com/cuda/archive/12.6.1/cuda-c-best-practices-guide/index.html).

6. **Keep final predictor validation independent of tuning.** Scikit-learn's validation guidance warns that repeatedly selecting models or settings using test results leaks information and makes generalization estimates optimistic. Applying that principle to GPU-to-CPU runtime prediction, reserve an untouched set for final evaluation; if extrapolating across workload families, hold out meaningful groups such as sizes or receiver configurations.
   - **Falsifier:** Choose the prediction rule or dispatch threshold using a development split, then report prediction errors and dispatch decisions on locked, unseen cases. Do not retune against the final set.
   - Source: [scikit-learn cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html) (source result identified documentation version 1.9.1; validation methodology applies independently of library use).

## Limits and counterexamples

These references motivate experiments; they do not establish pumpModem performance. GPU acceleration can still win end-to-end when keeping intermediates resident avoids transfers, even if an individual operation is slower. A full FFT may waste work when only a few DFT outputs are needed, so compare it with pruned/specialized options rather than presuming it wins. No project checks were run for this research note.
