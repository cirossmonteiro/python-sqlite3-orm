import abc

from schema import Schema
import sql


class Model:
    def cls(self, db: sql.SQLDatabase, name: str = None):
        """
        name: in case a model is a subclass of another model, inheriting its field names
        todo: use subclass's name instead of providing one
        """
        self.db = db

        fields = set(dir(self.__class__)) - set(dir(Model))
        self.fields = {
            field: getattr(self, field)
            for field in fields
        }
        self.schema = Schema(schema=self.schema_sqlite(), mode="schema_sqlite")
        
        self.name = Model.__subclasses__()[0].__name__ if name is None else name
        
        foreign_fields = [field for field, field_class in self.fields.items() if isinstance(field_class, sql.fields.ForeignKeyField)]
        self.objects = sql.SQLTable(self.db, tablename=self.name, schema=self.schema) # current task
        self.foreign_tables = [sql.SQLTable(self.db, is_foreign=True, local=self.name, foreign=field) for field in foreign_fields]
        print(27, 'init')
    
    def schema_sqlite(self):
        return {
            field: field_class.create_type
            for field, field_class in self.fields.items()
        }

    def __repr__(self):
        return f"<Model name={self.name} fields=[{self.fields}]"

    @classmethod
    def __is_valid(cls, values):
        print(37, dir(cls))
        print(38, values)
        return True

    @classmethod
    def create(cls, **kwargs):
        if cls.__is_valid(kwargs):
            return True