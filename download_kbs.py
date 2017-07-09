import KBS
import time
import json
import pickle
# total = KBS.items_number_from(0)
# kb = KBS.items_from(0, total)

# f = open("full_kb.txt", 'w')

# f.write(kb)
# f.close()

lo = json.loads(open('full_kb.txt').read())

pickle.dump(lo, open('full_kb.dump', 'wb'))