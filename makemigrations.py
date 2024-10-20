import importlib
import os

MIGRATIONS_REGEX = r'__migration__(\d+).py'

MIGRATIONS_FOLDER = 'migrations'

def main():
    print('MAKING MIGRATIONS...')
    
    if not os.path.exists(MIGRATIONS_FOLDER):
        os.makedirs('migrations')

    if not os.path.isdir(MIGRATIONS_FOLDER):
        raise RuntimeError("Bad directory, can't store migrations because already exists a file called 'migrations'.")
    
    # to-do: big file with all create tables
    source = ""
    models = importlib.import_module("models")
    for model in models.ModelExportation:
        source += model.make_migration() + "\n"
    with open(f'{MIGRATIONS_FOLDER}/0.sql', 'w') as fh:
        fh.write(source)  
