'''
Created on Aug 18, 2013

@author: Gabriel Farah
'''
from markdown import markdown
import sys
from bs4 import BeautifulSoup
from sklearn.externals import joblib
import numpy as np
import os

def features_extraction(clean_html):
    result_list = ""
    soup = BeautifulSoup(clean_html)
    #------------------------------- text = ''.join(soup.findAll(text=True))
    tags = ['h2','h3','h4','h5','h6']
    for link in soup.find_all(tags):
        temp_text = link.text
        for ch in ['&','#','_','?','.','-','1','2','3','4','5','6','7','8','9','0']:
            if ch in temp_text:
                temp_text=temp_text.replace(ch," ")
        result_list = result_list+" "+temp_text
    return result_list

def load_and_clear_file(local_path):
    with open(local_path, 'r') as content_file:
        content = content_file.read()
    content_file.close()
    return markdown(content)

def run_test(id, path, repo_db):
    for root, subFolders, files in os.walk(path):
        for f in files:
            if (f.endswith('.md') or f.endswith('.rst') or f.endswith('.rdoc')) and not 'license' in f.lower():
                clean_html = load_and_clear_file(os.path.join(root, f))
                result_list = features_extraction(clean_html)
                #Load the saved classifier
                classifier = joblib.load('./pickles/classifier.pkl')
                #convert our list of headers to an array
                X_test = np.array([result_list])
                target_names = ['Bad', 'Average', 'Good']
                #predict the class
                predicted = classifier.predict(X_test)
                for labels in  predicted:
                    return '%s' % (', '.join(target_names[x] for x in labels))


if __name__=='__main__':
    run_test(None, os.path.dirname(__file__), None)
