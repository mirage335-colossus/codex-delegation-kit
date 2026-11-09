"""Private deterministic acceptance checks; separate from participant source."""
from models import Event
from project_state import ProjectSequenceState
from service import get_export_page, response_body


class CountedBatch:
    """Sequence wrapper that counts reads independently of source callbacks."""
    def __init__(self, items):
        self._items = items
        self.reads = 0
    def __len__(self):
        return len(self._items)
    def __getitem__(self, index):
        value = self._items[index]
        self.reads += len(value) if isinstance(index, slice) else 1
        return value


def main():
    n, page_size = 2400, 40
    events = [Event(f"ev-{i}", f"project-{(i * 17) % 19}", (i * 97) % n, i) for i in range(n)]
    batch = CountedBatch(events)
    state = ProjectSequenceState()
    counts = {}
    expected = []
    inspected_total = 0
    failures = []
    for start in range(0, n, page_size):
        inspected = [0]
        def inspect(_event):
            inspected[0] += 1
        reads_before = batch.reads
        page = get_export_page(batch, start, page_size, state, inspect=inspect)
        independent_reads = batch.reads - reads_before
        body = response_body(page)
        expected_page = []
        for event in events[start:start + page_size]:
            counts[event.project_id] = counts.get(event.project_id, 0) + 1
            expected_page.append({"event_id": event.event_id, "project_id": event.project_id,
                                  "sequence": counts[event.project_id], "payload": event.payload})
        if body["rows"] != expected_page:
            failures.append(f"accepted order/project sequence mismatch at cursor {start}")
        if body["next_cursor"] != min(start + page_size, n) or body["has_more"] != (start + page_size < n):
            failures.append(f"cursor metadata mismatch at cursor {start}")
        if independent_reads > 2 * len(expected_page):
            failures.append(f"independent input-read bound exceeded at cursor {start}: {independent_reads} reads for {len(expected_page)} outputs")
        if inspected[0] > 2 * len(expected_page):
            failures.append(f"callback work bound exceeded at cursor {start}: {inspected[0]} inspections")
        inspected_total += independent_reads
    if state.snapshot() != counts:
        failures.append("caller-owned state did not retain per-project sequences")
    if inspected_total > 2 * n:
        failures.append(f"aggregate independent read bound exceeded: {inspected_total} for {n} accepted rows")
    if failures:
        raise AssertionError("; ".join(failures[:3]))
    print(f"PASS: {n} accepted rows across pages; {inspected_total} independently counted reads; state and response match")

if __name__ == "__main__":
    main()
