import unittest
from core import get_document
class Tests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(get_document({},'alice','x'), (404, {'error':'not_found'}))
    def test_owner(self):
        status,body=get_document({'d':{'id':'d','owner_id':'alice','title':'Hi'}},'alice','d')
        self.assertEqual(status,200)
        self.assertEqual(body['title'],'Hi')
