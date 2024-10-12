import os
import sqlite3

MIGRATIONS_REGEX = r'__migration__(\d+).py'

MIGRATIONS_FOLDER = 'migrations'

def main():
    print('MIGRATING...')
    con = sqlite3.connect("db.sqlite3")
    files = [f for f in os.listdir(MIGRATIONS_FOLDER) if os.path.isfile(f'{MIGRATIONS_FOLDER}/{f}')]
    for file in files:
        with open(f'{MIGRATIONS_FOLDER}/{file}') as fh:
            con.executescript(fh.read())
    con.close()