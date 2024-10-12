import importlib
import os
import shutil
import unittest

from test_commons import TestCase

from makemigrations import main as makemigrations
from migrate import main as migrate

class Test(TestCase):
    
    def setUpExtra(self):
        with open('mock/models.py') as fh_read:
            with open('models.py', 'w') as fh_write:
                fh_write.write(fh_read.read())
    
    def tearDown(self):
        # careful here
        os.remove('models.py')
        os.remove("db.sqlite3")
        shutil.rmtree('./migrations/') 

    def test_main(self):
        makemigrations()
        migrate()
        models = importlib.import_module("models")

        test11 = models.ModelExportation[0].objects.create(
            fieldIntfield=1,
            fieldFloatfield=2.5,
            fieldStringfield="Hello, world!"
        )
        self.assertEqual(test11.fieldIntfield, 1)
        self.assertEqual(test11.fieldFloatfield, 2.5)
        self.assertEqual(test11.fieldStringfield, "Hello, world!")

        test12 = models.ModelExportation[0].objects.create(
            fieldIntfield=2,
            fieldFloatfield=3,
            fieldStringfield="Hello, my world!"
        )

        test2 = models.ModelExportation[1].objects.create(
            fieldIntfield=1,
            fieldFloatfield=2.5,
            fieldStringfield="Hello, world!",
            fieldForeignkeyfield=[test11.id,test12.id]
        )
        self.assertEqual(test2.id, 1)
        self.assertListEqual(test2.fieldForeignkeyfield, [test11.id,test12.id])
            

if __name__ == '__main__':
    unittest.main()