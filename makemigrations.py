import os
import pickle
import re

import sql

MIGRATIONS_REGEX = r'__migration__(\d+).py'

MIGRATIONS_FOLDER = 'migrations'

db = sql.SQLDatabase('test.db')


def main():
    print('MAKING MIGRATIONS...')
    if os.path.exists(MIGRATIONS_FOLDER):
        if os.path.isdir(MIGRATIONS_FOLDER):
            print(18)
            files = [f for f in os.listdir(MIGRATIONS_FOLDER) if os.path.isfile(f'{MIGRATIONS_FOLDER}/{f}')]
            migration_files = list(filter(lambda f: re.search(MIGRATIONS_REGEX, f),files))
            new_index = -1
            for mf in migration_files:
                index = int(re.search(MIGRATIONS_REGEX, mf).group(1))
                if index > new_index:
                    new_index = index
            new_index += 1
            new_migration_file = f"__migration__{new_index}.py"
            print(f"New migration file: {new_migration_file}.")
            migrations = []
            for table in db:
                migrations.append(table.makemigrations())
                print(f"Current table: {table.tablename}.")
            return migrations

            # check if table doesn't exist - create table
            # compare table schema with table dumped at db
            # check if changes are necessary - alter table
        else:
            raise RuntimeError("Bad directory, can't store migrations because already exists a file call 'migrations'.")
    else:
        os.makedirs('migrations')
    pass