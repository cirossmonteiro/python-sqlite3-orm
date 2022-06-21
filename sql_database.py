from __future__ import annotations
import enum
import sqlite3
import typing


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
        return f"""CREATE TABLE {self.tablename} ( {schema_str} );"""

    def _create_table(self, schema):
        self.cursor.execute(self._query_create_table(schema))

    def _query_insert_into(self, rows: list[typing.Dict]):
        # todo: not all columns
        def build_row_str(row):
            return " , ".join([f"\'{value}\'" if type(value) == str else str(value) for value in row.values()])
        rows_str = [f"({build_row_str(row)})" for row in rows]
        values_str = ' , '.join(rows_str)
        return f"""INSERT INTO {self.tablename} VALUES {values_str};"""
    
    def insert_into(self, values: list[typing.Dict]):
        self.cursor.execute(self._query_insert_into(values))

    def _query_select(self, limit=10):
        return f"""SELECT * FROM {self.tablename} LIMIT {limit};"""        

    def select(self, limit=10):
        self.cursor.execute(self._query_select(limit))
        return self.cursor.fetchall()

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
