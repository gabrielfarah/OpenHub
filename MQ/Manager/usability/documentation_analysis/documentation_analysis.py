'''
Created on Aug 18, 2013

@author: Gabriel Farah
'''
from markdown import markdown
import sys
from bs4 import BeautifulSoup
from sklearn.externals import joblib
import numpy as np

def chomp(s):
    return s[:-1] if s.endswith('\n') else s

def analyze(local_code_path):
    list = ""
    with open(local_code_path, 'r') as content_file:
        content = content_file.read()
        html = markdown(content)
        soup = BeautifulSoup(html)
        #------------------------------- text = ''.join(soup.findAll(text=True))
        for element in ('h2','h3','h4','h5','h6'):
            for link in soup.find_all(element):
                list = list+" "+link.text
        #Load the saved classifier
        classifier = joblib.load('./pickles/classifier.pkl')
        #convert our list of headers to an array
        X_test = np.array([list])
        target_names = ['Bad', 'Average', 'Good']
        #predict the class
        predicted = classifier.predict(X_test)
        for labels in  predicted:
            print '%s' % (', '.join(target_names[x] for x in labels))
    return 0

#===============================================================================
# if __name__=='__main__':
#     analyze(sys.argv[1])
#===============================================================================
    
analyze("README.md")