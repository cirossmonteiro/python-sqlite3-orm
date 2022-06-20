import os
import sqlite3
import unittest

import sql_database as sql


def remove_extra_space(s):
    s = ' '.join(s.split())
    return s


def assertEqualStringQueries(self, first, second, msg=None):
    """
    Compare two query strings
    """
    self.assertEqual(
        remove_extra_space(first),
        remove_extra_space(second),
        msg
    )


# custom assertion
unittest.TestCase.assertEqualStringQueries = assertEqualStringQueries


class TestSQLTable(unittest.TestCase):

    def setUp(self):
        self.filename = 'test.db'
        self.tablename = 'test'
        self.db = sql.SQLDatabase(self.filename)
        self.cursor = self.db.cursor
        self.schema = {
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        }
        self.instance = sql.SQLTable(self.cursor, self.tablename, self.schema)

    def tearDown(self):
        os.remove(self.filename)

    def test_init(self):
        self.assertIsInstance(self.instance.cursor, sqlite3.Cursor)
        self.assertIsInstance(self.instance, sql.SQLTable)

    def test_query_create_table(self):
        self.assertEqualStringQueries(
            self.instance._query_create_table(self.schema),
            f"""
                CREATE TABLE {self.tablename}
                (
                    number_integer INTEGER ,
                    number_float REAL ,
                    number_numeric REAL ,
                    string_text TEXT
                )
            """
        )


class TestSQLDatabase(unittest.TestCase):

    def setUp(self):
        self.filename = 'test.db'
        self.tablename = 'test'
        self.schema = {
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        }
        self.instance = sql.SQLDatabase(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    def test_init(self):
        self.assertEqual(self.instance.filename, self.filename)
        self.assertIsInstance(self.instance, sql.SQLDatabase)
        self.assertIsInstance(self.instance.cursor, sqlite3.Cursor)

    def test_table(self):
        self.assertFalse(self.instance.table_exists(self.tablename))
        self.instance[self.tablename] = self.schema
        self.assertTrue(self.instance.table_exists(self.tablename))

        # error - when table already exists
        with self.assertRaises(sqlite3.OperationalError) as error:    
            self.instance.create_table(self.tablename, self.schema)
        self.assertEqual(str(error.exception), f"table {self.tablename} already exists")

        self.assertIsInstance(self.instance[self.tablename], sql.SQLTable)            


if __name__ == '__main__':
    unittest.main()
