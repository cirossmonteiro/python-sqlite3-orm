import os
import sqlite3

from schema import Schema
from test_commons import TestCase
import sql

class TestSQLDatabase(TestCase):
    
    def setUpExtra(self):
        self.tablename = 'test'
        self.schema = Schema(schema={
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        })

    def test_init(self):
        self.assertEqual(self.db.filename, self.filename)
        self.assertIsInstance(self.db, sql.SQLDatabase)
        
        #self.assertIsInstance(self.db.cursor, sqlite3.Cursor)

    def test_table(self):
        self.assertFalse(self.db.table_exists(self.tablename))
        self.db[self.tablename] = self.schema
        self.assertTrue(self.db.table_exists(self.tablename))

        # error - when table already exists
        # with self.assertRaises(sqlite3.OperationalError) as error:    
        #     sql.SQLTable(self.db, tablename=self.tablename, schema=self.schema)
        #     #self.db.create_table(self.tablename, self.schema)
        # self.assertEqual(str(error.exception), f"table {self.tablename} already exists")

        self.assertIsInstance(self.db[self.tablename], sql.SQLTable)
        self.assertIsInstance(self.db[self.tablename], sql.SQLTable)
        del self.db[self.tablename]

        for i in range(10):
            self.db[f"table_{i}"] = self.schema

        count = 0
        for table in self.db:
            self.assertIsInstance(table, sql.SQLTable)
            self.assertEqual(table.tablename, f"table_{count}")
            count += 1
