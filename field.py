from utils import SQLITE3_TYPES, MAP_TYPES_PYTHON_TO_SQLITE3

class Field:
    create_type = None
    def __init__(self, required=True, default=None):
        if required and default is not None:
            raise RuntimeWarning("You should't need to set a default value for a required field.")
        elif not required and default is None:
            raise RuntimeError("You must set a default value for a non-required field.")
        elif type(required) != bool:
            raise RuntimeError("Required is boolean.")
        self.required = required
        self.default = default
        if self.create_type is None:
            raise Exception(f"A Field instance must have a create_type defined by one of them: {",".join(SQLITE3_TYPES._member_names_)}")

    def __repr__(self):
        return f"<{self.__class__.__name__} required={self.required} default={self.default}>"

    def validate(self, value):
        return MAP_TYPES_PYTHON_TO_SQLITE3[type(value)] == self.create_type

class StringField(Field):
    create_type = SQLITE3_TYPES.TEXT.value

class IntField(Field):
    create_type = SQLITE3_TYPES.INTEGER.value

class FloatField(Field):
    create_type = SQLITE3_TYPES.REAL.value

class RelatedField(IntField):
    def set_first(self, first):
        self.first = first
        
    def __init__(self, model, **kwargs):
        self.second = model.__name__
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<RelatedField first=\"{self.first}\" second=\"{self.second}\" >"
    


    
# class NumberField(Field):
#     def __init__(self, **kwargs):
#         self.minimum = kwargs.get('minimum', None)
#         self.maximum = kwargs.get('maximum', None)
#         required = kwargs.get('required', True)
#         default = kwargs.get('default', None)
#         super().__init__(required, default)

# class ForeignKeyField(IntField):
#     def __init__(self, model_related, required=True, default=None):
#         self.model_related = model_related
#         super().__init__(required=required, default=default)