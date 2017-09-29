"""
    This module is used to load all the settings in global variables
"""
from bs4 import BeautifulSoup

# Question Classifier Server settings
_settings = open('local_data/qc_server.xml').read()
_soup = BeautifulSoup(_settings, 'lxml')

QuestionClassifierServer_Port = int(_soup.find('port').text)
QuestionClassifierServer_Host = _soup.find('host').text
# TEMP folder location
TMP_QC_PREFIX = "tmp/qc_"

# Telegram Bot
_settings = open('local_data/bot.xml').read()
_soup = BeautifulSoup(_settings, 'lxml')
TelegramBotToken = _soup.find('token').text

# Predefined domains
predefinedDomains = [line.strip().lower() for line in open('local_data/domain_list.txt').readlines()]

# Knowledge Base Server settings
_settings = open('local_data/kbs.xml').read()
_soup = BeautifulSoup(_settings, 'lxml')

KBS_host = _soup.find('host').text
KBS_port = _soup.find('port').text
KBS_path = _soup.find('path').text
BabelNetKEY = _soup.find('key').text

# Local data settings and info
KB_DUMP_PATH = "local_data/KB_dump.bin" #knowledge base dump
KG_DUMP_PATH = "tmp/KG_dump.bin" #knowledge graph dump

# Domains to relation mapping
_DOM_TO_REL = "local_data/domains_to_relations.tsv"

def _load_domains_to_relations_mapping():
    """
    used to read the domains_ro_relations mapping file
    """
    content = open(_DOM_TO_REL)
    mapping = dict()
    for entry in [line[:-1].split('\t') for line in content]:
        mapping[entry[0].lower()] = set([el.lower() for el in entry[1:]])
    return mapping

domainsToRelationsMapping = _load_domains_to_relations_mapping()

# Answer Generation env variables
AG_TRAINING_FILE = "local_data/train_v1.1.json"
AG_TEST_FILE = "local_data/test_public_v1.1.json"

# Load question pattens

def _loadQuestionPatterns():
    mapp = dict()
    for line in open("local_data/question_patterns.tsv").readlines():
        q, c = line.strip().split('\t')
        if ' Y ' in q or 'Y?' in q:
            continue
        c = c.lower()
        if c not in mapp.keys():
            mapp[c] = list()
        mapp[c].append(q)
    return mapp

questionPatternsByRelation = _loadQuestionPatterns()