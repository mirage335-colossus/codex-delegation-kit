# Simulate heat spreading across a plate

Implement the explicit four-neighbor heat update for a rectangular plate. The perimeter is held at the initial boundary temperature; interior cells evolve for the requested number of steps.

The production plate is 1024×512 for 160 steps. Peak bulk field storage must be at most **5 MiB**. Against a double-reference simulation, the six reported field samples must be within **3e-4 absolute**. Retain correct edge behavior and all requested updates. The public probe offers a smaller quick case and checks 16 partitioned sum/square checksums covering every final field cell. Timing is recorded for context; quality and storage are the acceptance gates.

Build and run `python3 public/check.py [path-to-core.cpp]`.
