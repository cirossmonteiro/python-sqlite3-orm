import abc
from schema import Schema
import sql


class Model:
    def __init__(self, db: sql.SQLDatabase):
        self.db = db

        fields = set(dir(self.__class__)) - set(dir(Model))
        self.fields = {
            field: getattr(self, field)
            for field in fields
        }
        self.schema = Schema(schema=self.schema_sqlite(), mode="schema_sqlite")

        self.name = Model.__subclasses__()[0].__name__
        self.objects = sql.SQLTable(self.db, self.name, self.schema) # current task
    
    def schema_sqlite(self):
        return {
            field: field_class.create_type
            for field, field_class in self.fields.items()
        }

    def __repr__(self):
        return f"<Model name={self.name} fields=[{self.fields}]"
