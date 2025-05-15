import unittest
from file_functions import save_file, open_file, list_files, remove_file
from os import listdir, remove
from toon import Toon

class TestFileFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_save_file(self):
        a = {'name':'test','a':1,'b':2,'c':3}
        save_file(a, "test", "savefiletest")
        self.assertTrue("savefiletest.json" in [f for f in listdir("testing/") if f.endswith("json")])
    
    def test_open_file(self):
        a = {'name':'test','a':1,'b':2,'c':3}
        save_file(a, "test", "openfiletest")
        filename = "openfiletest"
        b = open_file(filename, "test")
        self.assertEqual(b, a)

    def test_list_files(self):
        save_file({}, "test", "listfiletest")
        files = list_files("test", "json")
        self.assertTrue("listfiletest.json" in files)

    def test_remove_file(self):
        save_file({}, "test", "remove")
        removed = remove_file("remove.json", "test")
        files = list_files("test", "json")
        self.assertTrue(removed)

    def tearDown(self):
        try:
            for file in [f for f in listdir("testing/") if f.endswith("json")]:
                remove("testing/" + file)
        except OSError as e:
           print(e)
        return super().tearDown()
          
class TestToonConfig(unittest.TestCase):
    def setUp(self):
        self.toon = Toon()

    def test_toon_properties(self):
        self.toon.set_name("test")
        self.assertEqual(self.toon.get_name(), "test")

        self.toon.set_race("test")
        self.assertEqual(self.toon.get_race(), "test")

        self.toon.add_class("test", 1)
        cls = {"clsname": "test", "level" : 1}
        classes = self.toon.get_classes()
        self.assertTrue(cls in classes)

    def tearDown(self):
        self.toon = None



if __name__ == '__main__':
      unittest.main()