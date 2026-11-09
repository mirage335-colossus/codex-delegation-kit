import unittest

from models import Event
from project_state import ProjectSequenceState
from service import get_export_page


class ExportRegressionTests(unittest.TestCase):
    def test_accepted_order_project_sequences_and_page_sized_inspection(self):
        events = [
            Event("a", "p", 9, 1),
            Event("b", "q", 1, 2),
            Event("c", "p", 0, 3),
            Event("d", "q", 8, 4),
            Event("e", "p", 2, 5),
        ]
        state = ProjectSequenceState()
        inspected = []
        first = get_export_page(events, 0, 2, state, inspected.append)
        second = get_export_page(events, first.next_cursor, 2, state, inspected.append)
        third = get_export_page(events, second.next_cursor, 2, state, inspected.append)

        self.assertEqual([r.event_id for r in first.rows + second.rows + third.rows],
                         ["a", "b", "c", "d", "e"])
        self.assertEqual([r.sequence for r in first.rows + second.rows + third.rows],
                         [1, 1, 2, 2, 3])
        self.assertEqual([r.project_id for r in first.rows + second.rows + third.rows],
                         ["p", "q", "p", "q", "p"])
        self.assertEqual([e.event_id for e in inspected], ["a", "b", "c", "d", "e"])
        self.assertEqual([(p.next_cursor, p.has_more) for p in (first, second, third)],
                         [(2, True), (4, True), (5, False)])

    def test_zero_limit_and_cursor_past_end_do_no_inspection_or_state_advance(self):
        events = [Event("a", "p", 1, None)]
        state = ProjectSequenceState()
        inspected = []
        empty = get_export_page(events, 0, 0, state, inspected.append)
        past_end = get_export_page(events, 9, 2, state, inspected.append)
        self.assertEqual((empty.rows, empty.next_cursor, empty.has_more), ((), 0, True))
        self.assertEqual((past_end.rows, past_end.next_cursor, past_end.has_more), ((), 1, False))
        self.assertEqual(inspected, [])
        self.assertEqual(state.last_for("p"), 0)


if __name__ == "__main__":
    unittest.main()
