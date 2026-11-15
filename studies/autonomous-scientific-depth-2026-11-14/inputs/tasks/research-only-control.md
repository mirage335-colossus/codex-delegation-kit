Your assignment in this run is scientific research for the development problem
reproduced below. Make a reusable scientific account the substantive
deliverable. Investigate the full requested scope, using the current
implementation as context and primary evidence to explain mechanisms,
competing approaches, assumptions, contradictions and limits. Perform
informative authorized desk comparisons and connect the findings to the
original problem's development decisions, interfaces and discriminating
checks. Preserve all original constraints. The implementation plan is the
downstream use of this research; a safe first engineering step alone does not
complete the inquiry. Request permitted assistance as useful within the
supplied envelope.

## Downstream problem

# Development request

Prepare an implementation-ready improvement plan for the native three-carrier modem's channel appraisal and receiver. It should support meaningful receiver decisions across:

- Sub-9 kHz links using electrically small antennas and practical coupling alternatives.
- Approximately 1 MHz and 30 MHz groundwave.
- 1–30 MHz skywave, including quiet, changing, high-latitude and disturbed operation.
- Passive Earth–Moon–Earth communication near 5.8 GHz.

Represent received levels, delay/frequency behavior, polarization where relevant, noise and interference, actual front-end limitations, outages, and physically defensible severe conditions. Choose the simplest useful representations and receiver improvements across this envelope, with explicit limits. Explain which existing capabilities to reuse, which additions are worth implementing, and how to distinguish their benefits from model or measurement artifacts.

Begin with the current native implementation and work through the necessary steps before committing to the design. Preserve the canonical C++ modem and continuous receiver, public hypotheses and calendar behavior, and demanding-case complete-receiver capacity. The plan must connect the selected environmental and receiver models to concrete implementation boundaries, observable checks and priority order.
