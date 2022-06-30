
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


## How to develop (or test)

  

1- Install [nodemon](https://www.npmjs.com/package/nodemon) to run tests after every change in files.

  

1.1- Running `npm install -g nodemon` should be enough

  

2- You'll need two terminal windows:

2.1- First terminal: `nodemon --exec python3 http_server.py`

2.2- Second terminal: `nodemon --exec python3 test_main.py`