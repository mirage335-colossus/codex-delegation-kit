import unittest

from models import Event
from project_state import ProjectSequenceState
from service import get_export_page


class ExportRegressionTests(unittest.TestCase):
    def test_accepted_order_project_sequences_and_page_work(self):
        events = [
            Event("z", "p", 30, "first p"),
            Event("a", "q", 10, "first q"),
            Event("b", "p", 20, "second p"),
            Event("y", "q", 40, "second q"),
            Event("c", "p", 5, "third p"),
        ]
        state = ProjectSequenceState()
        examined = []

        first = get_export_page(events, 0, 2, state, inspect=examined.append)
        self.assertEqual([row.event_id for row in first.rows], ["z", "a"])
        self.assertEqual([row.sequence for row in first.rows], [1, 1])
        self.assertEqual(examined, events[:2])
        self.assertEqual((first.next_cursor, first.has_more), (2, True))

        examined.clear()
        second = get_export_page(events, first.next_cursor, 2, state, inspect=examined.append)
        self.assertEqual([row.event_id for row in second.rows], ["b", "y"])
        self.assertEqual([row.sequence for row in second.rows], [2, 2])
        self.assertEqual(examined, events[2:4])
        self.assertEqual((second.next_cursor, second.has_more), (4, True))

        third = get_export_page(events, second.next_cursor, 2, state, inspect=examined.append)
        self.assertEqual([row.event_id for row in third.rows], ["c"])
        self.assertEqual([row.sequence for row in third.rows], [3])
        self.assertEqual((third.next_cursor, third.has_more), (5, False))
        self.assertEqual(len(examined), 3)

    def test_state_snapshot_continues_sequences(self):
        events = [Event("a", "p", 2, None), Event("b", "p", 1, None)]
        state = ProjectSequenceState()
        first = get_export_page(events, 0, 1, state)
        restored = ProjectSequenceState.from_snapshot(state.snapshot())
        second = get_export_page(events, first.next_cursor, 1, restored)
        self.assertEqual([row.sequence for row in second.rows], [2])

    def test_large_interleaved_batch_examines_only_requested_rows(self):
        events = [
            Event(f"id-{i}", f"project-{i % 16}", 4095 - i, i)
            for i in range(4096)
        ]
        state = ProjectSequenceState()
        examined = []
        cursor = 0
        page_size = 128

        for page_number in range(3):
            examined.clear()
            page = get_export_page(events, cursor, page_size, state, inspect=examined.append)
            offset = page_number * page_size
            self.assertEqual([row.event_id for row in page.rows],
                             [f"id-{i}" for i in range(offset, offset + page_size)])
            self.assertEqual([row.sequence for row in page.rows],
                             [i // 16 + 1 for i in range(offset, offset + page_size)])
            self.assertEqual(len(examined), page_size)
            self.assertEqual(examined, events[offset:offset + page_size])
            cursor = page.next_cursor


if __name__ == "__main__":
    unittest.main()
