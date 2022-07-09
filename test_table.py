import copy
import sqlite3

from schema import Schema
import sql
from table import SQLTable
from test_commons import TestCase

class TestSQLTable(TestCase):
    
    def setUpExtra(self):
        self.tablename = 'test'
        self.schema = Schema(schema={
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        })
        self.row = lambda n: {
                'number_integer': n,
                'number_float': n + .1,
                'number_numeric': n + .2,
                'string_text': 'Hello, world!'
            }
        self.rows = [self.row(n) for n in range(1, 6)]
        self.instance = sql.SQLTable(self.db, self.tablename, self.schema)

    def test_init(self):
        self.assertIsInstance(self.instance.db.cursor, sqlite3.Cursor)
        self.assertIsInstance(self.instance, sql.SQLTable)

    def test_query_create_table(self):
        self.assertEqualStringQueries(
            self.instance._query_create_table(),
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
                self.row(1)
            ]),
            f"""
                INSERT INTO {self.tablename} VALUES
                (1 , 1.1 , 1.2 , 'Hello, world!');
            """
        )
        self.instance.insert_into(self.rows)

        # SELECT with pagination
        self.assertEqual(self.instance.select(), [tuple(self.row(n).values()) for n in range(1, 6)])
        self.assertEqual(self.instance[1:3].select(), [tuple(self.row(n).values()) for n in range(2, 4)])

        # SELECT with WHERE
        self.assertIsInstance(self.instance.filter(number_integer__le=1), SQLTable)
        self.assertEqual(self.instance[0].select(), self.instance.filter(number_integer__le=1).select())
        self.assertEqual([], self.instance.filter(number_integer__lt=1).select())
        
        # SELECT COUNT
        self.assertEqual(self.instance.count(), len(self.rows))
        self.assertEqual(len(self.instance), len(self.rows))

        # SELECT one column
        column_values = [tuple([row['number_integer']]) for row in self.rows]
        self.assertEqual(self.instance.number_integer.select(), column_values)
        self.assertEqual(self.instance["number_integer"].select(), column_values)
        
        # deepcopy and =/!=
        new_instance = copy.deepcopy(self.instance)
        self.assertEqual(self.instance, new_instance)
        self.assertNotEqual(self.instance, new_instance['number_integer'])