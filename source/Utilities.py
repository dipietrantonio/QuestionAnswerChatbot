from math import floor
from random import randint
"""
This module contains functions that support other functions but are not elegible to stay in the
same module for semantic reasons.
"""
def random_plit(X, split=0.3, bsize=2000):
    """
    Divide randomly a dataset in two parts, with sizes depending on `split`, 
    considering elements in blocks of size `bsize`. 

    Parameters:
    -----------
        - X: the dataset to be divided
        - split: a number between 0 and 1 that tells how many elements must go in the
        second sets.
        - bsize: size of the block of elements considered each time. Elements are not
        considered each one by itself, but in blocks, for efficiency reasons.
    
    Returns:
    --------
    Two lists of elements.
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

def correct_grammatical_errors(question):
    """
    Correct grammatical errors in an input sentence.

    This is done because grammatical errors can have huge impact on
    relation prediction, because of how frequent words are computed.
    As an example "Where" is different from "where", because the first
    is found only at the beginning of a sentence.
    """ 

    # The first word has uppercase letter
    question = question[0].upper() + question[1:]

    # TODO: other checks, but maybe are too costly
    return question