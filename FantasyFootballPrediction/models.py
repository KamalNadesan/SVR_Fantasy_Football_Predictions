# Copyright (c) Roman Lutz. All rights reserved.
# The use and distribution terms for this software are covered by the
# Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
# which can be found in the file LICENSE.md at the root of this distribution.
# By using this software in any fashion, you are agreeing to be bound by
# the terms of this license.
# You must not remove this notice, or any other, from this software.

import pdb
import numpy as np
from sklearn.svm import SVR
from sklearn import preprocessing
#from sklearn import cross_validation
from sklearn import feature_selection
from sklearn.metrics import mean_squared_error, mean_absolute_error 
from create_datasets import test_players
import time
from metrics import mean_relative_error
from plots import histogram
import sklearn.model_selection
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
import sklearn
import csv
import pandas as pd










def param_score(mean_score, params):
    ret = []
    kernel_type = 0
    if(params['kernel'] == 'linear'):
        kernel_type = 1
    elif(params['kernel'] == 'rbf'):
        kernel_type = 2
    elif(params['kernel'] == 'sigmoid'):
        kernel_type = 3
    elif(params['kernel'] == 'poly'):
        kernel_type = 4
    else:
        raise ValueError("Unexpected Kernel Type: " + str(kernel_type) + " For Parameters: " + str(params))
    ret.append(mean_score)
    ret.append(kernel_type)
    ret.append(params['degree'])
    ret.append(params['C'])
    ret.append(params['gamma'])
    ret.append(params['epsilon'])
    return(ret)




kernels = ['rbf', 'linear', 'sigmoid']
#degrees = [2, 3]
degrees = [2]
gamma_values = [0.05*k for k in range(1,4)]
C_values = [0.25*k for k in range(1, 5)]
epsilon_values = [0.05*k for k in range(1, 6)]



def hyperparameter(x, y):

    overall_best_params = open('overall_best_params.txt', 'w')
    
    ###
    """ MEAN ABSOLUTE """
    ###
    parameters = {'kernel':('linear', 'rbf', 'sigmoid'), 'degree':(degrees), 'C':(C_values), 'gamma':(gamma_values), 'epsilon':(epsilon_values)}
    svr = sklearn.svm.SVR()
    clf = sklearn.model_selection.GridSearchCV(svr, parameters, verbose=5, scoring='neg_mean_absolute_error')
    clf.fit(x, y)
    cvres = clf.cv_results_
    # iterate through all scores and params
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print(mean_score, params)
        # save each param and score to a file
        #wr.writerows(lst)
    print("Best Results For Training Mean Absolute Error: " + str(clf.best_params_))
    print("Best Results For Training Mean Absolute Error: " + str(clf.best_score_))
    #writer_Mean_Abs.close()

    # predict values for 2017
    best = clf.best_params_
    """
    best['C'] = (best['C'][0])
    best['gamma'] = float(best['gamma'][0])
    best['epsilon'] = float(best['epsilon'][0])
    best['degree']  = int(best['degree'][0])
    best['kernel'] = str(best['kernel'][0])
    """
    svr = sklearn.svm.SVR(C=best['C'], epsilon=best['epsilon'], kernel=best['kernel'], degree=best['degree'], gamma=best['gamma'])
    svr.fit(test_x, test_y)
    abs_mean_prediction = svr.predict(test_x)

    # save predictions
    writer = open('mean_absolute_results.csv', 'w')
    wr = csv.writer(writer, dialect='excel')
    legend = [['Predicted', 'Actual', 'Error', 'kernel', 'degree', 'C', 'gamma', 'epsilon']]
    wr.writerows(legend)
    data_set = []
    i=0
    for i in range(len(test_y)):
        values = [-1, -1, -1, -1, -1, -1, -1, -1]
        values[0] = abs_mean_prediction[i]
        values[1] = test_y[i]
        values[2] = mean_absolute_error(test_y, abs_mean_prediction)
        values[3] = best['kernel']
        values[4] = best['degree']
        values[5] = best['C']
        values[6] = best['gamma']
        values[7] = best['epsilon']
        values = [values]
        wr.writerows(values)
    writer.close()



    #pdb.set_trace()
    
    ###
    """ MEAN SQUARED """
    ###
    
    writer_Mean_Squared = open('mean_squared_results.csv', 'w')
    wr = csv.writer(writer_Mean_Squared, dialect='excel')
    legend = [['Predicted', 'Actual', 'Error', 'kernel', 'degree', 'C', 'gamma', 'epsilon']]
    wr.writerows(legend)
    
    # save all results in a dict that will be sorted to get top 5 results
    top_params_ms = {}
    parameters = {'kernel':('linear', 'rbf', 'sigmoid'), 'degree':(degrees), 'C':(C_values), 'gamma':(gamma_values), 'epsilon':(epsilon_values)}
    svr = sklearn.svm.SVR()
    clf = sklearn.model_selection.GridSearchCV(svr, parameters, verbose=5, scoring='neg_mean_squared_error')
    clf.fit(x, y)
    cvres = clf.cv_results_
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print(mean_score, params)
        # save each param and score to a file
        #lst = [param_score(mean_score, params)]
        #wr.writerows(lst)
    print("Best Results For Training Mean Squared Error: " + str(clf.best_params_))
    print("Best Results For Training Mean Squared Error: " + str(clf.best_score_))

    # predict values for 2017
    best = clf.best_params_
    """
    best['C']       = float(best['C'][0])
    best['gamma']   = float(best['gamma'][0])
    best['epsilon'] = float(best['epsilon'][0])
    best['degree']  = int(best['degree'][0])
    best['kernel']  = str(best['kernel'][0])
    """
    svr = sklearn.svm.SVR(C=best['C'], epsilon=best['epsilon'], kernel=best['kernel'], degree=best['degree'], gamma=best['gamma'])
    #pdb.set_trace()
    svr.fit(test_x, test_y)
    mean_squared_prediction = svr.predict(test_x)

    for i in range(len(test_y)):
        values = [-1, -1, -1, -1, -1, -1, -1, -1]
        values[0] = mean_squared_prediction[i]
        values[1] = test_y[i]
        values[2] = sklearn.metrics.mean_squared_error(test_y, mean_squared_prediction)
        values[3] = best['kernel']
        values[4] = best['degree']
        values[5] = best['C']
        values[6] = best['gamma']
        values[7] = best['epsilon']
        values = [values]
        wr.writerows(values)

    print("Mean Squared Error Finished")
    writer_Mean_Squared.close()


    
    
    ###
    """ Absolute Median """ 
    ###

    writer_Median_Squared = open('median_absolute_results.csv', 'w')
    wr = csv.writer(writer_Median_Squared, dialect='excel')
    legend = [['Predicted', 'Actual', 'Error', 'kernel', 'degree', 'C', 'gamma', 'epsilon']]
    wr.writerows(legend)
    
    # save all results in a dict that will be sorted to get top 5 results
    top_params_ms = {}
    parameters = {'kernel':('linear', 'rbf', 'sigmoid'), 'degree':(degrees), 'C':(C_values), 'gamma':(gamma_values), 'epsilon':(epsilon_values)}
    svr = sklearn.svm.SVR()
    clf = sklearn.model_selection.GridSearchCV(svr, parameters, verbose=5, scoring='neg_median_absolute_error')
    clf.fit(x, y)
    cvres = clf.cv_results_
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print(mean_score, params)
        # save each param and score to a file
        #lst = [param_score(mean_score, params)]
        #wr.writerows(lst)
    print("Best Results For Training Median Absolute Error: " + str(clf.best_params_))
    print("Best Results For Training Median Absolute Error: " + str(clf.best_score_))

    # predict values for 2017
    best = clf.best_params_
    svr = sklearn.svm.SVR(C=best['C'], epsilon=best['epsilon'], kernel=best['kernel'], degree=best['degree'], gamma=best['gamma'])
    #pdb.set_trace()
    svr.fit(test_x, test_y)
    median_absolute_prediction = svr.predict(test_x)
    for i in range(len(test_y)):
        values = [-1, -1, -1, -1, -1, -1, -1, -1]
        values[0] = median_absolute_prediction[i]
        values[1] = test_y[i]
        values[2] = sklearn.metrics.median_absolute_error(test_y, median_absolute_prediction)
        values[3] = best['kernel']
        values[4] = best['degree']
        values[5] = best['C']
        values[6] = best['gamma']
        values[7] = best['epsilon']
        values = [values]
        wr.writerows(values)















    overall_best_params.close()
    print("FEATURE SELECTION FINISHED")
















# Only one of the feature selection methods can be chosen
FEATURE_SELECTION = False
MANUAL_FEATURE_SELECTION = False
FEATURE_NORMALIZATION = False
HYPERPARAMETER_SELECTION = True
HISTOGRAM = True


train = np.load('train.npy')
test  = np.load('test.npy')

""" should add opponent"""
    # row consists of
    # 0: QB id
    # 1: QB name
    # 2: QB age
    # 3: QB years pro
    # 4: Last game opponent (values in map_opponent(opponent))
    # 5: Last game home(1.0) or away(0.0)
    # 6-18: last game QB stats
    # 19-31: last 10 games QB stats
    # 32-35: last game defense stats
    # 36-39: last 10 games defense stats
    # 40: actual fantasy score = target

train_x = train[:, 2:40].astype(np.float)
train_y = train[:, 40].astype(np.float)
test_x  = test[:, 2:40].astype(np.float)
test_y  = test[:, 40].astype(np.float)
#pdb.set_trace()
"""
train_x = pd.DataFrame(train_x)
train_y = pd.DataFrame(train_y)
test_x  = pd.DataFrame(test_x)
test_y  = pd.DataFrame(test_y)
"""



""" NOTE: Poly kernel is not running for some reason, infinite loop behavior """
#kernels = ['rbf', 'linear', 'sigmoid', 'poly']
kernels = ['rbf', 'linear', 'sigmoid']
#degrees = [2, 3]
degrees = [2]
gamma_values = [0.05*k for k in range(1,4)]
C_values = [0.25*k for k in range(1, 5)]
epsilon_values = [0.05*k for k in range(1, 6)]

# Feature Normalization
if FEATURE_NORMALIZATION:
    print 'started feature normalization', time.time()
    x = np.concatenate((train_x, test_x), axis=0)
    x = preprocessing.scale(x)
    train_x = x[:len(train_x)]
    test_x  = x[len(train_x):]

# Recursive Feature Elimination with cross-validation (RFECV)
if FEATURE_SELECTION:
    print('Started Feature Selection (LINEAR)', time.time())
    selector = feature_selection.RFECV(estimator=SVR(kernel='linear'), step=1, cv=5)
    selector.fit(train_x, train_y)
    train_x = selector.transform(train_x)
    test_x  = selector.transform(test_x)
    print("For Linear Kernel: ")
    print(selector.ranking_)

    print('Started Feature Selection (RBF)', time.time())
    selector = feature_selection.RFECV(estimator=SVR(kernel='rbf'), step=1, cv=5)
    selector.fit(train_x, train_y)
    train_x = selector.transform(train_x)
    test_x  = selector.transform(test_x)
    print("For RBF Kernel: ")
    print(selector.ranking_)

    print('Started Feature Selection (SIGMOID)', time.time())
    selector = feature_selection.RFECV(estimator=SVR(kernel='sigmoid'), step=1, cv=5)
    selector.fit(train_x, train_y)
    train_x = selector.transform(train_x)
    test_x  = selector.transform(test_x)
    print("For SIGMOID Kernel: ")
    print(selector.ranking_)



    print("RECRUSIVE FEATURE SELECTION FINISHED")

# Manual Feature Selection
elif MANUAL_FEATURE_SELECTION: # leave out the two point attempts
    manual_indices = [0, 1, 2, 3, 4, 5, 8, 9, 10, 13, 14, 15, 16, 17, 20, 21, 22, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    train_x = train_x[:, manual_indices]
    test_x  = test_x[:, manual_indices]

# Hyperparameter Selection
if HYPERPARAMETER_SELECTION:
    hyperparameter(train_x, train_y)
