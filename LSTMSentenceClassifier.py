"""
This module provides a fast interface to LSTM implementation in keras, in particular
to deal with sequences of words.
"""
import keras
import pickle
import numpy
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.layers.recurrent import LSTM

_word_vect = None
_vect_size = 0

def load_word_vect(binary_dump):
    """
    loads the word vectors dictionary, that maps words to their distributed
    representation.

    Parameters:
    ------------
        - binary_dump: path to a file that is a pickle dump of the dictionary
          created with word2vect or glove.
    """
    _word_vect = pickle.load(open(binary_dump, 'rb'))
    _vect_size = len(_word_vect.values()[0])
    return

def _word_lookup(word):
    """
    returns the distributional representation of a word, if exists. Returns the
    0 vector otherwise.
    """
    try:
        return _word_vect[word]
    except:
        return numpy.array([0]*_vect_size)


def preprocess_training_set(X, Y, discrete_labels=True):
    """
    preprocess the training set, transforming words into real vectors.

    Parameters:
    ------------
        - X: a list of sentences, where each sentence is a list of words.
        - Y: a list of labels corresponding to the sentences.
    """
    # First of all, if descrete_label is equal to true, associate to each label
    # an ID. Otherwise, the labels must be words
    new_Y = list()
    new_X = list()

    if discrete_labels == True:
        global _labelToIDMapping
        global _IDToLabelMapping
        _labelToIDMapping = dict()
        for y in Y:
            if y not in _labelToIDMapping.keys():
                k = len(_labelToMapping.keys())
                _labelToIDMapping[y] = k
                _IDToLabelMapping[k] = y
            new_Y.append(_labelToIDMapping[y])
    else:
        # we assume that each element in Y id a word, and we take its distributed
        # representation.
        for y in Y:
            new_Y.append(_word_lookup(y))
    
    # now we populate new X
    for x in X:
        if isinstance(x, list):
            new_x = list()
            for _x in x:
                new_x.append(_word_lookup(_x))
            new_X.append(new_x)
        else:
            new_X.append(_word_lookup(x))
    
    return new_X, new_Y


def train_LSTM_model(X, Y, lstm_params):
    """
    train a LSTM model (neural network) using the training data in (X, Y).
    TODO: Support sequence prediciton (i.e., a 3D Y array)
    """
    
    # now that preprocessing is done, lets build and train the model
    model = Sequential()
    model.add(LSTM(params['lstm_units'], return_sequences=True, input_shape=(len(X[0]), len(X[0][0])),\
        dropout=params['dropout'], use_bias=params['bias'], recurrent_dropout=params['rec_dropout'],\
        recurrent_activation=params['rec_activation'], activation=params['lstm_activation']))
    
    model.add(Dense(17, activation='softmax'))
    model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])

    if verbose:
        print("Training..")
    model.fit(x_train, y_train, verbose=0, batch_size=params['batch_size'], epochs=params['epochs'])
