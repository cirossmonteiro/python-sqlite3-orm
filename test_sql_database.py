import os
import sqlite3
import unittest

import sql_database as sql
from utils_test import TestCase


class TestSQLTableSlice(TestCase):

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
        self.rows = [
            {
                'number_integer': n,
                'number_float': n+0.1,
                'number_numeric': n+0.2,
                'string_text': f'Hello, x-{n} world!'
            }
            for n in range(10)
        ]
        self.table = sql.SQLTable(self.cursor, self.tablename, self.schema)
        self.table.insert_into(self.rows)
        self.indexes = {
            'one': 0,
            'start': 1,
            'stop': 6
        }

    def tearDown(self):
        os.remove(self.filename)
    
    def test_init(self):
        slice1 = self.table[self.indexes['one']]
        self.assertIsInstance(slice1, sql.SQLTableSlice)
        self.assertEqual(slice1.values(), [tuple(self.rows[self.indexes['one']].values())])

        slice2 = self.table[self.indexes['start']:self.indexes['stop']]
        self.assertIsInstance(slice2, sql.SQLTableSlice)
        self.assertEqual(slice2.values(), [tuple(self.rows[n].values()) for n in range(self.indexes['start'], self.indexes['stop'])])

    

class TestSQLTable(TestCase):

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
        self.row = {
                    'number_integer': 1,
                    'number_float': 2.1,
                    'number_numeric': 2.2,
                    'string_text': 'Hello, world!'
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
                );
            """
        )

        # testing SQLTable._load_schema()
        new_instance = sql.SQLTable(self.cursor, self.tablename)
        self.assertEqual(self.instance.schema, new_instance.schema)

    def test_insert_select(self):
        self.assertEqualStringQueries(
            self.instance._query_insert_into([
                self.row
            ]),
            f"""
                INSERT INTO {self.tablename} VALUES
                (1 , 2.1 , 2.2 , 'Hello, world!');
            """
        )
        self.instance.insert_into([self.row, self.row])
        self.assertEqual(self.instance.select(2), [tuple(self.row.values()), tuple(self.row.values())])

        


class TestSQLDatabase(TestCase):

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
