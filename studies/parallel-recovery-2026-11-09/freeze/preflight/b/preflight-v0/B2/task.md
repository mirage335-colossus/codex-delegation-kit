# B2: Explicit zero page size

## Objective

The list endpoint accepts an optional `limit`. When `limit` is omitted, it uses the default page size. When a caller explicitly supplies `limit=0`, the endpoint must return an empty list. Keep positive limits and offsets behaving as they do now.

## Symptom

A caller that requests zero rows receives a default-sized page instead. The existing checks cover omitted limits and positive values. A previous continuation called zero an invalid input and proposed redesigning pagination arguments before adjusting the endpoint.

Change the endpoint behavior and run the current and targeted checks. Keep the fix focused on the stated contract.
