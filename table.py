from __future__ import annotations

import enum
import re
import sqlite3
import typing

import sql

class SQLITE3_TYPES(enum.Enum):
    INTEGER = 'INTEGER'
    BLOB = 'BLOB'
    REAL = 'REAL'
    NUMERIC = 'NUMERIC'
    TEXT = 'TEXT'


MAP_TYPES_PYTHON_TO_SQLITE3 = {
    int: SQLITE3_TYPES.INTEGER.value,
    float: SQLITE3_TYPES.REAL.value,
    str: SQLITE3_TYPES.TEXT.value
}

MAP_TYPES_SQLITE3_TO_PYTHON = {
    SQLITE3_TYPES.INTEGER.value: int,
    SQLITE3_TYPES.REAL.value: float,
    SQLITE3_TYPES.TEXT.value: str
}

SCHEMA_TYPES_REGEX = r"((?P<name>\w+) (?P<type>INTEGER|REAL|TEXT))"

class SQLTable:
    
    def __init__(self, cursor: sqlite3.Cursor, tablename: str, schema: typing.Union[dict, None] = None):
        """
        cursor: Cursor object (sqlite3)
        table_name: name for table (even if already exists)
        """
        self.cursor = cursor
        self.tablename = tablename
        self.schema = schema
        if schema is None:
            self._load_schema()
        else:
            self._create_table(schema)

    def _load_schema(self):
        self.cursor.execute(f'select sql from sqlite_master where type = \'table\' and name = \'{self.tablename}\';')
        describe_str = self.cursor.fetchone()[0];
        patt = re.compile(SCHEMA_TYPES_REGEX)
        self.schema = {}
        for group in patt.finditer(describe_str):
            self.schema[group[2]] = MAP_TYPES_SQLITE3_TO_PYTHON[group[3]]

    def _query_create_table(self, schema):
        schema_str = ' , '.join([f"{column_name} {MAP_TYPES_PYTHON_TO_SQLITE3[column_type]}\n" for column_name, column_type in schema.items()])
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

    def _query_select(self, limit=10, offset=0, **kwargs):
        columns = kwargs.get('columns', [])
        columns_str = '*' if len(columns) == 0 else ','.join(columns)
        return f"""SELECT {columns_str} FROM {self.tablename} LIMIT {limit} OFFSET {offset};"""        

    def select(self, limit=10, offset=0, **kwargs):
        columns = kwargs.get('columns', [])
        for column in columns:
            if column not in self.schema:
                raise RuntimeError(f"The column '{column}' doesn't exist on this table.")
        self.cursor.execute(self._query_select(limit, offset, columns=columns))
        return self.cursor.fetchall()

    def __getitem__(self, params: typing.Union[slice, int]):
        start, end = params, None
        if type(params) != slice:
            params = slice(params, params+1)
        # return self.select(end-start, start)
        return sql.SQLTableSlice(self, params)

    # todo
    def __eq__(self, sqltable: SQLTable):
        """
        compare schemas and rows
        """
        return

