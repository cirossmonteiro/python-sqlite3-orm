import sqlite3

import sql

class SQLDatabase:
    
    def __init__(self, filename = 'sqlite3.db'):
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def _query_table_exists(self, name):
        return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"""

    def table_exists(self, name):
        self.cursor.execute(self._query_table_exists(name))
        return self.cursor.fetchone() is not None
    
    def create_table(self, name, schema):
        return sql.SQLTable(self.cursor, name, schema)

    def __getitem__(self, name: str):
        if self.table_exists(name):
            return sql.SQLTable(self.cursor, name)
        # todo: raise error if table doesn't exist
        return None

    def __setitem__(self, name: str, schema: dict):
        # todo: raise error for bad schema
        return self.create_table(name, schema)