import sqlite3

from field import *

reserved = ["make_migration", "fields", "objects", 'create', "filter", "get", "build_objects"]

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


class Objects:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def create(self, **kwargs):
        query = f"""
            INSERT INTO {self.name} ({",".join(kwargs.keys())})
            VALUES ({",".join(kwargs.values())});
        """
        con = sqlite3.connect("db.sqlite3", autocommit=True)
        con.execute(query)
        con.close()

class QuerySet:
    def __init__(self, name, fields, sliced=slice(0, 10, 1), kwargs={}):
        self.name = name
        self.fields = fields
        self.sliced = sliced
        self.kwargs = kwargs
    
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
        if "id" not in columns:
            columns.insert(0, "id")

        # nonRelated columns
        nonRelated = [col for col in columns if col in self.fields["nonRelated"]]
        nonRelated_str = ",".join(nonRelated)
        if nonRelated_str == "":
            nonRelated_str = "id"
        nonRelated_kwargs_str = " AND ".join([
            f"{key} = {value}"  # to-do: other conditions
            for key, value in self.kwargs.items()
            if key in nonRelated
        ])
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
        related_kwargs_str = " AND ".join([
            f"{key} = {value}"
            for key, value in self.kwargs.items()
            if key in related
        ])
        if related_kwargs_str == "":
            related_kwargs_str = "1"
        select_str = ""
        joins_str = ""
        for index, col in enumerate(related):
            field = self.fields["fields"][col]
            rel_table = f"relationship_{field.first}_{col}_{field.second}"
            joins_str += f"""
                LEFT JOIN {rel_table} rt{index}
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
                    final_row[index_col] = [int(v) for v in related_rows[index_row][related.index(col)].split(',')]
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
        if name not in self.fields["fields"] and name not in self.fields["related"]:
            raise Exception("Column doesn't exist.")
        if name == "id":
            return self.values(name)[0][0]
        else:
            return self.values(name)[0][1]
    # done
    def create(self, **kwargs):
        f = self.fields
        for key, value in f["fields"].items():
            if key not in kwargs and value.required and key != "id":
                raise Exception(f"Column '{key}' is required.")
            elif key in f["related"] and type(kwargs[key]) != list:
                raise Exception(f"Column '{key}' must be a list.")

        keys = [key for key in kwargs.keys() if key in f["nonRelated"]]
        values = [kwargs[key] for key in keys]

        query = f"""
            INSERT INTO {self.name}
            ({",".join(keys)})
            VALUES ({",".join([str(v) if type(v) != str else f"\"{v}\"" for v in values])});
        """
        con = sqlite3.connect("db.sqlite3", autocommit=True)
        con.execute(query)
        last_id = next(con.execute("SELECT last_insert_rowid()"))[0]
        con.close()

        for related in f["related"]:
            field = f["fields"][related]
            values = kwargs[related]
            # to-do: accept queryset
            query = f"""
                INSERT INTO relationship_{field.first}_{related}_{field.second}
                (first, second)
                VALUES {",".join([f"({last_id}, {value})" for value in values])};
            """
            con = sqlite3.connect("db.sqlite3", autocommit=True)
            # print(193, query)
            con.execute(query)
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

        related = [field for field, field_class in fields.items() if isinstance(field_class, RelatedField) and field not in reserved]
        nonRelated = [field for field, field_class in fields.items() if not isinstance(field_class, RelatedField) and field not in reserved]

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
