from __future__ import annotations
import typing

from utils import MAP_TYPES_PYTHON_TO_SQLITE3, MAP_TYPES_SQLITE3_TO_PYTHON, compute_transpositions

class Schema:
    def __init__(self, **kwargs):
        mode = kwargs.get('mode', 'schema')
        schema = kwargs.get('schema')
        if mode == 'schema':
            self.check_schema(schema)
            self.schema = schema
        elif mode == 'schema_sqlite':
            self.schema = self._infer_sqlite(schema)
        elif mode == 'row':
            self.schema = self._infer(schema)
        else:
            raise RuntimeError("A schema must be provided.")
        return

    def check_schema(self, schema):
        if type(schema) != dict:
            raise RuntimeError("Schema must be a dict.")
        for schema_label, schema_type in schema.items():
            if type(schema_label) != str:
                raise RuntimeError(f"Field name must be a string, not of {type(schema_label)}.")
            if schema_type not in [int, float, str]:
                raise RuntimeError(f"Bad type/class for field '{schema_label}': {type(schema_type)}.")

    def _infer_sqlite(self, schema):
        fixed_schema = {
            field: MAP_TYPES_SQLITE3_TO_PYTHON[field_type]
            for field, field_type in schema.items()
        }
        return fixed_schema
    
    def _infer(self, row: typing.List[typing.Any]):
        obj = {
            key: type(value)
            for key, value in row.items()
        }
        return obj

    def __len__(self):
        return len(self.schema)

    # check by Python types
    def is_valid(self, row):
        if len(row) != len(self.schema):
            return False

        for key, value in self.schema.items():
            if key in row:
                if type(row[key]) != value:
                    return False
            else:
                return False

        return True

    def __getattr__(self, name):
        if name == 'columns':
            return tuple(self.schema.keys())

    def __contains__(self, item):
        return item in self.schema.keys()

    def __repr__(self):
        return str(self.schema.keys())

    def __eq__(self, other):
        return self.schema == other
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def convert_to_sqlite_types(self):
        schema = {}
        for key, value in self.schema.items():
            schema[key] = MAP_TYPES_PYTHON_TO_SQLITE3[value]
        return schema

    # compute necessary migrations for database
    def __makemigrations(old_schema: Schema, new_schema: Schema, **kwargs):
        """
        types of changes in schema:
        - renaming columns
          - remark: this must be the first one, so both schemas
            have the same colum names
        - changing column types
        - removing columns
        - adding columns
        - swapping columns (changing their positions)
          - remark: this must be the last one, so both schemas
            have the same columns (then the same size)
        
        guess: add+remove ()
        """
        # without this preset you can't distinguish a column
        # which has changed his name and his type at same time
        before_migration = kwargs.get('before_migration', {})
        rename_columns = before_migration.get('rename_columns', [])
        rename_table = before_migration.get('rename_table', None)
        old_schema = old_schema.convert_to_sqlite_types()
        # for (old_name, new_name) in rename:
        #     old_schema[new_name] = old_schema[old_name]
        #     del old_schema[old_name]
        
        new_schema = new_schema.convert_to_sqlite_types()
        
        
        remove_columns = []
        # NOT SUPPORTED BY SQLITE   
        #update_columns = []
        add_columns = []
        
        # updating (ignored by now) and removing columns
        dict_items = list(old_schema.items())
        for old_field, old_type in dict_items:
            if old_field in new_schema:
                new_type = new_schema[old_field]
                if old_type != new_type:
                    raise RuntimeError("Changing column type is not supported by SQLite.")
                    # NOT SUPPORTED BY SQLITE
                    # update_columns.append({
                    #     'name': old_field,
                    #     'type': new_type
                    # })
                    old_schema[old_field] = new_type
            else:
                remove_columns.append(old_field)
                del old_schema[old_field]
        
        # adding columns
        for new_field, new_type in new_schema.items():
            if new_field not in old_schema:
                add_columns.append({
                    'name': new_field,
                    'type': new_type
                })
                old_schema[new_field] = new_type
        
        # todo: reorder old_schema 
        # old_indexes = list(range(old_schema))
        # new_indexes = [new_schema.keys().index(old_field) for old_field in old_schema.keys()]
        old_columns, new_columns = list(old_schema.keys()), list(new_schema.keys())
        transpositions = compute_transpositions(old_columns, new_columns)
        
        return dict(
            rename_table=rename_table,
            rename_columns=rename_columns,
            remove_columns=remove_columns,
            #update_columns=update_columns,
            add_columns=add_columns,
            transpositions=transpositions
        )

    def makemigrations(old_schema: Schema, new_schema: Schema, **kwargs):
        """
        hint: clone old_schema, maybe consider changing it step by step,
              until it becomes equal to new_schema
        """
        # swapping columns: https://stackoverflow.com/questions/37649/swapping-column-values-in-mysql
        migrations = []
        __migrations = old_schema.__makemigrations(new_schema, **kwargs)
        rename_table = __migrations.get('rename_table', None)
        if rename_table is not None:
            if old_schema.tablename is None:
                raise RuntimeError("Schema doesn't have a table name set.")
            migrations.append(f"ALTER TABLE {old_schema.tablename} RENAME TO {rename_table};")

        for columns in __migrations.rename_columns:
            migrations.append(f"ALTER TABLE RENAME COLUMN '{columns[0]}' TO '{columns[1]}';")

        for column in __migrations.remove_columns:
            migrations.append(f"ALTER TABLE DROP COLUMN '{column}';")

        for column in __migrations.add_columns:
            migrations.append(f"ALTER TABLE ADD COLUMN '{column['name']}' {column['type']};")

        # NOT SUPPORTED BY SQLITE
        # for column in __migrations.update_columns:
        #     migrations.append(f"ALTER TABLE")

        # todo: consider transpositions
        return migrations
