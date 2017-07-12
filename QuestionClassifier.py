"""
This module is used to train and use a model that is able to predict the relation
underlying a question pattern.
"""
import LSTMSentenceClassifier as lstm
from LSTMSentenceClassifier import LSTMSentenceClassifier
import json
from math import floor
import os
import pickle
from random import randint
from nltk import word_tokenize
PATH_TO_GLOVE = "models/glove.bin"
PATH_TO_KB = "full_kb.txt"

def find_labels(jdata):
    
    if os.path.isfile('tmp_labels.bin'):
        return pickle.load(open('tmp_labels.bin', 'rb'))
    labels = set()
    for d in jdata:
        labels.add(d['relation'])
    
    pickle.dump(labels, open('tmp_labels.bin', 'wb'))
    return labels

def preprocess_data(jdata):
    """
    this function loads the full knowledge base and extract (question, relation) pairs.
    For each question, subject and object are removed in order to make classification
    easier.
    """
    X, Y = list(), list()
    for d in jdata:
        question = d['question']
        c1 = d['c1']
        c2 = d['c2']
        Y.append(d['relation'])
        if ':' in c1 and ':' in c2:
            c1 = c1[:c1.index(':')]
            c2 = c2[:c2.index(':')]
            question = question.replace(c1, 'X').replace(c2, 'Y')
            #print("Missing :", c1, c2)

        tokenized = word_tokenize(question)
        X.append(tokenized)
    return X, Y

def get_training_test_set(X, split=0.5, bsize=2000):
    """
    divides the dataset in training and test set.
    """
    N = len(X)
    Tsize = floor((N/bsize)*split)

    test_X = list()
    training_X = list()
    remaining_indexes = list(range(0, N, bsize))
    selected_test = 0
    while selected_test < Tsize:
        t = len(remaining_indexes) - 1
        if t == 0:
            break
        j = randint(0, t)
        i = remaining_indexes[j]
        test_X += X[i:i+bsize]
        del remaining_indexes[j]
        selected_test += 1
       
    for i in remaining_indexes:
        training_X += X[i:i+bsize]
      
    return training_X, test_X

def train_question_to_relation():
    """
    this function is used to train a LSTM Network that, given as input a question,
    predicts the underlying relation between the entities.
    """
    #jdata = json.load(open('full_kb.txt'))
    jdata = None
    if not os.path.isfile('tmp_training.bin'):
        jdata = pickle.load(open("test_data.bin", 'rb'))
    labels = find_labels(jdata)

    LSTMCL = lstm.LSTMSentenceClassifier()
    LSTMCL.set_labels(labels)

    if not(os.path.isfile("tmp_x_training.bin")):

        if os.path.isfile('tmp_test.bin'):
            training = pickle.load(open('tmp_training.bin', 'rb'))
            test = pickle.load(open('tmp_test.bin', 'rb'))
            
        else:
            print("splitting dataset")
            training, test = get_training_test_set(jdata, split=0.3)
            pickle.dump(training, open('tmp_training.bin', 'wb'))
            pickle.dump(test, open("tmp_test.bin", 'wb'))
            del jdata

        print("start preprocessing")
        X_training, Y_training = preprocess_data(training)
        del training
        X_test, Y_test = preprocess_data(test)
        del test

        X_training = LSTMCL.preprocess_input_sentences(X_training)
        X_test = LSTMCL.preprocess_input_sentences(X_test)
        Y_training = LSTMCL.preprocess_labels(Y_training)
        Y_test = LSTMCL.preprocess_labels(Y_test)
        
        pickle.dump(X_training, open("tmp_x_training.bin", 'wb'))
        pickle.dump(Y_training, open("tmp_y_training.bin", 'wb'))
        pickle.dump(X_test, open("tmp_x_test.bin", 'wb'))
        pickle.dump(Y_test, open("tmp_y_test.bin", 'wb'))
    else:
        X_training = pickle.load(open("tmp_x_training.bin", 'rb'))
        Y_training = pickle.load(open("tmp_y_training.bin", 'rb'))
        X_test = pickle.load(open("tmp_x_test.bin", 'rb')) 
        Y_test = pickle.load(open("tmp_y_test.bin", 'rb'))

    

    print("dataset preprocessed")

    LSTMCL.train_LSTM_model(X_training, Y_training)
    cm = LSTMCL.test_model(X_test, Y_test)

    print(cm.getAccuracy())

train_question_to_relation()