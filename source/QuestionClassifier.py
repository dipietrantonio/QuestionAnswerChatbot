"""
This module implements a machine learning classifier that is able to predict a relation
given a question. It is built on top of a LSTMSentenceClassifier.
"""
import os
from nltk import word_tokenize
import pickle
from ConfusionMatrix import ConfusionMatrix
import LSTMSentenceClassifier as lstm
from LSTMSentenceClassifier import LSTMSentenceClassifier
from Utilities import random_plit
import DataAccessManager
from math import floor
from Settings import TMP_QC_PREFIX

def _extract_question_relation_pairs(jdata):
    """
    Take the 'question' and 'relation' fields for each data entry in the given dataset.
    Also, the question is tokenized as list of words.

    Parameters:
    -----------
        - jdata: list of KBS data entries.
    
    Returns:
    --------
    A pair X, Y where X is a list of tokenized questions and Y is a list of relations.
    """
    X, Y = list(), list()
    for d in jdata:
        question = d['question']
        Y.append(d['relation'])
        tokenized = word_tokenize(question)
        X.append(tokenized)
    return X, Y

def _build_training_validation_test_sets(verbose=1):
    """
    Create training, test and validation sets to build and test the model, using the
    local dump of the Knowledge Base System. Files are written on the temp folder.

    Parameters:
    -----------
        - `verbose`: if 1, the function prints debug information.
    
    Returns:
    --------
    Nothing
    """
    # First, we split the dataset, then process each split.

    # if the datasets don't exist already
    if not(os.path.isfile(TMP_QC_PREFIX + "x_training.bin")):

        # if the unprocessed data splits are present
        if os.path.isfile(TMP_QC_PREFIX + 'unprocessed_test.bin'):
            
            unprocessed_training = pickle.load(open(TMP_QC_PREFIX + 'unprocessed_training.bin', 'rb'))
            unprocessed_test = pickle.load(open(TMP_QC_PREFIX + 'unprocessed_test.bin', 'rb'))
            unprocessed_dev = pickle.load(open(TMP_QC_PREFIX + 'unprocessed_dev.bin', 'rb'))
            
        else: # we need to create the split
            # load the full dataset
            jdata = DataAccessManager.load_knowledge_base_dump()
            jdata, other = random_plit(jdata, 0.33)
            unprocessed_training, other = random_plit(jdata, 0.5)
            unprocessed_test, unprocessed_dev = random_plit(other, 0.25)
            pickle.dump(unprocessed_training, open(TMP_QC_PREFIX + 'unprocessed_training.bin', 'wb'))
            pickle.dump(unprocessed_test, open(TMP_QC_PREFIX + 'unprocessed_test.bin', 'wb'))
            pickle.dump(unprocessed_dev, open(TMP_QC_PREFIX + 'unprocessed_dev.bin', 'wb'))
            del jdata

        if verbose:
            print("Start extracting question-relation pairs")
            print("get training questions")

        x_training, y_training = _extract_question_relation_pairs(unprocessed_training)
        del unprocessed_training
        pickle.dump(x_training, open(TMP_QC_PREFIX + "x_training.bin", 'wb'))
        pickle.dump(y_training, open(TMP_QC_PREFIX + "y_training.bin", 'wb'))
        translationData = lstm.get_bag_of_words_translator(x_training, y_training, 80)
        pickle.dump(translationData, open(TMP_QC_PREFIX + "bow.bin", 'wb'))
        del x_training
        del y_training

        if verbose:
            print("generating test question-relation pairs")
        x_test, y_test = _extract_question_relation_pairs(unprocessed_test)
        del unprocessed_test
        pickle.dump(x_test, open(TMP_QC_PREFIX + "x_test.bin", 'wb'))
        pickle.dump(y_test, open(TMP_QC_PREFIX + "y_test.bin", 'wb'))
        del x_test
        del y_test

        if verbose:
            print("generating dev question-relation pairs")
        x_dev, y_dev = _extract_question_relation_pairs(unprocessed_dev)
        del unprocessed_dev
        pickle.dump(x_dev, open(TMP_QC_PREFIX + "x_dev.bin", 'wb'))
        pickle.dump(y_dev, open(TMP_QC_PREFIX + "y_dev.bin", 'wb'))
        del x_dev
        del y_dev

class QuestionClassifier:
    """
    Based on LSTM, this classifier can predict a relation a given question refers to.
    """
    def __init__(self, model = None):
        # load the translation method, i.e. the function that maps words to vectors.
        # If it is not present, then we need to compute it (together with the datasets)
        if not os.path.isfile(TMP_QC_PREFIX + "bow.bin"):
            _build_training_validation_test_sets()
        
        translation_method = pickle.load(open(TMP_QC_PREFIX + "bow.bin", 'rb'))
        self._lstm_classifier = LSTMSentenceClassifier(translation_method)
        self.params = self._lstm_classifier.default_lstm_params
        # load a model if present
        if not(model is None):
            mapping = pickle.load(open(TMP_QC_PREFIX + "labelMapping.bin", 'rb'))
            self._lstm_classifier.set_label_mapping(mapping)
            self._lstm_classifier.load_model(model)
    
    def train_model(self):
        """
        Train the Question Classifier using the datasets in the temp directory.
        """
        if not os.path.isfile(TMP_QC_PREFIX + "x_training.bin"):
            _build_training_validation_test_sets()
        
        x_train = pickle.load(open(TMP_QC_PREFIX + "x_training.bin", 'rb'))
        y_train = pickle.load(open(TMP_QC_PREFIX + "y_training.bin", 'rb'))
        
        if not os.path.isfile(TMP_QC_PREFIX + "labelMapping.bin"):
            labels = set(y_train)
            mapping = lstm.LabelMapping(labels)
            pickle.dump(mapping, open(TMP_QC_PREFIX + "labelMapping.bin", 'wb'))
        
        mapping = pickle.load(open(TMP_QC_PREFIX + "labelMapping.bin", 'rb'))
        self._lstm_classifier.set_label_mapping(mapping)
        x_train = self._lstm_classifier.preprocess_input_sentences(x_train)
        y_train = self._lstm_classifier.preprocess_labels(y_train)
        print("training started..")
        self._lstm_classifier.train_LSTM_model(x_train, y_train, self.params)
        self._lstm_classifier.save_model(TMP_QC_PREFIX + "lstm_model")

    def predict(self, sentence):
        """
        Predicts a relation given a sentence.

        Parameters:
        -----------
            - `sentence`: the sentence in input to the classifier.
        
        Returns:
        --------
        A string containing the relation.
        """
        tok = word_tokenize(sentence)
        X = [tok]
        X = self._lstm_classifier.preprocess_input_sentences(X)
        Y = self._lstm_classifier.predict(X)
        return Y[0]

    def test(self, x_test, y_test):
        """
        Predicts a relation given a sentence.

        Parameters:
        -----------
            - `sentence`: the sentence in input to the classifier.
        
        Returns:
        --------
        A string containing the relation.
        """
        X = self._lstm_classifier.preprocess_input_sentences(x_test)
        Y = self._lstm_classifier.predict(X)
        cm = ConfusionMatrix(y_test, Y)
        return cm

def get_question_classifier():
    """
    Get an instance of a Question Classifier.

    If there is a trained model already, return that. Otherwise, train a new model.

    Returns:
    --------
    An instance of QuestionClassifier. 
    """
    if os.path.isfile(TMP_QC_PREFIX + "lstm_model"):
        q = QuestionClassifier(TMP_QC_PREFIX + "lstm_model")
        return q
    else:
        q = QuestionClassifier()
        q.train_model()
        return q
