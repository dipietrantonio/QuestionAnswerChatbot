"""
    This module implements communication functions with BabelFy application.
"""
import urllib3
import json
from bs4 import BeautifulSoup
from Settings import BabelNetKEY as key

lang = "EN"
# pool handles http connections
pool = urllib3.PoolManager()

def get_annotations(text):
    """
    get BabelFy annotations from a text.

    Parameters:
    -----------
        - text: the text to be analyzed by BabelFy
    
    Returns:
    --------
    A list of dictionaries, where each dictionary is an annotation.
    """
    js = pool.request('GET',"https://babelfy.io/v1/disambiguate", {'text':text, 'lang':lang, 'key':key}).data.decode(errors='ignore')
    return parse_json(js, text)

def get_id(text):
    """
    get the BabelNet ID of a concept.

    Parameters:
    -----------
        - text: textual representation of the concept
    
    Returns:
    --------
    A Babelnet ID.
    """
    js = pool.request('GET',"https://babelnet.io/v4/getSynsetIds", {'word':text, 'langs':lang, 'key':key}).data.decode(errors='ignore')
    print(js)
    try:
        return json.loads(js)[0]['id']
    except Exception:
        return None

def parse_json(jsondata, text):
    """
    Parse BabelFy JSON data and transform it to a more convenient format.

    Parameters:
    -----------
        - jsondata: data downloaded from BabelFy.
        - text: the text that BabelFy was queried about.
    
    Returns:
    --------
    List of dictionaries, where each dictionary is an annotation.
    """
    try:
        data = json.loads(jsondata)
        annotations = list()
        for token in data:
            annotation = dict()
            annotation['start'] = int(token['tokenFragment']['start'])
            annotation['end'] = int(token['tokenFragment']['end']) + 1
            annotation['bab_id'] = token['babelSynsetID']
            annotation['type'] = token['source']
            cs = int(token['charFragment']['start'])
            ce = int(token['charFragment']['end'])
            annotation['mention'] = text[cs:ce+1]
            annotations.append(annotation)
        return annotations
    except Exception:
        return []