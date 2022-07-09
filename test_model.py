import sql
from test_commons import TestCase
from utils import SQLITE3_TYPES

class TestModel(TestCase):
    
    def setUpExtra(self):
        # todo: think about order in dicts
        self.schema = {
            'field_floatfield': SQLITE3_TYPES.REAL.value,
            'field_intfield': SQLITE3_TYPES.INTEGER.value,
            'field_stringfield': SQLITE3_TYPES.TEXT.value,
        }
        class TestModel(sql.Model):
            field_intfield = sql.fields.IntField()
            field_floatfield = sql.fields.FloatField()
            field_stringfield = sql.fields.StringField()
        
        self.model = TestModel
        self.instance = self.model(self.db)

    def test_model(self):
        self.assertIsInstance(self.instance.objects, sql.SQLTable)
        self.assertEqualUnorderedDicts(self.schema, self.instance.schema_sqlite())
    