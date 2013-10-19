'''
Created on 18/10/2013

@author: Gabrie
'''
import unittest
import main as m


class Test(unittest.TestCase):

    def test_SQL_Injection(self):
        """Found string sql param in python in file."""
        assert m.find_sql_injection("asdfasdf.execute( query % params) asdf") == 1 
        assert m.find_sql_injection("asdfasdf.execute( \"select table_users where id = \" % params) asdf") == 1
        assert m.find_sql_injection("asdfasdf.execute( \"select table_users where id = \" , params) asdf") == 0
        
    def test_pycrypt_library(self):
        """Found pycrypt library usage in python in file."""
        assert m.find_crypto("from Crypto.Hash import MD5") == 1
        assert m.find_crypto("from  import MD5") == 0
        
    def test_hashlib_library(self):
        """Found hashlib library usage in python in file."""
        assert m.find_hashlib("import sha5, md6,md5, hashlib") == 1
        assert m.find_hashlib("import sha5, md6,md5, ") == 0
        
    def test_debug_mode_true(self):
        """Found hashlib library usage in python in file."""
        assert m.find_debug_mode_on(""" <html> asdfasdf sdfasdfsdfa  import asdfasdf asdfaasdfa  asdfadf sadfasdfasdf   debug = true """) == 1
        assert m.find_debug_mode_on(""" <html> asdfasdf sdfasdfsdfa  import asdfasdf asdfaasdfa  asdfadf sadfasdfasdf   debug = false """) == 0


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()