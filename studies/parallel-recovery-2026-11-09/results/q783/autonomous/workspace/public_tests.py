import unittest
from models import Event
from project_state import ProjectSequenceState
from service import get_export_page, response_body


class ExportPublicTests(unittest.TestCase):
    def test_single_project_timestamp_ordered_batch(self):
        events = [Event("a", "p", 1, {"v": 1}), Event("b", "p", 2, {"v": 2})]
        page = get_export_page(events, 0, 2, ProjectSequenceState())
        body = response_body(page)
        self.assertEqual([r["sequence"] for r in body["rows"]], [1, 2])
        self.assertEqual([r["event_id"] for r in body["rows"]], ["a", "b"])
        self.assertEqual((body["next_cursor"], body["has_more"]), (2, False))
        self.assertEqual(body["rows"][0]["payload"], {"v": 1})

    def test_default_page_size_and_cursor_validation(self):
        from pagination import DEFAULT_PAGE_SIZE, page_bounds
        self.assertEqual(page_bounds(DEFAULT_PAGE_SIZE + 1, 0, None), (0, DEFAULT_PAGE_SIZE))
        with self.assertRaises(ValueError):
            page_bounds(4, -1, 2)

    def test_empty_batch_response(self):
        page = get_export_page([], 0, 10, ProjectSequenceState())
        self.assertEqual(response_body(page), {"rows": [], "next_cursor": 0, "has_more": False})


if __name__ == "__main__":
    unittest.main()
