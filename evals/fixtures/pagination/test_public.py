import unittest
from core import page
class Tests(unittest.TestCase):
    def test_complete_page(self):
        self.assertEqual(page([1,2,3],0,3), [1,2,3])
    def test_beyond_end(self):
        self.assertEqual(page([1],5,2), [])
