#import LSTMSentenceClassifier as lstm
import json
from math import floor
import pickle
from random import randint


def _get_next_dict():
    data = json.load(open('full_kb.txt'))
    for d in data:
        yield d


def how_many_relations():
    rel = set()

    for d in _get_next_dict():
        rel.add(d['relation'])

    print(len(rel))    


def get_training_test_set(dataset, split=0.5):
    """
    divides the dataset in training and test set.
    """
    jdata = json.load(open(dataset))
    print('loaded')
    N = len(jdata)
    Tsize = floor((N/2000)*split)

    selected_items = list()
    remaining_indexes = list(range(0, N, 2000))
    training_items = list()

    while len(selected_items) < Tsize:
        t = len(remaining_indexes) - 1
        j = randint(0, t)
        i = remaining_indexes[j]
        selected_items.append(jdata[i:i+2000])
        del remaining_indexes[j]
    
    
    for d, i in enumerate(remaining_indexes):
        training_items.append(jdata[i:i+2000])
        

    return training_items, selected_items

def write_splitted_datasets():
    training_items, test = get_training_test_set('full_kb.txt')
    pickle.dump(training_items, open("training_data.bin", 'wb'))
    pickle.dump(test, open("test_data.bin", 'wb'))

how_many_relations()