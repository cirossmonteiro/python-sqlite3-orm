import typing

from utils import MAP_TYPES_SQLITE3_TO_PYTHON

class Schema:
    def __init__(self, **kwargs):
        mode = kwargs.get('mode', 'schema')
        schema = kwargs.get('schema')
        if mode == 'schema':
            self.schema = schema
        elif mode == 'schema_sqlite':
            self.schema = self._infer_sqlite(schema)
        elif mode == 'row':
            self.schema = self._infer(schema)
        return

    def _infer_sqlite(self, schema):
        fixed_schema = {
            field: MAP_TYPES_SQLITE3_TO_PYTHON[field_type]
            for field, field_type in schema.items()
        }
        return fixed_schema
    
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
