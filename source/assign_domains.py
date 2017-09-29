import pickle

mapping = dict()
for line in open('local_data/babeldomains_babelnet.txt'):
    key, val , _ = line.split('\t')[:3]
    mapping[key] = val


KB = pickle.load(open('local_data/KB_dump.bin', 'rb'))

total = len(KB)
count = 0
for d in KB:
    l1 = d['c1'].rfind('bn:')
    l2 = d['c2'].rfind('bn:')
    c1 = d['c1'][l1:]
    c2 = d['c2'][l2:]

    domains = list()

    try:
        domains.append(mapping[c1])
    except Exception:
        pass
    
    try:
        domains.append(mapping[c2])
    except Exception:
        pass
    
    if len(domains) == 0:
        count += 1
    
    d['domains'] = domains

pickle.dump(KB, open('local_data/KB_dump2.bin', 'wb'))

print(count/total)
