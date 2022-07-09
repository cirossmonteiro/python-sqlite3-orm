import sqlite3
from schema import Schema

import sql

class SQLDatabase:
    
    def __init__(self, filename='sqlite3.db'):
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def _query_table_exists(self, name):
        return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"""
    
    def tables(self):
        query = f"""SELECT name FROM sqlite_master WHERE type='table'"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def table_exists(self, name):
        self.cursor.execute(self._query_table_exists(name))
        return self.cursor.fetchone() is not None
    
    def create_table(self, name, schema: Schema):
        return sql.SQLTable(self, name, schema)

    def __getitem__(self, name: str):
        if self.table_exists(name):
            return sql.SQLTable(self, name)
        # todo: raise error if table doesn't exist
        return None

    def __setitem__(self, name: str, schema: Schema):
        # todo: raise error for bad schema
        return sql.SQLTable(self, name, schema)
