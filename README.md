# A simple, naive and SQLite3-compatible Python ORM

- two classes: SQLTable, SQLDatabase
- current supported one-table operations: CREATE TABLE
- next supported one-table operations: INSERT, SELECT, UPDATE, DELETE
- no external dependencies



## How to test

Just run `python3 test_sql_database.py`

## How to develop

1) Install [nodemon](https://www.npmjs.com/package/nodemon) to run tests after every change in files.
1.1) Running `npm install -g nodemon` should be enough
2) Run `nodemon --exec test_sql_database.py`