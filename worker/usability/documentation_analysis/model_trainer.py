'''
Created on Aug 18, 2013

@author: gabo
'''
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB
import os
from markdown import markdown
import sys
from bs4 import BeautifulSoup

def features_extraction(clean_html):
    result_list = ""
    soup = BeautifulSoup(clean_html)
    #------------------------------- text = ''.join(soup.findAll(text=True))
    tags = ['b','h1','h2','h3','h4','h5','h6']
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
    return markdown(content.decode('utf-8'))

training_list_X = []
training_list_Y = []
training_data_paths = ["./training_data/bad/","./training_data/average/","./training_data/good/"]
for path in training_data_paths:
    files = [ f for f in os.listdir(path) ]
    for f in files:
        clean_html = load_and_clear_file(path + f)
        result_list = features_extraction(clean_html)
        training_list_X.append(result_list)
        if path is "./training_data/bad/":
            training_list_Y.append(0)
        elif path is "./training_data/average/":
            training_list_Y.append(1)
        else:
            training_list_Y.append(2)
X_train = np.array(training_list_X)
y_train = training_list_Y
#===============================================================================
# target_names = ['New York', 'London']
#===============================================================================

classifier = Pipeline([
    ('vectorizer', TfidfVectorizer(ngram_range=(1, 2))),
    ('clf', MultinomialNB())])
classifier.fit(X_train, y_train)

joblib.dump(classifier, './pickles/model.pkl', compress=0)

