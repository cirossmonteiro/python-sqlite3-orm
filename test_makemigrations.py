import copy
import sqlite3

from schema import Schema
import sql
from table import SQLTable
from test_commons import TestCase
from makemigrations import main as makemigrations

class TestSQLTable(TestCase):
    
    def setUpExtra(self):
        self.old_tablename = 'old_test'
        self.old_schema = Schema(schema={
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        })

        self.new_tablename = 'new_test'
        self.new_schema = Schema(schema={
            'number_integer': int,
            'new_number_float': float,
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
        self.table = sql.SQLTable(self.db, tablename=self.old_tablename, schema=self.old_schema)

    def test_main(self):
        table_updated = sql.SQLTable(self.db, tablename=self.old_tablename, schema=self.new_schema)
        migrations = makemigrations()
        print(41, migrations)
