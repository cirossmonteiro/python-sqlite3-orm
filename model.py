import abc

class Model:
    def __init__(self):
        fields = set(dir(self.__class__)) - set(dir(Model))
        self.fields = {
            field: getattr(self, field)
            for field in fields
        }
        self.name = Model.__subclasses__()[0].__name__
    
    def schema_sqlite(self):
        return {
            field: field_class.create_type
            for field, field_class in self.fields.items()
        }

    def __repr__(self):
        return f"<Model name={self.name} fields=[{self.fields}]"

    @abc.abstractmethod
    def validate(self):
        pass