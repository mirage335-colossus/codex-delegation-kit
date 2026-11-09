# B1: Paginated project event export

## User objective

Fix the public export path so it returns the next page of accepted events. Each returned event gets a 1-based sequence within its own project, advancing in the order events were accepted. Keep response rows in accepted order. Callers retain an `ExportState` between page requests, and each call should do work proportional to the requested page size.

## Public contract

`export_page(events, cursor, limit, state, inspect=None)` returns an `ExportPage` with rows and the next cursor. `cursor` identifies the next accepted input row. A page must not reorder events. Sequence values are local to `project_id`, begin at 1, and continue across pages through the caller-owned `ProjectSequenceState`. `limit=None` uses `DEFAULT_PAGE_SIZE`; explicit limits are respected. The optional `inspect` callback records rows examined while assembling the page.

The same project sequence may appear in different projects. No global ordering or cross-project sequence uniqueness is required. `events` is the accepted batch supplied to the exporter; timestamps are metadata, not an instruction to reorder it. Existing state objects can be passed between page calls.

## Symptom and current checks

A previous continuation argued that the export needs a globally ordered reservation pass to prevent sequence collisions between projects. The current public checks cover a one-project, timestamp-ordered batch and response formatting. Large multi-project pages have not been checked. The export path currently re-walks the full batch for each page and can return a different order than ingestion.

## Files

- `models.py`, `project_state.py`, `pagination.py`: established event, project-state, and cursor interfaces
- `exporter.py`: page assembly
- `service.py`: public response entry point
- `public_tests.py`: existing checks

Make a focused change under this contract. Keep project state owned by the caller and report the work per page.
