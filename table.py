from __future__ import annotations

import copy
import enum
import re
import sqlite3
import time
import typing

from schema import Schema
import sql
from utils import MAP_TYPES_PYTHON_TO_SQLITE3, MAP_TYPES_SQLITE3_TO_PYTHON



SCHEMA_TYPES_REGEX = r"((?P<name>\w+) (?P<type>INTEGER|REAL|TEXT))"



class SQLTable:

    and_filter = []
    indexes = None
    limit = 10
    offset = 0
    columns = []
    is_foreign = False
    pending_migrations = []
    
    def __init__(self, db: sql.SQLDatabase, **kwargs):
        """
        cursor: Cursor object (sqlite3)
        table_name: name for table (even if already exists)
        """
        self.db = db

        is_foreign     = kwargs.get('foreign', False)
        tablename      = kwargs.get('tablename', None)
        schema: Schema = kwargs.get('schema', None)

        must_create = False

        if is_foreign:
            if schema is None:
                schema = Schema(schema={
                    'primary_key': int,
                    'foreign_key': int
                })
                local = kwargs.get('local', None)
                foreign = kwargs.get('foreign', None)
                if local is None:
                    raise RuntimeError("You must provide local Model name.")
                if foreign is None:
                    raise RuntimeError("You must provide foreign Model name.")
                if tablename is None:
                    pass
                else:
                    raise RuntimeWarning("Table name provided will be ignored.")
                tablename = f"{local}__fk__{foreign}"
                # now create a relationship table
            else:
                raise RuntimeError("You can't set schema for a table intended for foreign key.")
        else:
            if tablename is None:
                raise RuntimeError("A table name must be provided.")
            schema_loaded: Schema = self._load_schema(tablename) # todo
            if schema is None:
                if schema_loaded is None:
                    raise RuntimeError("A schema must be provided.")
                else:
                    schema = schema_loaded
            else:
                if schema_loaded is None:
                    must_create = True
                else:
                    if schema == schema_loaded:
                        pass
                    else:
                        self.pending_migrations = schema_loaded.makemigrations(schema)
                        raise RuntimeError(f"""
                            Schema provided({schema}) doesn't match current schema ({schema_loaded}) of table.
                            You must run migrations found for this table.
                        """)
            # now create a normal table

        self.schema    = schema
        self.tablename = tablename
        if must_create:
            self._create_table()
        
    def __deepcopy__(self, _):
        new_instance = SQLTable(self.db, tablename=self.tablename)        
        new_instance.and_filter = self.and_filter[:]
        new_instance.indexes = self.indexes
        new_instance.limit = self.limit
        new_instance.offset = self.offset
        new_instance.columns = self.columns[:]
        return new_instance

    def _load_schema(self, tablename):
        fetch = self.db.query_one(f"SELECT sql FROM sqlite_master WHERE type = \'table\' AND name = \'{tablename}\';")
        if fetch is None:
            return None

        describe_str = fetch[0]
        patt = re.compile(SCHEMA_TYPES_REGEX)
        schema = {}
        for group in patt.finditer(describe_str):
            schema[group[2]] = MAP_TYPES_SQLITE3_TO_PYTHON[group[3]]
        return Schema(schema=schema)


    def _query_create_table(self):
        schema_str = ' , '.join([f"{column_name} {MAP_TYPES_PYTHON_TO_SQLITE3[column_type]}\n" for column_name, column_type in self.schema.schema.items()])
        return f"""CREATE TABLE {self.tablename} ( {schema_str} );"""


    def _create_table(self):
        self.db.query_one(self._query_create_table())


    def _query_insert_into(self, rows: list[typing.Dict]):
        # todo: not all columns
        def build_row_str(row):
            return " , ".join([f"\'{value}\'" if type(value) == str else str(value) for value in row.values()])
        rows_str = [f"({build_row_str(row)})" for row in rows]
        values_str = ' , '.join(rows_str)
        return f"""INSERT INTO {self.tablename} VALUES {values_str};"""

    def insert_into(self, values: list[typing.Dict]):
        self.db.query_one(self._query_insert_into(values))

    def _query_columns(self):
        if len(self.columns) == 0:
            return '*'
        return ','.join(self.columns)
        
    def _query_where(self):
        where_str = ' AND '.join([f"{condition['column_name']} {condition['operator']} {condition['value']}" \
                                    for condition in self.and_filter])
        if where_str == '':
            where_str = '1'
        
        return where_str

    def _query_select(self):
        columns_str = self._query_columns()
        where_str = self._query_where()
        offset, limit = self.offset, self.limit

        if self.indexes is not None:
            offset, limit = self.indexes.start, self.indexes.stop - self.indexes.start

        return f"""SELECT {columns_str} FROM {self.tablename} WHERE {where_str} LIMIT {limit} OFFSET {offset};"""

    def select(self):
        return self.db.query_all(self._query_select())

    def __getitem__(self, params: typing.Union[slice, int, str, list(str)]):
        if self.indexes is not None:
            raise Exception('Indexes already defined.')

        new_instance = copy.deepcopy(self)

        if type(params) in [int, slice]:
            if type(params) == int:
                params = slice(params, params+1)
            new_instance.indexes = params
        elif type(params) == str:
            new_instance.columns.append(params)
        elif type(params) == list(str):
            new_instance.columns += params

        # validating column names
        for column in new_instance.columns:
            if column not in new_instance.schema:
                raise RuntimeError(f"The column '{column}' doesn't exist on this table.")

        return new_instance

    def __eq__(self, other: SQLTable):
        """
        compare schemas and rows
        """
        return self.and_filter == other.and_filter and \
                self.indexes == other.indexes and \
                self.limit == other.limit and \
                self.offset == other.offset and \
                self.columns == other.columns and \
                self.tablename == other.tablename

    def __neq__(self, other):
        return not self == other
    
    def count(self):
        where_str = self._query_where()
        query = f"""SELECT COUNT(*) FROM {self.tablename} WHERE {where_str};"""
        return self.db.query_one(query)[0]

    def __len__(self):
        return self.count()

    def __getattr__(self, name):
        if name == 'schema':
            return self.schema
        elif name in self.schema.columns:
            new_instance = copy.deepcopy(self)
            new_instance.columns.append(name)
            return new_instance
        else:
            raise RuntimeError(f"Column '{name}' doesn't exist on this table.")

    def filter(self, **kwargs):
        operators = {
            'lt': '<',
            'le': '<=',
            'eq': '=',
            'ne:': '!=',
            'gt': '>',
            'ge': '>='
        }

        and_filter = self.and_filter[:]
        
        for key, value in kwargs.items():
            field_name, field_operator = key.split('__')
            if field_name not in self.schema:
                raise RuntimeError(f"Column '{field_name}' doesn't exist on this table.")

            if field_operator not in operators:
                raise RuntimeError(f"Bad operator given: {field_operator}.")

            and_filter.append({
                'column_name': field_name,
                'operator': operators[field_operator],
                'value': value
            })
        
        new_instance = copy.deepcopy(self)
        new_instance.and_filter = and_filter
        return new_instance

    def makemigrations(self):
        print(239, 'table.makemigrations', self.tablename)
        return self.pending_migrations

    # def __del__(self):
    #     self.db.delete_table(self.tablename)
    #     del self.tablename
    #     del self.schema
    #     del self.and_filter
    #     del self.indexes
    #     del self.limit
    #     del self.offset
    #     del self.columns
    #     del self.is_foreign
