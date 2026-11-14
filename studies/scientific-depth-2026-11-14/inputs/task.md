# Development request

Prepare an implementation-ready improvement plan for the native three-carrier modem's channel appraisal and receiver. It should support meaningful receiver decisions across:

- Sub-9 kHz links using electrically small antennas and practical coupling alternatives.
- Approximately 1 MHz and 30 MHz groundwave.
- 1–30 MHz skywave, including quiet, changing, high-latitude and disturbed operation.
- Passive Earth–Moon–Earth communication near 5.8 GHz.

Represent received levels, delay/frequency behavior, polarization where relevant, noise and interference, actual front-end limitations, outages, and physically defensible severe conditions. Choose the simplest useful representations and receiver improvements across this envelope, with explicit limits. Explain which existing capabilities to reuse, which additions are worth implementing, and how to distinguish their benefits from model or measurement artifacts.

Begin with the current native implementation and work through the necessary steps before committing to the design. Preserve the canonical C++ modem and continuous receiver, public hypotheses and calendar behavior, and demanding-case complete-receiver capacity. The plan must connect the selected environmental and receiver models to concrete implementation boundaries, observable checks and priority order.
