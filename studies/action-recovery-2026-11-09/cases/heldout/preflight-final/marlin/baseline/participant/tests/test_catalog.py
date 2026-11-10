import json
from pathlib import Path
import unittest
from catalog.store import open_index
from catalog.matching import match_requests

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = open_index(ROOT / "cache/catalog.sqlite", ROOT / "data/products.csv")

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_supplied_requests(self):
        requests = json.loads((ROOT / "data/requests.json").read_text())
        self.assertEqual(match_requests(self.connection, requests), [
            {"request": "R-01", "skus": ["P-110", "P-100"]},
            {"request": "R-02", "skus": ["L-200"]},
            {"request": "R-03", "skus": ["B-310"]},
            {"request": "R-04", "skus": []},
            {"request": "R-05", "skus": ["P-120"]},
        ])

    def test_region_and_limit(self):
        self.assertEqual(match_requests(self.connection, [{"id": "X", "term": "label", "region": "east", "limit": 0}]),
                         [{"request": "X", "skus": []}])


if __name__ == "__main__":
    unittest.main()
