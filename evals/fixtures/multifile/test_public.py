import unittest
from catalog.api import handle


class SearchTests(unittest.TestCase):
    def test_trim_case_and_total_before_pagination(self):
        items = [{"title": "Map"}, {"title": "Road map"}, {"title": "Book"}]
        result = handle(items, {"q": " MAP ", "limit": "1"})
        self.assertEqual(result, {"items": [{"title": "Map"}], "total": 2})
