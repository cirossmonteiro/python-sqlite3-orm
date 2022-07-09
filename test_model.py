from unittest import TestCase

from model import Model
from field import IntField, FloatField, StringField
from utils import SQLITE3_TYPES

class TestModel(TestCase):
    
    def setUp(self):
        # todo: think about order in dicts
        self.schema = {
            'field_floatfield': SQLITE3_TYPES.REAL.value,
            'field_intfield': SQLITE3_TYPES.INTEGER.value,
            'field_stringfield': SQLITE3_TYPES.TEXT.value,
        }
        class TestModel(Model):
            field_intfield = IntField()
            field_floatfield = FloatField()
            field_stringfield = StringField()
        
        self.model = TestModel
        self.instance = self.model()

    def test_model(self):
        self.assertEqual(self.schema, self.instance.schema_sqlite())