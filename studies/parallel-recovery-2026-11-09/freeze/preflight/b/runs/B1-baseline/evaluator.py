"""Private deterministic acceptance checks; keep outside participant source."""
from sequence import assign_sequences


def main():
    n = 12000
    events = [(f"event-{i}", f"project-{(i * 37) % 113}") for i in range(n)]
    expected_counts = {}
    expected = []
    for event_id, project in events:
        expected_counts[project] = expected_counts.get(project, 0) + 1
        expected.append((event_id, project, expected_counts[project]))
    inspected = [0]
    def inspect(*_row):
        inspected[0] += 1
    actual = assign_sequences(events, inspect=inspect)
    assert actual == expected, "numbering or row order changed"
    assert inspected[0] <= 3 * n, f"work exceeded linear allowance: {inspected[0]} inspections for {n} rows"
    assert events[0] == ("event-0", "project-0"), "input was mutated"
    print(f"PASS: output matches; {inspected[0]} inspected rows for {n} input rows")

if __name__ == "__main__":
    main()
