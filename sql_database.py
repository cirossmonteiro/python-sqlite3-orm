import enum
import sqlite3
import typing

from __future__ import annotations


class SQLITE3_TYPES(enum.Enum):
    INTEGER = 'INTEGER'
    BLOB = 'BLOB'
    REAL = 'REAL'
    NUMERIC = 'NUMERIC'
    TEXT = 'TEXT'


MAP_SQLITE3_PYTHON_TYPES = {
    int: SQLITE3_TYPES.INTEGER,
    float: SQLITE3_TYPES.REAL,
    str: SQLITE3_TYPES.TEXT
}


class SQLTable:

    def __init__(self, cursor: sqlite3.Cursor, tablename: str, schema: typing.Union[dict, None] = None):
        """
        cursor: Cursor object (sqlite3)
        table_name: name for table (even if already exists)
        """
        self.cursor = cursor
        self.tablename = tablename
        if schema is not None:
            self._create_table(schema)

    def _query_create_table(self, schema):
        schema_str = ' , '.join([f"{column_name} {MAP_SQLITE3_PYTHON_TYPES[column_type].value}\n" for column_name, column_type in schema.items()])
        return f"""CREATE TABLE {self.tablename} ( {schema_str} )"""

    def _create_table(self, schema):
        self.cursor.execute(self._query_create_table(schema))

    # todo
    def insert(self, row: dict):
        return
    
    # todo
    def insert(self, rows: typing.List[dict]):
        return

    # todo
    def __eq__(self, sqltable: SQLTable):
        """
        compare schemas and rows
        """
        return


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
        return SQLTable(self.cursor, name, schema)

    def __getitem__(self, name: str):
        if self.table_exists(name):
            return SQLTable(self.cursor, name)
        # todo: raise error if table doesn't exist
        return None

    def __setitem__(self, name: str, schema: dict):
        # todo: raise error for bad schema
        return self.create_table(name, schema)