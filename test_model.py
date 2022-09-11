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
        
        class AnotherTestModel(TestModel):
            field_foreignkeyfield = sql.fields.ForeignKeyField(TestModel, 'Another')

        self.model = TestModel
        self.another_model = AnotherTestModel
        self.instance = self.model(self.db)
        self.another_instance = self.another_model(self.db, 'another')

    def test_model(self):
        self.assertIsInstance(self.instance.objects, sql.SQLTable)
        self.assertEqualUnorderedDicts(self.schema, self.instance.schema_sqlite())

        # todo: create objects
        model_first_object = self.model.create(
            field_intfield=1,
            field_floatfield=1.2,
            field_stringfield="Hello, World!"
        )
        another_model_first_object = self.another_model.create(
            field_intfield=2,
            field_floatfield=2.2,
            field_stringfield="Bye, World!",
            field_foreignkeyfield=model_first_object
        )
