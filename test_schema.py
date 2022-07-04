from unittest import TestCase

from schema import Schema

class TestSchema(TestCase):
    
    def setUp(self):
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
        self.instance = Schema(schema=self.schema)

    def test_instance(self):
        self.assertIsInstance(self.instance, Schema)
        self.assertEqual(self.instance._infer(self.row), self.schema)
        
        self.assertEqual(self.instance.columns, tuple(self.schema.keys()))
        self.assertTrue('number_integer' in self.instance)

        self.assertEqual(len(self.instance), len(self.schema))
        self.assertTrue(self.instance.is_valid(self.row))
        self.row.update({ 'bad_column': 0})
        self.assertFalse(self.instance.is_valid(self.row))
        