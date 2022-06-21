# A one-table-only and SQLite3-compatible Python ORM

- two classes: SQLTable, SQLDatabase
- current supported one-table operations: CREATE TABLE, INSERT, SELECT
- next supported one-table operations: UPDATE, DELETE
- no external dependencies



## How to test

Just run `python3 test_sql_database.py`

## How to develop

1- Install [nodemon](https://www.npmjs.com/package/nodemon) to run tests after every change in files.

1.1- Running `npm install -g nodemon` should be enough

2- Run `nodemon --exec python3 test_sql_database.py`
