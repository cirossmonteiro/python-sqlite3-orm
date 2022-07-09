import enum

class SQLITE3_TYPES(enum.Enum):
    INTEGER = 'INTEGER'
    BLOB = 'BLOB'
    REAL = 'REAL'
    NUMERIC = 'NUMERIC'
    TEXT = 'TEXT'


MAP_TYPES_PYTHON_TO_SQLITE3 = {
    int: SQLITE3_TYPES.INTEGER.value,
    float: SQLITE3_TYPES.REAL.value,
    str: SQLITE3_TYPES.TEXT.value
}

MAP_TYPES_SQLITE3_TO_PYTHON = {
    SQLITE3_TYPES.INTEGER.value: int,
    SQLITE3_TYPES.REAL.value: float,
    SQLITE3_TYPES.TEXT.value: str
}
