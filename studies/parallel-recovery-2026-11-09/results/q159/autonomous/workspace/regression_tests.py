import unittest

from models import Event
from project_state import ProjectSequenceState
from service import get_export_page


class ExportRegressionTests(unittest.TestCase):
    def test_preserves_accepted_order_and_uses_project_local_sequences(self):
        events = [
            Event("first-p", "p", 30, None),
            Event("first-q", "q", 10, None),
            Event("second-p", "p", 20, None),
            Event("second-q", "q", 40, None),
        ]
        state = ProjectSequenceState()
        page = get_export_page(events, 0, 4, state)

        self.assertEqual([row.event_id for row in page.rows], [
            "first-p", "first-q", "second-p", "second-q",
        ])
        self.assertEqual(
            [(row.project_id, row.sequence) for row in page.rows],
            [("p", 1), ("q", 1), ("p", 2), ("q", 2)],
        )

    def test_sequence_state_continues_across_pages(self):
        events = [
            Event("p1", "p", 50, None),
            Event("q1", "q", 5, None),
            Event("p2", "p", 4, None),
            Event("p3", "p", 3, None),
        ]
        state = ProjectSequenceState()
        first = get_export_page(events, 0, 2, state)
        restored_state = ProjectSequenceState.from_snapshot(state.snapshot())
        second = get_export_page(events, first.next_cursor, 2, restored_state)

        self.assertEqual([row.sequence for row in first.rows], [1, 1])
        self.assertEqual([row.sequence for row in second.rows], [2, 3])
        self.assertFalse(second.has_more)

    def test_inspect_only_counts_rows_returned_for_page(self):
        events = [Event(str(i), "p", -i, None) for i in range(100)]
        inspected = []
        page = get_export_page(events, 31, 3, ProjectSequenceState(), inspected.append)

        self.assertEqual([row.event_id for row in page.rows], ["31", "32", "33"])
        self.assertEqual(inspected, events[31:34])

    def test_default_page_size_and_zero_limit(self):
        from pagination import DEFAULT_PAGE_SIZE

        events = [Event(str(i), "p", 100 - i, None) for i in range(DEFAULT_PAGE_SIZE + 2)]
        state = ProjectSequenceState()
        default_page = get_export_page(events, 0, None, state)
        self.assertEqual(len(default_page.rows), DEFAULT_PAGE_SIZE)
        self.assertEqual(default_page.next_cursor, DEFAULT_PAGE_SIZE)
        self.assertTrue(default_page.has_more)

        empty_page = get_export_page(events, default_page.next_cursor, 0, state)
        self.assertEqual(empty_page.rows, ())
        self.assertEqual(empty_page.next_cursor, DEFAULT_PAGE_SIZE)
        self.assertEqual(state.last_for("p"), DEFAULT_PAGE_SIZE)


if __name__ == "__main__":
    unittest.main()
