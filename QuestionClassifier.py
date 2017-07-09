"""
This module is used to train and use a model that is able to predict the relation
underlying a question pattern.
"""
import keras
import json

PATH_TO_GLOVE = "models/glove.bin"
PATH_TO_KB = "full_kb.txt"

def _get_next_dict():
    data = json.load(open(PATH_TO_KB))
    for d in data:
        yield d

def preprocess_training_set():
    """
    this function loads the full knowledge base and extract (question, relation) pairs.
    For each question, subject and object are removed in order to make classification
    easier.
    """
    X, Y = list(), list()
    for d in _get_next_dict():
        question = d['question']
        c1 = d['c1']
        c2 = d['c2']
        Y.append(d['relation'])
        if '::' is in c1 and '::' is in c2:
            c1 = c1[:c1.index('::')]
            c2 = c2[:c2.index('::')]
            question = question.replace(c1, 'X').replace(c2, 'Y')
        else:
            print("Missing ::", c1, c2)
        X.append(question)
        



def train_question_to_relation():
    """
    this function is used to train a LSTM Network that, given as input a question,
    predicts the underlying relation between the entities.
    """