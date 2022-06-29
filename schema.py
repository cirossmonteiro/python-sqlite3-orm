import typing

class Schema:
    def __init__(self, **kwargs):
        mode = kwargs.get('mode', 'schema')
        schema = kwargs.get('schema')
        if mode == 'schema':
            self.schema = schema
        elif mode == 'row':
            self.schema = self.__infer(schema)
        return
    
    def __infer(self, row):
        obj = {
            key: type(value)
            for key, value in row.items()
        }
        return obj

    # todo: def __contains__(self): # operator 'in'