# Private oracle: B1

The exported contract is explicit: accepted order is the stable row order, and sequence ownership is per project across pages. The baseline builds and sorts the whole batch on every request, assigning global positions; this both changes interleaved accepted order and does unnecessary full-batch work. The existing `ProjectSequenceState.next_for(project_id)` API is the incremental mechanism. A witness can use `page_bounds` to select the requested accepted-order slice, call `state.next_for` for each selected event, preserve payloads and response shape, and count only page events as inspected. The evaluator allows at most 2N inspections over the full run.

Frozen user intervention: “The contract says the cursor follows accepted order and state is already retained per caller; could each page advance the existing sequence state only for the rows it returns?”
