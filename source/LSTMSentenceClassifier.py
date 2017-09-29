"""
This module provides a fast interface to LSTM implementation in keras, in particular
to deal with sequences of words.

It also provides a set of functions that are useful when working with sentences, such
as the function that computes the most frequent words.
"""
import keras
import pickle
import numpy
from statistics import stdev
from keras.models import Sequential
from math import floor
from keras.layers import Activation, Dense
from keras.layers.recurrent import LSTM
from ConfusionMatrix import ConfusionMatrix

class LabelMapping:
    """
    Wrapper class used to pass to a LSTM Classifier the mapping between 
    N labels and integers between 0 and N-1
    """
    def __init__(self, labels):
        self._IDToLabelMapping = dict()
        self._labelToIDMapping = dict()
        for i, lab in enumerate(labels):
            self._IDToLabelMapping[i] = lab
            self._labelToIDMapping[lab] = i
            self.length = len(labels)
        return

    def __len__(self):
        return self.length

    def labelToID(self, label):
        return self._labelToIDMapping[label]

    def IDToLabel(self, id):
        return self._IDToLabelMapping[id]
    

class WordTranslation:
    """
    Wrapper class used to pass to a LSTM Classifier the function to be used to 
    translate words into vectors.
    """
    def __init__(self, lookup_function, dictionary):
        self._lookup_function = lookup_function
        self._dictionary = dictionary

def _compute_frequent_words(X, Y, vect_dimension):
    """
    Given a list of sentences, constructs the set of frequent words
    and associates to each of them an integer. In this way we have a
    mapping to translate sentences in bag-of-words.

    Parameters:
    -----------
        - `X`: list of lists of words.
        - `Y`: list of labels.
        - `vect_dimension`: dimension of the vectors that will represent
        a word.
    
    Returns:
    --------
    A dictionary that maps frequent words to integers.
    """
    # first of all, associate to each category the most frequent words in it
    frequencies_per_category = dict()
    avg_per_category = dict()

    for i, v in enumerate(Y):
        current_dict = None 
        try:
            current_dict = frequencies_per_category[v]
        except KeyError:
            frequencies_per_category[v] = dict()
            current_dict = frequencies_per_category[v]
        
        sentence = X[i]
    
        for word in sentence:
            try:
                current_dict[word] += 1
            except KeyError:
                current_dict[word] = 1
        
    words_rarity = dict()
    words_frequency = dict()

    for k in list(frequencies_per_category.keys()):
        total = sum([frequencies_per_category[k][v] for v in frequencies_per_category[k].keys()]) 
        current_dict = frequencies_per_category[k]
        items = [current_dict[v]/total for v in current_dict.keys()]
        # the first step is to remove words that have a frequency below average
        avg = sum(items) / len(items)
        std = stdev(items)
        for v in list(current_dict.keys()):
            current_dict[v] = current_dict[v] / total
            if current_dict[v] < avg + std/2:
                del current_dict[v]
            else:
                try:
                    words_rarity[v] += 1
                except KeyError:
                    words_rarity[v] = 1
                
                try:
                    words_frequency[v] += current_dict[v]
                except KeyError:
                    words_frequency[v] = current_dict[v]
    
    # in this second steps, we first chose the keywords that are unique 
    # for each category, so that to characterize that cateogory
    uniques = [w for w in words_rarity.keys() if words_rarity[w] == 1 ]
    uniques = sorted(uniques, key=lambda x : words_frequency[x], reverse=True)

    commons = [w for w in words_rarity.keys() if words_rarity[w] > 1]
    commons = sorted(commons, key=lambda x : words_frequency[x], reverse=True)

    h = floor(vect_dimension / 2.5)
    all_important_words = uniques[:h] + commons[:vect_dimension - h]
    mapping = dict()
    for i, v in enumerate(all_important_words):
        mapping[v] = i
    
    return mapping
    

def _word_to_one_hot(word, dictionary):
    """
    get the one_hot representation of `word`, according to `dictionary` mapping.

    Parameters:
    -----------
        - `word`: a string representing a word to be translated into a vector.
        - `dictionary`: mapping that associates each word to an integer.
    
    Returns:
    --------
    One hot vector representing `word`.
    """
    try:
        ind = dictionary[word]
        nv = [0] * len(dictionary)
        nv[ind] = 1
        return nv
    except KeyError:
        nv = [0] * len(dictionary)
        return nv

def get_bag_of_words_translator(X, Y, dim=80):
    words = _compute_frequent_words(X, Y, dim)
    return WordTranslation(_word_to_one_hot, words)

class LSTMSentenceClassifier:
    """
    A Machine Learning Classifier that deals with sequences of words.
    """
    def __init__(self, word_translation_method):
        
        self.default_lstm_params = {
            'lstm_units' : 100,
            'dropout' : 0.1,
            'rec_dropout' : 0.1,
            'batch_size' : 40,
            'epochs' : 6,
            'bias' : True,
            'rec_activation' : 'relu',
            'loss' : 'categorical_crossentropy',
            'lstm_activation' : 'sigmoid',
            'optimizer' : 'adagrad'
        }

        self.word_lookup = word_translation_method._lookup_function
        self.dictionary = word_translation_method._dictionary

    def preprocess_input_sentences(self, X, sequence_length = 20):
        """
        Transform each list of words in list of vectors.
        
        It uses padding. If a sequence is too short, 0 vectors will be added. If too long, it will
        be truncated.
        
        Parameters:
        -----------
            - `X`: a list of list of words
            - `sequence_length`: an integer dictating how long a sequence must be.
        
        Returns:
        --------
        The processed list of sentences.
        """
        new_X = list()
        for x in X:
            new_x = list()
            counter = 0
            for _x in x:
                counter += 1
                new_x.append(self.word_lookup(_x, self.dictionary))
                if counter >= sequence_length:
                    break
            if counter < sequence_length:
                while counter < sequence_length:
                    new_x.append([0]*len(new_x[0]))
                    counter += 1
            new_X.append(new_x)
        return new_X

    def set_label_mapping(self, mapping):
        """
        Set the mapping that associate a number to each label.

        Parameters:
        -----------
            - `mapping`: a dictionary that maps each label to an unique number
        
        Returns:
        --------
        Nothing
        """
        self.mapping = mapping

    def preprocess_labels(self, Y):
        """
        Transform each label into a one hot vector.

        Parameters:
        -----------
            - `Y`: list of labels.
        
        Returns:
        --------
        The list of labels as list of one hot vectors.
        """
        # First of all, if descrete_label is equal to true, associate to each label
        # an ID. Otherwise, the labels must be words
        new_Y = list()
        for y in Y:
            nv = [0] * len(self.mapping)
            nv[self.mapping.labelToID(y)] = 1
            new_Y.append(nv)
        return new_Y

    def train_LSTM_model(self, X, Y, params = None):
        """
        Train a LSTM model (neural network) using the training data in (X, Y).
        
        Parameters:
        -----------
            - `X`: a list of lists of vectors (i.e. a 3D vector) of numbers. It is assumed
            that the sequences in input have already been preprocessed using the 
            `preprocess_input_sentences` function.
            - `Y`: a list of vectors, representing the corresponding labels of the sequences in
            `X`. It is assumed that the labels have already been preprocessed using the
            `preprocess_labels` function.
            - `params`: dictionary containing the parameters for the keras model (LSTM classifier).
        
        Returns:
        --------
        Nothing

        TODO:
        -----
        Support sequence prediciton (i.e., a 3D Y array)

        """

        if params is None:
            params = self.default_lstm_params
        
        # now that preprocessing is done, lets build and train the model
        self.model = Sequential()
        self.model.add(LSTM(params['lstm_units'], return_sequences=False, input_shape=(len(X[0]), len(X[0][0])),\
            dropout=params['dropout'], use_bias=params['bias'], recurrent_dropout=params['rec_dropout'],\
            recurrent_activation=params['rec_activation'], activation=params['lstm_activation']))
        
        dense_out = len(self.mapping)
        self.model.add(Dense(dense_out, activation='softmax'))
        self.model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])
        self.model.fit(X, Y, verbose=1, batch_size=params['batch_size'], epochs=params['epochs'])
    
    def save_model(self, path):
        """
        Save the keras model on a file.

        Parameters:
        -----------
            - `path`: the absolute path on the filesystem where to save the model.
        
        Returns:
        --------
        Nothing
        """
        self.model.save(path)
    
    def load_model(self, path):
        """
        Load a model previously saved.

        Parameters:
        -----------

        """
        self.model = keras.models.load_model(path)

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
        """
        Test the trained model against a test set.

        Parameters:
            - `X`: test sequences
            - `Y`: target labels of the test sequences.
        
        Both `X` and `Y` are assumed to be preprocessed.

        Returns:
        --------
        A `ConfusionMatrix` instance.
        """
        y_pred = LSTMSentenceClassifier._prob_dist_to_one_hot(self.model.predict(X))
        cm = ConfusionMatrix(Y, y_pred, self.mapping._IDToLabelMapping)
        return cm

    def _print_distribution(y):
        """
        Print a distribution given as output by the model.
        """
        for v in y:
            print("{:.3f}    ".format(v), end='')
        print("")
        return

    def _prediction_to_top_3_labels(self, Y):
        new_Y = list()
        for y in Y:
            L = sorted(list(enumerate(y)), key=lambda x: x[1], reverse=True)
            top_3_labels = list()
            for i in range(3):
                top_3_labels.append(self.mapping.IDToLabel(L[i][0]))
            new_Y.append(top_3_labels)
        return new_Y


    def predict(self, X):
        """
        Assign a label to each sequence in X.
        
        Parameters:
        -----------
            - `X`: the 3D input, i.e. a list of lists of vectors.
        
        Returns:
        --------
        A list of one predicted labels.
        """
        Y = self.model.predict(numpy.asarray(X))
        return self._prediction_to_top_3_labels(Y)
        # Y = LSTMSentenceClassifier._prob_dist_to_one_hot(Y)
        # new_Y = list()
        # for y in Y:
        #     new_Y.append(self.mapping.IDToLabel(y.index(1)))
        # return new_Y
