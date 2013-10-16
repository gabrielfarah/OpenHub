'''
Created on 12/10/2013

@author: Gabrie
'''
import os, re

def find_sql_injection(string):
    string  = string.replace(" ", "")
    return len(re.findall(r'\.execute\([\w\"\'\,\.\+=%]+[%][\w\"\'\,\.\+=%]+\)', string))
    
def find_burned_secret_key(string):
    string  = string.replace(" ", "")
    return len(re.findall(r'secret_key=', string))
        
def find_debug_mode_on(string):
    string  = string.replace(" ", "")
    return len(re.findall(r'debug=true', string))
    
def find_crypto(string):
    return len(re.findall(r' Crypto\.', string))
    
def find_md5(string):
    return len(re.findall(r'import[\s+\w+\,+]+md5', string))

def find_hashlib(string):
    return len(re.findall(r'import[\s+\w+\,+]+hashlib', string))

def find_ssl(string):
    return len(re.findall(r'import[\s+\w+\,+]+ssl', string))

def run_test(id, path, repo_db):
    sql_injection_flaws = 0
    burned_secret_keys = 0
    debug_mode_on = False
    use_crypto = False
    response = {}
    for root, subFolders, files in os.walk(path):
        for n_file in files:
            if (n_file.endswith('.py')):
                #print file
                with open(os.path.join(root, n_file), 'r') as content_file:
                    content = content_file.readlines()
                    for line in content:
                        n_line = line.lower()
                        sql_injection_flaws += find_sql_injection(n_line)
                        burned_secret_keys += find_burned_secret_key(n_line)
                        if find_debug_mode_on(n_line) != 0:
                            debug_mode_on = True
                        if find_crypto(n_line) != 0 or find_md5(n_line) != 0 or find_hashlib(n_line) != 0 or find_ssl(n_line) != 0:
                            use_crypto = True
                content_file.close()
    response["sql_injections"] = sql_injection_flaws
    response["burned_secret_keys"] = burned_secret_keys
    response["debug_mode_on"] = debug_mode_on
    response["use_crypto"] = use_crypto
    return response


if __name__ == '__main__':
    #===========================================================================
    # print find_sql_injection("asdfasdf.execute( query % params) asdf")
    # print find_sql_injection("asdfasdf.execute( \"query\" % params) asdf")
    # print find_sql_injection("asdfasdf.execute( \"select table_users where id = \" % params) asdf")
    # print find_crypto("import sha5, md5")
    # print find_crypto("import md5")
    # print find_crypto("import sha5, md6,md5")
    # print find_crypto("from Crypto.Hash import MD5")
    # print find_hashlib("import sha5, md6,md5, hashlib")
    # print find_ssl("import sha5, md6,md5, ssl, hashlib")
    # print find_crypto("import sha5, md6,md5, ssl, hashlib")
    # print find_debug_mode_on(""" <html> asdfasdf sdfasdfsdfa  import asdfasdf asdfaasdfa  asdfadf sadfasdfasdf   debug = true """)
    # print find_xss_defense(""" < .html> asdfasdf sdfasdfsdfa  import asdfasdf asdfaasdfa  asdfadf sadfasdfasdf   debug = true  hghgfgfjgh  render """ )
    # print find_xss_defense(""" < .html> asdfasdf  template sdfasdfsdfa  import .escape asdfasdf asdfaasdfa  asdfadf sadfasdfasdf   debug = true  hghgfgfjgh  render """ )
    #===========================================================================
    print run_test(None, os.path.dirname(__file__), None)
