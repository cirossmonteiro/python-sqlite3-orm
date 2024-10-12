import model
import field

@model.builder
class TestModel(model.Model):
    fieldIntfield = field.IntField()
    fieldFloatfield = field.FloatField()
    fieldStringfield = field.StringField()

@model.builder
class AnotherTestModel(TestModel):
    fieldForeignkeyfield = field.RelatedField(TestModel)

ModelExportation = [
    TestModel,
    AnotherTestModel
]