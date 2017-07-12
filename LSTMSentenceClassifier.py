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
from MachineLearning.model_evaluation import ConfusionMatrix

_word_vect = pickle.load(open('models/glove.bin', 'rb'))
_vect_size = len(list(_word_vect.values())[0])

def _word_lookup(word):
    """
    returns the distributional representation of a word, if exists. Returns the
    0 vector otherwise.
    """
    try:
        return _word_vect[word]
    except KeyError:
        try:
            return _word_vect[word.lower()]
        except KeyError:
            print(word, "not found")
            return [0]*_vect_size


class LSTMSentenceClassifier:

    def __init__(self):
        self._labelToIDMapping = dict()
        self._IDToLabelMapping = dict()


        self.default_lstm_params = {
            'lstm_units' : 120,
            'dropout' : 0.1,
            'rec_dropout' : 0.1,
            'batch_size' : 40,
            'epochs' : 6,
            'bias' : True,
            'rec_activation' : 'relu',
            'loss' : 'categorical_crossentropy',
            'lstm_activation' : 'linear',
            'optimizer' : 'adagrad'
        }

    def preprocess_input_sentences(self, X, sequence_length = 20):
        """
        transform each list of words in list of vectors. Finally, pad sequences.
        If a sequence is too short, 0 vectors will be added. If too long, it will
        be truncated.
        """
        new_X = list()
        for x in X:
            new_x = list()
            counter = 0
            for _x in x:
                counter += 1
                new_x.append(_word_lookup(_x))
                if counter >= sequence_length:
                    break
            if counter < sequence_length:
                while counter < sequence_length:
                    new_x.append([0]*len(new_x[0]))
                    counter += 1
            new_X.append(new_x)
        return new_X

    def set_labels(self, labels):
        """
        assign to each label an id.
        """
        for i, lab in enumerate(labels):
            self._IDToLabelMapping[i] = lab
            self._labelToIDMapping[lab] = i
        return

    def preprocess_labels(self, Y):
        """
        transform each label into a one hot vector
        """
        # First of all, if descrete_label is equal to true, associate to each label
        # an ID. Otherwise, the labels must be words
        new_Y = list()
        for y in Y:
            nv = [0] * len(self._labelToIDMapping.keys())
            nv[self._labelToIDMapping[y]] = 1
            new_Y.append(nv)
        return new_Y

    def train_LSTM_model(self, X, Y, params = None):
        """
        train a LSTM model (neural network) using the training data in (X, Y).
        TODO: Support sequence prediciton (i.e., a 3D Y array)
        """

        if params is None:
            params = self.default_lstm_params
        
        # now that preprocessing is done, lets build and train the model
        self.model = Sequential()
        self.model.add(LSTM(params['lstm_units'], return_sequences=False, input_shape=(len(X[0]), len(X[0][0])),\
            dropout=params['dropout'], use_bias=params['bias'], recurrent_dropout=params['rec_dropout'],\
            recurrent_activation=params['rec_activation'], activation=params['lstm_activation']))
        
        dense_out = len(self._IDToLabelMapping.keys())
        self.model.add(Dense(dense_out, activation='softmax'))
        self.model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])
        
        self.model.fit(X, Y, verbose=1, batch_size=params['batch_size'], epochs=params['epochs'])
    
    def _prob_dist_to_one_hot(Y):
        new_Y = list()
        for y in Y:
            max_ind = -1
            max_val = -1
            for i, v in enumerate(y):
                if v > max_val:
                    max_val = v
                    max_ind = i
            nv = [0]*len(Y[0])
            nv[max_ind] = 1
            new_Y.append(nv)
        return new_Y

    def test_model(self, X, Y):

        y_pred = LSTMSentenceClassifier._prob_dist_to_one_hot(self.model.predict(X))
        cm = ConfusionMatrix(Y, y_pred, self._IDToLabelMapping)
        return cm