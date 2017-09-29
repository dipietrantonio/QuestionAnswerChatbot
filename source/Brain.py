"""
    This module implements an interface to intelligent tasks to be performed by the application.
"""
import DataAccessManager
from SentenceAnalysis import extract_entities, sentence_similarity
from RemoteClassifier import remote_predict
from Settings import QuestionClassifierServer_Port, QuestionClassifierServer_Host,\
    questionPatternsByRelation

def analize_answer(answer, c1):
    """
    Get the entity-answer to a question by analyzing the sentence sent by the user. 

    After having sent a question to a user, the bot has at its disposal the 
    question's subject and the relation used to formulate the question.
    At this point the correct entity to put in relation with the question's subject 
    must be extracted from the user's reply.

    Parameters:
    -----------
        - answer: the user's reply to a question.
        - c1: the question's subject
    
    Returns:
    --------
    Babelnet ID and Text of the concept
    """
    annotations_with_dep = extract_entities(answer)
    if len(annotations_with_dep) == 0:
        print("No entities!")
        return None

    elif len(annotations_with_dep) == 1:
        # there is only one entity, it must be that
        print('Concept chosen from answer:', annotations_with_dep[0][1]['mention'])
        return annotations_with_dep[0][1]['bab_id'], annotations_with_dep[0][1]['mention']

    else:
        candidates = list()
        for dependency, annotation in annotations_with_dep:
            if 'obj' in dependency  and annotation['bab_id'] != c1:
                print('Concept chosen from asnwer:', annotation['mention'])
                return annotation['bab_id'], annotation['mention']


def answer_question(question):
    """
    return the answer to a question.

    This function performs the following steps:
        * first, it predicts the relation involved by looking at the question. It does so
        using a machine learning classifier that is hosted on a server (in another process).
        * then, it extracts entities from the question
        * lastly, it uses the information gathered to search the Knowledge Graph for the best
        answer.
    
    Parameters:
    -----------
        - `question`: string containing the question asked.
    
    Returns:
    --------
    `None` if no answer can be found, a string containing the answer otherwise.
    """
    print("answering a question..")
    top3relations = remote_predict(question, QuestionClassifierServer_Host, QuestionClassifierServer_Port)
    entities = extract_entities(question)
    if len(entities) == 0:
        print("No entities in the question.")
        return None #No entities
    database_entries = DataAccessManager.query_knowledge_graph(entities, top3relations)
    print("Relations predicted out of the question:", top3relations)
    print("Entities extracted:", entities)

    if len(database_entries) == 0:
        print("Entities in the question were not found in the Knowledge Graph")
        return None
    
    # get the most similar question according to "sentence similarity"
    chonsen_entry = None
    max_sim = -1
    for entry in database_entries:
        entry_answer = entry['answer']
        entry_question = entry['question']
        s = sentence_similarity(question, entry_question)
        if s > max_sim:
            max_sim = s
            chonsen_entry = entry

    answer = chonsen_entry['answer']
    print("Dataset entry chosen:", chonsen_entry)

    # There are two types of question. One with only one entity, asking for the
    # related one. Another with 2 entities, asking if they are related according
    # to a given relation.

    if len(entities) == 1:
        return answer
    else:
        # must return yes or no
        if 'no' in answer and len(answer) < 5:
            return "No"
        else:
            return "Yes"

def _single_ent_question(q):
    if 'Y ' in q or ' Y' in q:
        return False
    else:
        return True

def ask_question(domain):
    """
    generate a question to be asked to an user, given a domain.

    Parameters:
    -----------
        - `domain`: string representing the domain of the question to be
        generated.
    
    Returns:
    --------
    A triple (question, entity_id_and_text, relation) where
        - `question` is the question to be asked to the user
        - `entity_id_and_text` is the "entity_name::id" string that will be used to add
        a record in the KBS.
        - `relation` is the relation chosen.
    """
    entity_id, entity_id_and_text, relation = DataAccessManager.pick_subject_to_ask_about(domain)
    print("subject selected", entity_id_and_text, "relation:", relation)
    visual_name = entity_id_and_text.split(':')[0]
    question = set([q for q in questionPatternsByRelation[relation] if _single_ent_question(q)]).pop()
    question = question.replace('X', visual_name)
    return question, entity_id_and_text, relation