import sqlite3

from field import *

reserved = ["make_migration", "fields", "objects", 'create', "filter", "get", "build_objects"]

def escape_str(v):
    return str(v) if type(v) != str else f"\"{v}\""

def create_tables(name, fields):
    del fields["fields"]["id"]
    fields["nonRelated"].pop()
    nonRelated_str = ',\n    '.join([f"{field} {fields["fields"][field].create_type}" for field in fields["nonRelated"]])
    query = f"""CREATE TABLE {name} (
        id INTEGER PRIMARY KEY,
        {nonRelated_str}
    );\n"""
    for field in fields["related"]:
        query += f"""\nCREATE TABLE relationship_{fields["fields"][field].first}_{field}_{fields["fields"][field].second} (
            id INTEGER PRIMARY KEY,
            first INTEGER,
            second INTEGER
        );\n"""
    return query

MAP_OP = dict(
    eq="=",
    ne="!=",
    gt=">",
    ge=">=",
    lt="<",
    le="<="
)

class QuerySet:
    def __init__(self, name, fields, sliced=slice(0, 10, 1), kwargs={}):
        super().__setattr__("name", name)
        super().__setattr__("fields", fields) # basic information about table schema
        super().__setattr__("sliced", sliced) # slice(x,y,z) == [x:y;z]: LIMIT + OFFSET
        super().__setattr__("kwargs", kwargs) # WHERE conditions

    def _where(self, columns=None, **options):
        # to-do: modifier of column: example => t.example
        # to-do: OR condition
        columns = options.get("columns", None)
        before = options.get("before", "")
        if columns is None:
            columns = self.fields.keys()
        for column in self.kwargs.keys():
            if column in self.fields["related"]:
                raise Exception("WHERE with related columns is not supported yet.", column)

        kwargs, items = self.kwargs.copy(), self.kwargs.items()
        for key, value in items:
            if key.find("_") == -1:
                kwargs[f"{key}_eq"] = value
                del kwargs[key]
        return " AND ".join([
            f"{before}{key.split('_')[0]} {MAP_OP[key.split('_')[1]]} {value}"  # to-do: other conditions
            for key, value in kwargs.items()
            if key in columns
        ])

    def update(self, **values):
        for column in values.keys():
            if column not in self.fields["fields"]:
                raise Exception("Column doesn't exist in schema.")

        con = sqlite3.connect("db.sqlite3", autocommit=True)

        # nonRelated columns
        values_str = ",".join([
            f"{key} = {escape_str(value)}" for key, value in values.items()
            if key in self.fields["nonRelated"]
        ])
        kwargs_str = self._where()
        if kwargs_str == "":
            kwargs_str = "1"
        if values_str != "":
            query = f"""
                UPDATE {self.name}
                SET {values_str}
                WHERE {kwargs_str};
            """
            con.execute(query)

        # related columns
        f = self.fields
        query = ""
        for related in [column for column in values if column in f["related"]]:
            delete = insert = ""
            field = f["fields"][related]

            # remove current state of relationships
            kwargs_str = self._where(before="t.")
            if kwargs_str == "":
                kwargs_str = "1"
            delete = f"""
                DELETE FROM relationship_{field.first}_{related}_{field.second}
                WHERE id IN (SELECT id WHERE {kwargs_str});
            """
            
            # get list of IDs to build new relationships according to WHERE
            select = f"""
                SELECT id FROM {self.name}
                WHERE {kwargs_str};
            """
            rows = con.execute(select).fetchall()

            # build new relationships
            if len(rows) > 0 and len(values[related]) > 0:
                insert = f"""
                    INSERT INTO relationship_{field.first}_{related}_{field.second}
                    (first, second)
                    VALUES {",".join([
                        ",".join([
                            f"({row[0]}, {escape_str(obj.id)})"
                            for obj in values[related]
                        ])
                        for row in rows
                    ])};
                """
                con.execute(insert);
            query += delete + insert
        if query != "":
            con.executescript(query)
        con.close()
    
    def values(self, columns=None):
        # to-do: need to SELECT id in nonRelated
        con = sqlite3.connect("db.sqlite3", autocommit=True)

        # general columns
        if type(columns) == str and columns != "*":
            columns = columns.split(" ")
        elif columns == None or columns == "*":
            columns = [*self.fields["nonRelated"], *self.fields["related"]]
        elif type(columns) != list:
            raise Exception("bad columns variable: ", columns)
        for column in columns:
            if column not in self.fields["fields"]:
                raise AttributeError("Column doesn't exist in current schema.")
        if "id" not in columns:
            columns.insert(0, "id")

        # nonRelated columns
        nonRelated = [col for col in columns if col in self.fields["nonRelated"]]
        nonRelated_str = ",".join(nonRelated)
        if nonRelated_str == "":
            nonRelated_str = "id"
        nonRelated_kwargs_str = self._where(columns=nonRelated)
        if nonRelated_kwargs_str == "":
            nonRelated_kwargs_str = "1"
        nonRelated_query = f"""
            SELECT {nonRelated_str}
            FROM {self.name}
            WHERE {nonRelated_kwargs_str}
            LIMIT {self.sliced.stop-self.sliced.start+1}
            OFFSET {self.sliced.start};
        """
        # print("query nonrelated", nonRelated_query)
        if len(nonRelated) > 0:
            nonRelated_rows = con.execute(nonRelated_query).fetchall()

        # related columns
        related = [col for col in columns if col in self.fields["related"]]
        related_kwargs_str = self._where(columns=related)
        if related_kwargs_str == "":
            related_kwargs_str = "1"
        select_str = ""
        joins_str = ""
        for index, col in enumerate(related):
            field = self.fields["fields"][col]
            rel_table = f"relationship_{field.first}_{col}_{field.second}"
            joins_str += f"""
                FULL JOIN {rel_table} rt{index}
                ON t.id = rt{index}.first
            """
        select_str = ",".join([f"GROUP_CONCAT(rt{index}.second)" for index in range(len(related))])
        groupby_str = "".join(["GROUP BY t.id\n" for i in range(len(related))])
        related_query = f"""
            SELECT {select_str}
            FROM {self.name} t
            {joins_str}
            WHERE {related_kwargs_str}
            {groupby_str}
            LIMIT {self.sliced.stop-self.sliced.start+1}
            OFFSET {self.sliced.start};
        """
        # print("query related", related_query)
        if len(related) > 0:
            related_rows = con.execute(related_query).fetchall()

        # merging related and nonRelated columns
        final_rows = []
        for index_row in range(len(nonRelated_rows)):
            final_row = list(range(len(columns)))
            for index_col, col in enumerate(columns):
                if col in nonRelated:
                    final_row[index_col] = nonRelated_rows[index_row][nonRelated.index(col)]
                elif col in related:
                    values = related_rows[index_row][related.index(col)]
                    final_row[index_col] = [] if values is None else [int(v) for v in values.split(',')]

            final_rows.append(final_row)
        
        con.close()
        return final_rows
    
    def filter(self, **kwargs):
        return QuerySet(self.name, self.fields, self.sliced, {**self.kwargs, **kwargs})
    
    def get(self, **kwargs):
        return self.filter(**kwargs)[0]
    
    def __getitem__(self, key):
        if type(key) == int:
            key = slice(0, key)
        elif type(key) == str:
            return self.values(key)
        return QuerySet(self.name, self.fields, key, self.kwargs)
        
    
    def __getattr__(self, name):
        # to-do: add validation step
        if name == "id":
            return self.values(name)[0][0]
        else:
            return self.values(name)[0][1]
    
    def __setattr__(self, name, value):
        # to-do: add validation step
        self.update(**{ name: value })

    def create(self, **kwargs):
        f = self.fields
        for key, value in f["fields"].items():
            if key not in kwargs and value.required and key != "id":
                raise Exception(f"Column '{key}' is required.")
            elif key in f["related"] and type(kwargs[key]) != list:
                raise Exception(f"Column '{key}' must be a list.")

        # nonRelated columns
        keys = [key for key in kwargs.keys() if key in f["nonRelated"]]
        values = [kwargs[key] for key in keys]

        query = f"""
            INSERT INTO {self.name}
            ({",".join(keys)})
            VALUES ({",".join([escape_str(v) for v in values])});
        """
        con = sqlite3.connect("db.sqlite3", autocommit=True)
        con.execute(query)

        last_id = next(con.execute("SELECT last_insert_rowid()"))[0]

        # related columns
        query = ""
        for related in f["related"]:
            field = f["fields"][related]
            values = kwargs[related]
            if len(values) == 0:
                continue
            query += f"""
                INSERT INTO relationship_{field.first}_{related}_{field.second}
                (first, second)
                VALUES {",".join([f"({last_id}, {escape_str(obj.id)})" for obj in values])};
            """    
        con.executescript(query)
        con.close()

        return self.get(id=last_id)

def builder(model):
    model.objects = QuerySet(model.__name__, model._fields())
    return model

class Model:
    @classmethod
    def _fields(self):
        fields = [field for field in dir(self) if field[0] != '_']

        fields = {
            field: getattr(self, field)
            for field in fields
            if field not in reserved
        }
        fields["id"] = IntField()

        for field, field_class in fields.items():
            if isinstance(field_class, RelatedField):
                fields[field].set_first(self.__name__)

        related = [
            field
            for field, field_class in fields.items()
            if isinstance(field_class, RelatedField)
                and field not in reserved
        ]
        nonRelated = [
            field
            for field, field_class in fields.items() 
            if not isinstance(field_class, RelatedField)
                and field not in reserved
        ]

        for field in related:
            fields[field].set_first(self.__name__)

        return dict(
            fields=fields,
            related=related,
            nonRelated=nonRelated
        )

    @classmethod
    def make_migration(cls):#, db: sql.SQLDatabase, name: str = None):
        return create_tables(cls.__name__, cls._fields())
