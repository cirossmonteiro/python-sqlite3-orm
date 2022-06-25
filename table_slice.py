import typing

import sql

class SQLTableSlice:
    
    def __init__(self, table: sql.SQLTable, indexes: slice):
        self.table = table
        self.indexes = indexes

    def values(self, **kwargs):
        columns = kwargs.get('columns', [])
        return self.table.select(self.indexes.stop-self.indexes.start, self.indexes.start, columns=columns)

    def __getitem__(self, column_table):
        return self.values(columns=[column_table])