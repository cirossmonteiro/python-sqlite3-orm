import sqlite3
from schema import Schema

from test_commons import TestCase
import sql

class TestSQLTable(TestCase):
    
    def setUpExtra(self):
        self.tablename = 'test'
        self.schema = Schema(schema={
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        })
        self.row = {
                    'number_integer': 1,
                    'number_float': 2.1,
                    'number_numeric': 2.2,
                    'string_text': 'Hello, world!'
                }
        self.rows = [self.row, self.row]
        self.instance = sql.SQLTable(self.db, self.tablename, self.schema)

    def test_init(self):
        self.assertIsInstance(self.instance.db.cursor, sqlite3.Cursor)
        self.assertIsInstance(self.instance, sql.SQLTable)

    def test_query_create_table(self):
        self.assertEqualStringQueries(
            self.instance._query_create_table(self.schema.schema),
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
        new_instance = sql.SQLTable(self.db, self.tablename)
        self.assertEqual(self.instance.schema.schema, new_instance.schema.schema)

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
        self.instance.insert_into(self.rows)
        self.assertEqual(self.instance.select(2), [tuple(self.row.values()), tuple(self.row.values())])
        self.assertEqual(self.instance.count(), len(self.rows))
        self.assertEqual(len(self.instance), len(self.rows))
    