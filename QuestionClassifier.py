"""
This module is used to train and use a model that is able to predict the relation
underlying a question pattern.
"""
import json
from math import floor
import os
from MarkovChain import MarkovChain
import pickle
from random import randint
from nltk import word_tokenize
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

    if not(os.path.isfile("tmp_training_questions.bin")):

        if os.path.isfile('tmp_test.bin'):
            training = pickle.load(open('tmp_training.bin', 'rb'))
            test = pickle.load(open('tmp_test.bin', 'rb'))
            
        else:
            print("splitting dataset")
            training, test = get_training_test_set(jdata, split=0.2)
            pickle.dump(training, open('tmp_training.bin', 'wb'))
            pickle.dump(test, open("tmp_test.bin", 'wb'))
            del jdata

        print("start preprocessing")
        X_training, Y_training = preprocess_data(training)
        del training
        X_test, Y_test = preprocess_data(test)
        del test

        # now we have to divide each question by category

        training_questions = dict()

        for i in range(len(Y_training)):
            la = Y_training[i]
            try:
                training_questions[la] += [X_training[i]]
            except KeyError:
                training_questions[la] = [X_training[i]]
        
        pickle.dump(training_questions, open("tmp_training_questions.bin", 'wb'))
        del X_training
        del Y_training

        test_questions = dict()

        for i in range(len(Y_test)):
            la = Y_test[i]
            try:
                test_questions[la] += [X_test[i]]
            except KeyError:
                test_questions[la] = [X_test[i]]
        
        pickle.dump(test_questions, open("tmp_test_questions.bin", 'wb'))
        del X_test
        del Y_test
    else:
        training_questions = pickle.load(open("tmp_training_questions.bin", 'rb'))
        test_questions = pickle.load(open("tmp_test_questions.bin", 'rb'))
   
    print("dataset preprocessed", "Start training")
    
    models = dict()
    for k in training_questions.keys():
        models[k] = MarkovChain()
        print("training model for", k)
        models[k].train_model(training_questions[k])

train_question_to_relation()