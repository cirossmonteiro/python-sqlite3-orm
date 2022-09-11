import os
import unittest

import sql

def remove_extra_space(s):
    s = ' '.join(s.split())
    return s


class TestCase(unittest.TestCase):
    setUpExtra = None

    def setUp(self):
        self.filename = 'test.db'
        self.db = sql.SQLDatabase(self.filename)
        if self.setUpExtra is not None:
            self.setUpExtra()
            
    
    def tearDown(self):
        os.remove(self.filename)

    def assertEqualStringQueries(self, first, second, msg=None):
        """
        Compare two query strings
        """
        self.assertEqual(
            remove_extra_space(first),
            remove_extra_space(second),
            msg
        )

    def assertEqualUnorderedDicts(self, first: dict, second: dict, msg=None):
        self.assertEqual(first.keys(), second.keys(), msg)
        for key in first.keys():
            self.assertEqual(first[key], second[key], msg)
        
            


#class HTTPServerTestCase(unittest.TestCase):

