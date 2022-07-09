import abc
import typing

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


class StringField(Field):
    create_type = SQLITE3_TYPES.TEXT.value
    

class Schema:
    def __init__(self, **kwargs):
        mode = kwargs.get('mode', 'schema')
        schema = kwargs.get('schema')
        if mode == 'schema':
            self.schema = schema
        elif mode == 'row':
            self.schema = self._infer(schema)
        return
    
    def _infer(self, row: typing.List[typing.Any]):
        obj = {
            key: type(value)
            for key, value in row.items()
        }
        return obj

    def __len__(self):
        return len(self.schema)

    def is_valid(self, row):
        if len(row) != len(self.schema):
            return False

        for key, value in self.schema.items():
            if key in row:
                if type(row[key]) != value:
                    return False
            else:
                return False

        return True

    def __getattr__(self, name):
        if name == 'columns':
            return tuple(self.schema.keys())

    def __contains__(self, item):
        return item in self.schema.keys()
