import functools as f
import typing

import sql

class SQLTableSlice:
    
    def __init__(self, table: sql.SQLTable, indexes: slice):
        self.table = table
        self.indexes = indexes

    def values(self, **kwargs):
        columns = kwargs.get('columns', [])
        return self.table.select(self.indexes.stop-self.indexes.start, self.indexes.start, columns=columns)

    def __getitem__(self, params: typing.Union[str,list,int,slice]):
        """
        params: name of column(str), list of column names
        """
        columns = None
        if type(params) == str:
            columns = [params]

        if type(params) in [int, slice]:
            columns = list(self.table.schema.keys())[params]
            if type(params) == int:
                columns = [columns]
        
        if type(params) == list:
            # list of strings
            if f.reduce(lambda ac, cv: ac and cv, [type(arg) == str for arg in params]):
                columns = params[:]
        
        if columns is None:
            raise RuntimeError(f"Bad value for getitem: {type(params)}.")
        else:
            return self.values(columns=columns)

        