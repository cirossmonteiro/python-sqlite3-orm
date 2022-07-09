
# A one-table-only and SQLite3-compatible Python ORM

  

- three classes: SQLTable, SQLDatabase, SQLTableSlice

- currently supported one-table operations: CREATE TABLE, INSERT, SELECT

- next supported one-table operations: UPDATE, DELETE

- no external dependencies


## Documentation

*class* sql.**SQLDatabase**(*filename='sqlite3.db'*)


*class* sql.**SQLTable**(*cursor, tablename, schema=None*)

NEW *class* sql.**Field**(*required=True, default=None*)

NEW *class* sql.**Model**(*db: SQLDatabase*)

```
class TestModel(sql.Model):
    field_intfield = sql.fields.IntField()
    field_floatfield = sql.fields.FloatField()
    field_stringfield = sql.fields.StringField()
```

*class* test_commons.**TestCase**

&nbsp;&nbsp;&nbsp;&nbsp;**assertEqualStringQueries**

&nbsp;&nbsp;&nbsp;&nbsp;**assertEqualUnorderedDicts**


## How to develop (or test)

  

1- Install [nodemon](https://www.npmjs.com/package/nodemon) to run tests after every change in files.

  

1.1- Running `npm install -g nodemon` should be enough

  

2- You'll need two terminal windows:

2.1- First terminal: `nodemon --exec python3 http_server.py`

2.2- Second terminal: `nodemon --exec python3 test_main.py`