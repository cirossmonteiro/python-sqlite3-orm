import sql

class SQLTableSlice:
    
    def __init__(self, table: sql.SQLTable, indexes: slice):
        self.table = table
        self.indexes = indexes

    def values(self):
        return self.table.select(self.indexes.stop-self.indexes.start, self.indexes.start)