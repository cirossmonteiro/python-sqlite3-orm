import importlib
import os
import shutil
import unittest

import field

from makemigrations import main as makemigrations
from migrate import main as migrate

import sqlite3

print(sqlite3.sqlite_version)

class Test(unittest.TestCase):
    
    def setUp(self):
        with open('mock/models.py') as fh_read:
            with open('models.py', 'w') as fh_write:
                fh_write.write(fh_read.read())
        makemigrations()
        migrate()
    
    def tearDown(self):
        # careful here
        os.remove('models.py')
        os.remove("db.sqlite3")
        shutil.rmtree('./migrations/')
    
    def test_fields(self):
        self.fieldIntField = field.IntField()
        self.assertTrue(self.fieldIntField.validate(1))
        self.assertFalse(self.fieldIntField.validate(1.0))
        
        self.fieldStringfied = field.StringField()
        self.assertTrue(self.fieldStringfied.validate("hello, world"))
        self.assertFalse(self.fieldStringfied.validate(1))
        
        self.fieldFloatField = field.FloatField()
        self.assertTrue(self.fieldFloatField.validate(1.0))
        self.assertFalse(self.fieldFloatField.validate(1))

    def test_main(self):
        models = importlib.import_module("models")

        test11 = models.ModelExportation[0].objects.create(
            fieldIntfield=1,
            fieldFloatfield=2.5,
            fieldStringfield="Hello, world!"
        )
        self.assertEqual(test11.fieldIntfield, 1)
        self.assertEqual(test11.fieldFloatfield, 2.5)
        self.assertEqual(test11.fieldStringfield, "Hello, world!")
        test11.fieldStringfield = "Hello, there!"
        self.assertEqual(test11.fieldStringfield, "Hello, there!")

        test12 = models.ModelExportation[0].objects.create(
            fieldIntfield=2,
            fieldFloatfield=3,
            fieldStringfield="Hello, my world!"
        )

        test2 = models.ModelExportation[1].objects.create(
            fieldIntfield=1,
            fieldFloatfield=2.5,
            fieldStringfield="Hello, world!",
            fieldForeignkeyfield=[test11,test12],
            fieldForeignkeyfield2=[]
        )
        self.assertEqual(test2.id, 1)
        self.assertListEqual(test2.fieldForeignkeyfield, [test11.id,test12.id])
        self.assertListEqual(test2.fieldForeignkeyfield2, [])
        test2.fieldForeignkeyfield = [test12,test11]
        self.assertListEqual(test2.fieldForeignkeyfield, [test12.id, test11.id])
            

if __name__ == '__main__':
    unittest.main()