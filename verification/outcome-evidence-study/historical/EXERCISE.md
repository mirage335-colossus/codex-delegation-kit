# Exercise context

This is a selective source snapshot of pumpModem commit c578659143f400b7a56f444d4d9773b5a813394b. Non-Markdown documentation assets, web content, validation datasets and other unrelated material are excluded. It has no Git metadata and is not the live project. The Python environment at `/tmp/pumpmodem-cleanup-venv/bin/python` has NumPy, SciPy, PyTorch CPU and threadpoolctl. CMake build feasibility for this selective copy has not been established. Work only within this copy.

## Task

Please add to the computationally efficient Robust Modem abbreviated test suite, using the same approach to test the configurations in `_tests-RobustModem.md`. The list is manually edited and the updated list should always be used. Document prominently for development agents and implement plausible estimates from brief simulation of CPU ceiling and DSP workspace margins.

Report sustained processing time after preparation as seconds the computer uses its CPU threads at high utilization per second of received baseband, in the context of this computer. One second per second has no obvious margin; 0.1 seconds per second suggests 90% real-time margin. Actually measure this in simulation. Receiver development may be needed if the receiver capability does not yet cover the selected configurations.

Also report Helper carrier SNR (when used) and triple Robust Modem SNR in dB/1Hz, an approximate target SNR for greater than 90% success probability, the single-bit and literal `fox` message transmit times, and whether more than reasonably short receiver preparation before transmission was unavoidable.
