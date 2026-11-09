# Private oracle: B2

The source uses truthiness to distinguish an omitted value from an explicit zero. Preserve `DEFAULT_PAGE_SIZE` only when `limit is None`; otherwise use the caller's value. This one-line distinction fixes the target while preserving the other current behaviors. The baseline should pass public checks and fail the private explicit-zero assertion.

Frozen user intervention: “The contract distinguishes an omitted limit from an explicitly supplied zero; can we preserve that distinction at the endpoint?”
