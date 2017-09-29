import KnowledgeBaseServer as KBS
import time
import json
import pickle

import re
counter = 0
total = KBS.items_number_from(0)

alls = list()
while counter < total:
    kb = KBS.items_from(counter, total)
    counter += len(kb)
    alls += kb
pickle.dump(alls, open('tmp/KB_dump.bin', 'wb'))