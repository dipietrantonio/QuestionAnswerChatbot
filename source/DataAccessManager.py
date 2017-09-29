"""
    This module acts as interface to both local and remote data available to the application.
"""
import pickle
import re
import os
import traceback
from Settings import domainsToRelationsMapping, KG_DUMP_PATH, KB_DUMP_PATH
from KnowledgeGraph import KnowledgeGraph
import KnowledgeBaseServer as KBS

knowledgeGraph = KnowledgeGraph(domainsToRelationsMapping)

##################################################################################################
#
#                                       Knowledge Graph API
#
##################################################################################################
def dump_knowledge_graph():
    """
    Save the Knowledge Graph structure on a file.
    """
    pickle.dump(knowledgeGraph, open(KG_DUMP_PATH, "wb"))

def initialize_knowledge_graph():
    """
    Initialize the knowledge Graph using the dump, if available, or: if the KBS dump is available, 
    use it; otherwise, use the online KBS.
    """
    if os.path.isfile(KG_DUMP_PATH):
        global knowledgeGraph
        knowledgeGraph = pickle.load(open(KG_DUMP_PATH, 'rb'))
    else:
        if os.path.isfile(KB_DUMP_PATH):
            kb = load_knowledge_base_dump()
            ckb = _clean_downloaded_data(kb)
            knowledgeGraph.update(ckb, len(kb))
        else:
            update_knowledge_graph()
        dump_knowledge_graph()

def update_knowledge_graph():
    """
    Update the Knowledge Graph with new entries (if any) from the online dataset.

    Returns:
    --------
    The number of new entries.
    """
    try:
        data = KBS.get_all_items_from(knowledgeGraph.entry_counter)
        cleaned_data = _clean_downloaded_data(data)
        # TODO: also update the local mirror dump
        print(data)
        knowledgeGraph.update(cleaned_data, len(data))
        if len(data) > 0:
            dump_knowledge_graph()
        return len(data)
    except Exception:
        traceback.print_exc()
        print("Error while updating the knowledge graph.")
        return
    
def query_knowledge_graph(entities, relation):
    """
    query the knowledge graph to find triples that involve `entities` and `relation`.

    Parameters:
    -----------
        - `entities`: a list of tuples (t, A), where t is a SpaCy dep tag, and A is 
        a BabelFy annotation
        - `¶elation`: a string representing a relation between entities.
    
    Returns:
    --------
    A list of dictionaries, where each dictionary is in the KBS entry format.
    """
    return knowledgeGraph.query(entities, relation)

def pick_subject_to_ask_about(domain):
    """
    choose from the local knowledge base an entity and a relation to formulate a question
    and increase knowledge about it.

    Parameter:
    ----------
        - domain: the domain the entity and relation must be extracted from.

    Returns:
    --------
    a triple (entity id, entity name, relation) where
        - entity id is the babelnet id
        - entity name is the textual representation of the entity
        - relation is the chosen relation for the question
    """
    return knowledgeGraph.pick_entity_and_relation(domain)

##################################################################################################
#
#                                      Knowledge Base System Server
#
##################################################################################################
def load_knowledge_base_dump():
    """
    load a json file representing a dump of the online dataset. 
    This is used mostly to load training data.

    Note:
    -----
    At the moment, the KBS dump must be done "manually", i.e., there is
    no function in this module to perform the dump. This is because it is
    used only in the training phase.
    """
    return pickle.load(open(KB_DUMP_PATH, 'rb'))


def add_entry_to_knowledge_base(entry):
    """
    Add an entry to the online knowledge base system.

    Parameters:
    -----------
        - `entry`: dictionary that encode data to be added according to the
        KBS format.
    
    Returns:
    --------
    Nothing
    """
    try:
        KBS.add_item(entry)
    except Exception:
        print("Error while adding a new entry.")
    
    return

##################################################################################################
#
#                                      Helper Functions
#
##################################################################################################

def _clean_downloaded_data(data):
    """
    fix noise in order to be able to save data locally in the graph.
    """
    new_data = list()

    for d in data:
        c1 = d['c1']
        c2 = d['c2']

        if re.match(r"^([A-Za-z0-9 ]+::)bn(:|::)[0-9]+[a-z]$",c1) is None or\
        re.match(r"^([A-Za-z0-9 ]+::)bn(:|::)[0-9]+[a-z]$",c2) is None:
            continue
        new_data.append(d)

    return new_data