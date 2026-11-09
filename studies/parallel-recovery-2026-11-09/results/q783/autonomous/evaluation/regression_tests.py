import unittest

from models import Event
from project_state import ProjectSequenceState
from service import get_export_page


class ExportRegressionTests(unittest.TestCase):
    def test_preserves_accepted_order_not_timestamp_order(self):
        events = [
            Event("later", "p", 20, None),
            Event("earlier", "p", 10, None),
            Event("other", "q", 5, None),
        ]
        page = get_export_page(events, 0, 3, ProjectSequenceState())
        self.assertEqual([r.event_id for r in page.rows], ["later", "earlier", "other"])
        self.assertEqual([r.sequence for r in page.rows], [1, 2, 1])

    def test_sequences_continue_across_pages_and_are_project_local(self):
        events = [
            Event("a", "p", 3, None),
            Event("b", "q", 2, None),
            Event("c", "p", 1, None),
            Event("d", "q", 0, None),
        ]
        state = ProjectSequenceState()
        first = get_export_page(events, 0, 2, state)
        second = get_export_page(events, first.next_cursor, 2, state)
        self.assertEqual([r.sequence for r in first.rows], [1, 1])
        self.assertEqual([r.sequence for r in second.rows], [2, 2])
        self.assertEqual(state.snapshot(), {"p": 2, "q": 2})

    def test_inspect_only_visits_rows_returned_on_page(self):
        events = [Event(str(i), "p", 100 - i, None) for i in range(8)]
        inspected = []
        page = get_export_page(events, 3, 2, ProjectSequenceState(), inspect=inspected.append)
        self.assertEqual([e.event_id for e in inspected], ["3", "4"])
        self.assertEqual([r.event_id for r in page.rows], ["3", "4"])
        self.assertEqual((page.next_cursor, page.has_more), (5, True))


if __name__ == "__main__":
    unittest.main()
