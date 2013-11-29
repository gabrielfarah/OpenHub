'''
Created on 18/10/2013

@author: Gabrie
'''
import unittest
import main as m


class Test(unittest.TestCase):
    self.content = None

    def setUp(self):
        with open("./main.py", 'r') as content_file:
            self.content = content_file.read()
        content_file.close()


    def tearDown(self):
        pass


    def test_metrics(self):
        assert m.get_maintenability_index(self.content) != None
        assert m.get_code_metrics(self.content) != None


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
