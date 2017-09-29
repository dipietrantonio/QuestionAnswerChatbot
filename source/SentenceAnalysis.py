"""
This module implements functions that perform several operations on sentences,
like extracting entities and computing the similarity between two sentences.
"""
import spacy
dep_parser = spacy.load('en')
from nltk import Tree, word_tokenize
from BabelFy import get_annotations, get_id
from Settings import predefinedDomains

def extract_entities(sentence):
    """
    Extract a list of entities from a sentence.

    Parameters:
    -----------
        - `sentence`: the sentence which entities must be extracted from.
    
    Returns:
    --------
    A list of pairs (a, B) where
        - `a` is a spaCy dep tag
        - `B` is a dictionary representing a babelnet annotation
    """
    
    doc = dep_parser(sentence)

    annotations_by_start = dict()
    annotations = [ann for ann in get_annotations(sentence) if ann['bab_id'][-1] != 'v']
    if len(annotations) == 0:
        for tok in doc:
            if tok.pos_ in ['NOUN', 'PROPN', 'NUM']:
                babId = get_id(tok.text)
                if babId is None:
                    continue
                annotation = dict()
                annotation['start'] = tok.i
                annotation['end'] = tok.i + 1
                annotation['bab_id'] = babId
                annotation['type'] = 'MCS'
                annotation['mention'] = tok.text
                annotations.append(annotation)
            
    for annotation in annotations:
        if annotation['bab_id'][-1] in ['v']: #if it is not an entity
            continue
        try:
            annotations_by_start[annotation['start']].append(annotation)
        except KeyError:
            annotations_by_start[annotation['start']] = list()
            annotations_by_start[annotation['start']].append(annotation)

    entities = list()
    last_returned = -1
    for node in doc:
        if last_returned > node.i:
            continue
        try:
            annotations = annotations_by_start[node.i]
            # get the one that covers the most
            chosen = sorted(annotations, key=lambda x: x['end'], reverse=True)[0]
            last_returned = chosen['end']
            if node.pos_ not in ['NOUN', 'PROPN', 'ADJ', 'NUM']:
                continue
            entities.append((node.dep_, chosen))
        except KeyError:
            pass
    return entities

def sentence_similarity(sent1, sent2):
    """
    Measure the similarity between two sentences with a number between 0 and 1.

    Parameters:
    -----------
        - `sent1`: the first sentence
        - `sent2`: the second sentence

    Returns:
    --------
    A value between 0 (totally different) and 1 (the same sentence) 
    """
    sent1_tree = list(dep_parser(sent1).sents)[0].root
    sent2_tree = list(dep_parser(sent2).sents)[0].root

    v = _support_sentence_similarity(sent1_tree, sent2_tree)

    max_v = max(_support_sentence_similarity(sent1_tree, sent1_tree),\
        _support_sentence_similarity(sent2_tree, sent2_tree))
    
    return v / max_v

def _support_sentence_similarity(node1, node2):
    """
    Given two parse trees of two sentences, compute a value that measures the
    similarity between the two.

    Supports the function sentence_similarity

    Parameters:
    -----------
        - `node1`, `node2`: SpaCY token roots
    
    Returns:
    --------
    A number between 0 and 1
    """
    v1 = 1 if node1.lemma_ == node2.lemma_ else 0

    v2 = 1 if node1.dep == node2.dep else 0

    ch_points = 0

    for child1, child2 in zip(node1.children, node2.children):
        if child1.dep == child2.dep:
            ch_points += 1

    value = v1 + v2 + ch_points

    for child1, child2 in zip(node1.children, node2.children):
        value += _support_sentence_similarity(child1, child2)
    
    return value

def tell_domain(text):
    """
    associates to a user specified domain one of the predefined ones.

    Parameters:
    -------------
        - `text`: user specified domain.
    
    Returns:
    --------
    A string containing the mapped domain, or `None` if no matching domain is found.
    """
    # keep a simple implementation, for now. Just check a partial match
    for i, e in enumerate(predefinedDomains):
        if text.lower() in e:
            return e
    
    # returns none if domain's not found
    return None

