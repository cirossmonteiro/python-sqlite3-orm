from schema import Schema
from test_commons import TestCase
import sql

class TestSQLTableSlice(TestCase):
    
    def setUpExtra(self):
        self.tablename = 'test'
        self.schema = Schema(schema={
            'number_integer': int,
            'number_float': float,
            'number_numeric': float,
            'string_text':  str,
        })
        self.rows = [
            {
                'number_integer': n,
                'number_float': n+0.1,
                'number_numeric': n+0.2,
                'string_text': f'Hello, x-{n} world!'
            }
            for n in range(10)
        ]
        self.table = sql.SQLTable(self.db, self.tablename, self.schema)
        self.table.insert_into(self.rows)
        self.indexes = {
            'one': 0,
            'start': 1,
            'stop': 6
        }
        self.column_name = 'number_integer'
        self.error_column_name = 'number'
    
    def test_init(self):
        slice1 = self.table[self.indexes['one']]
        self.assertIsInstance(slice1, sql.SQLTableSlice)
        self.assertEqual(slice1.values(), [tuple(self.rows[self.indexes['one']].values())])

        slice2 = self.table[self.indexes['start']:self.indexes['stop']]
        self.assertIsInstance(slice2, sql.SQLTableSlice)
        self.assertEqual(slice2.values(), [tuple(self.rows[n].values()) for n in range(self.indexes['start'], self.indexes['stop'])])

        d = self.indexes['stop']-self.indexes['start']
        self.assertEqual(slice2.count(), d)
        self.assertEqual(len(slice2), d)
    
    def test_values(self):
        table_slice = self.table[self.indexes['start']:self.indexes['stop']]
        column_values = [(row['number_integer'],) for row in self.rows[1:6]]
        all_columns_values = [tuple(row.values()) for row in self.rows[1:6]]

        # values(columns=list)
        self.assertEqual(table_slice.values(columns=['number_integer']), column_values)

        # type(params) == str
        self.assertEqual(table_slice[self.column_name], column_values)

        # __getattr__
        self.assertEqual(table_slice.number_integer, column_values)

        # type(params) == int - accessing by schema
        self.assertEqual(table_slice[0], column_values)

        # all columns
        self.assertEqual(table_slice[:], all_columns_values)

        # type(params) == list(str)
        self.assertEqual(table_slice[[self.column_name]], column_values)
        
        # error - when table doesn't have column with name given
        with self.assertRaises(RuntimeError) as error:    
            table_slice.values(columns=[self.error_column_name])
        self.assertEqual(str(error.exception), f"The column '{self.error_column_name}' doesn't exist on this table.")

