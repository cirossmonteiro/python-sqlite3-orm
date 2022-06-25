
# A one-table-only and SQLite3-compatible Python ORM

  

- three classes: SQLTable, SQLDatabase, SQLTableSlice

- currently supported one-table operations: CREATE TABLE, INSERT, SELECT

- next supported one-table operations: UPDATE, DELETE

- no external dependencies


## Documentation

*class* sql.**SQLDatabase**(*filename='sqlite3.db'*)


*class* sql.**SQLTable**(*cursor, tablename, schema=None*)


*class* sql.**SQLTableSlice**(*table, indexes*)

*class* test_commons.**TestCase**
&nbsp;&nbsp;&nbsp;&nbsp;**assertEqualStringQueries**
  

## How to test

  

Just run `python3 test_main.py`

  

## How to develop

  

1- Install [nodemon](https://www.npmjs.com/package/nodemon) to run tests after every change in files.

  

1.1- Running `npm install -g nodemon` should be enough

  

2- Run `nodemon --exec python3 test_main.py`