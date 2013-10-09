'''
Created on Aug 18, 2013

@author: gabo
'''
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
import os
import documentation_analysis

training_list_X = []
training_list_Y = []
training_data_paths = ["./training_data/bad/","./training_data/average/","./training_data/good/"]
for path in training_data_paths:
    files = [ f for f in os.listdir(path) ]
    for f in files:
        clean_html = documentation_analysis.load_and_clear_file(path + f)
        result_list = documentation_analysis.features_extraction(clean_html)
        training_list_X.append(result_list)
        if path is "./training_data/bad/":
            training_list_Y.append([0])
        elif path is "./training_data/average/":
            training_list_Y.append([1])
        else:
            training_list_Y.append([2])
X_train = np.array(training_list_X)
y_train = training_list_Y
#===============================================================================
# target_names = ['New York', 'London']
#===============================================================================

classifier = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', OneVsRestClassifier(LinearSVC()))])
classifier.fit(X_train, y_train)

joblib.dump(classifier, './pickles/classifier.pkl', compress=3)
#===============================================================================
# classifier2 = joblib.load('./pickles/classifier.pkl')
# predicted = classifier2.predict(X_test)
# for item, labels in zip(X_test, predicted):
#     print '%s => %s' % (item, ', '.join(target_names[x] for x in labels))
#===============================================================================
