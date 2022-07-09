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


#class HTTPServerTestCase(unittest.TestCase):

def assertEqualUnorderedDicts(dict1, dict2):
    if dict1.keys() == dict2.keys():
        return False