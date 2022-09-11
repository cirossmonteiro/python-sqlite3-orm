import os
import sqlite3

from schema import Schema

import sql

class SQLDatabase:
    
    def __init__(self, filename='sqlite3.db'):
        self.filename = filename
        self.start_cursor()
        self.end_cursor()
        self.tables = []
        self.table_index = 0

    def start_cursor(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
    
    def end_cursor(self):
        self.cursor.close()
        self.connection.close()

    def query_one(self, query):
        self.start_cursor()
        self.cursor.execute(query)
        fetch = self.cursor.fetchone()
        if fetch is not None:
            fetch = list(fetch)
        if 'INSERT' in query or 'CREATE TABLE' in query:
            self.connection.commit()
        self.end_cursor()
        return fetch

    def query_all(self, query):
        self.start_cursor()
        self.cursor.execute(query)
        fetch = self.cursor.fetchall()
        if fetch is not None:
            fetch = list(fetch)
        if 'INSERT' in query or 'CREATE TABLE' in query:
            self.connection.commit()
        self.end_cursor()
        return fetch

    def _query_table_exists(self, name):
        return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"""
    
    def _tables(self):
        query = f"""SELECT name FROM sqlite_master WHERE type='table'"""
        return [row[0] for row in self.query_all(query)]

    def table_exists(self, name):
        return self.query_one(self._query_table_exists(name)) is not None
    
    def create_table(self, tablename, schema: Schema):
        return sql.SQLTable(self, tablename=tablename, schema=schema)

    def __getitem__(self, name: str):
        if self.table_exists(name):
            return sql.SQLTable(self, tablename=name)
        else:
            raise RuntimeError(f"Table '{name}' doesn't exist in database.")

    def __setitem__(self, tablename: str, schema: Schema):
        # todo: raise error for bad schema
        return sql.SQLTable(self, tablename=tablename, schema=schema)

    def __delitem__(self, tablename: str):
        self.delete_table(tablename)
	
    def __iter__(self):
        self.tables = self._tables()
        self.table_index = -1
        return self

    def __next__(self):
        self.table_index += 1
        if self.table_index < len(self.tables):
            return self.__getitem__(self.tables[self.table_index])
        else:
            raise StopIteration

    def __query_delete_table(self, tablename: str):
        return f"DROP TABLE {tablename};"

    def delete_table(self, tablename: str):
        return self.query_one(self.__query_delete_table(tablename))
