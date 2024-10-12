import abc

from utils import SQLITE3_TYPES

class Field(metaclass=abc.ABCMeta):
    def __init__(self, required=True, default=None):
        if required and default is not None:
            raise RuntimeWarning("You should't need to set a default value for a required field.")
        elif not required and default is None:
            raise RuntimeError("You must set a default value for a non-required field.")
        elif type(required) != bool:
            raise RuntimeError("Required is boolean.")
        self.required = required
        self.default = default

    def __repr__(self):
        return f"<Field required={self.required} default={self.default} >"

    # @property
    # @abc.abstractmethod
    # def required(self):
    #     pass

    # @property
    # @abc.abstractmethod
    # def default(self):
    #     pass

    @property
    @abc.abstractmethod
    def create_type(self):
        pass

    @abc.abstractmethod
    def validate(self):
        pass


class StringField(Field):
    create_type = SQLITE3_TYPES.TEXT.value

    def validate(self, value):
        return type(value) == str


class NumberField(Field):
    def __init__(self, **kwargs):
        self.minimum = kwargs.get('minimum', None)
        self.maximum = kwargs.get('maximum', None)
        required = kwargs.get('required', True)
        default = kwargs.get('default', None)
        super().__init__(required, default)


class IntField(NumberField):
    create_type = SQLITE3_TYPES.INTEGER.value

    def validate(self, value):
        return type(value) == int


class FloatField(NumberField):
    create_type = SQLITE3_TYPES.REAL.value

    def validate(self, value):
        return type(value) == float

class ForeignKeyField(IntField):

    def __init__(self, model_related, required=True, default=None):
        self.model_related = model_related
        super().__init__(required=required, default=default)

class RelatedField(IntField):

    def set_first(self, first):
        self.first = first
        
    def __init__(self, model, **kwargs):
        self.second = model.__name__
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<RelatedField first=\"{self.first}\" second=\"{self.second}\" >"