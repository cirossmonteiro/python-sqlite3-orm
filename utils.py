import enum
import typing

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

def compute_transpositions(start: list, end: list):
    print(25, start, end)
    transpositions, size, start = [], len(start), start[:]
    for pivot in range(size-1): # when list has only one item left, then it's already over
        index = start.index(end[pivot])
        if pivot != index:
            transpositions.append((pivot, index))
            temp = start[pivot]
            start[pivot] = start[index]
            start[index] = temp
    return transpositions

def apply_transpositions(start: list, transpositions: typing.List[typing.Tuple[int, int]]):
    for tp in transpositions:
        temp = start[tp[0]]
        start[tp[0]] = start[tp[1]]
        start[tp[1]] = temp
    return start


        
