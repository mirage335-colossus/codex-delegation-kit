import tempfile
import unittest
from pathlib import Path
from feed import connect, import_lines, validate


class FeedTest(unittest.TestCase):
    def test_validation(self):
        self.assertTrue(validate({"id": 1, "value": "a"}))
        self.assertFalse(validate({"id": "1", "value": "a"}))

    def test_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = connect(Path(tmp) / "feed.sqlite")
            try:
                self.assertEqual(import_lines(['{"id":1,"value":"a"}',
                                               'bad json',
                                               '{"id":2,"value":"b"}'], db), 2)
                self.assertEqual(db.execute("SELECT count(*) FROM records").fetchone()[0], 2)
            finally:
                db.close()

