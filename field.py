import abc

from utils import SQLITE3_TYPES

class Field:
    def __init__(self, required=True, default=None):
        if required and default is not None:
            raise RuntimeWarning("You should't need to set a default value for a required field.")
        elif not required and default is None:
            raise RuntimeError("You must set a default value for a non-required field.")
        
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


class StringField(Field):
    create_type = SQLITE3_TYPES.TEXT.value


class NumberField(Field):
    def __init__(self, **kwargs):
        self.minimum = kwargs.get('minimum', None)
        self.maximum = kwargs.get('maximum', None)
        required = kwargs.get('required', True)
        default = kwargs.get('default', None)
        super().__init__(required, default)


class IntField(NumberField):
    create_type = SQLITE3_TYPES.INTEGER.value


class FloatField(NumberField):
    create_type = SQLITE3_TYPES.REAL.value
