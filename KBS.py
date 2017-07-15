"""
This module implements the interface to the Knowledge Base System. The KBS is located on a server
and it is accessible using REST API.
"""
import urllib3
from bs4 import BeautifulSoup
import json
import time 
# parse settings and information needed to access the server
xmlfile = open('kbs.xml').read()
soup = BeautifulSoup(xmlfile, 'lxml')

host = soup.find('host').text
port = soup.find('port').text
path = soup.find('path').text
key = soup.find('key').text

main_url = "http://" + host + ":" + port

# create an instance of request pool
_connection_pool = urllib3.connection_from_url(main_url)

def do_get(endpoint, params):
    """
    performs a GET request to the server.
    """
    #return _connection_pool.request('GET', endpoint, params).data.decode('utf8', 'ignore')
    return _connection_pool.request('GET', path + endpoint, params).data.decode('utf8', 'ignore')

def do_post(endpoint, post_data):
    """
    performs a POST request to the server.
    """
    return _connection_pool.request('POST', path + endpoint + "?key=" + key, body=post_data, headers={'Content-Type':'application/json'}).data.decode('utf8', 'ignore')

def items_number_from(id):
    """
    Returns the number of items that has an id greater or equal to the given id. The
    number of such items is returned as long.
    """
    params = {'id' : id, 'key' : key}
    resp = do_get('items_number_from', params)
    return int(resp)

def items_from(start_id, nItems=1000):
    """
    returns the nItems items with id greater or equal to the given id.
    """
    counter = 0
    c_id = start_id
    final_resp = "["
    while counter < nItems:
        params = {'id' : c_id, 'key' : key}
        resp = do_get('items_from', params)
        ld = len(json.loads(resp))
        if ld == 0:
            print("No more data")
            exit(1)
        final_resp += resp[1:-1] + ","
        counter += ld
        c_id = c_id + ld
        print("{}/{}          ".format(counter, nItems), end='\r')
        time.sleep(0.2)
    
    return final_resp[:-1] + "]"
    #return json.loads(final_resp)

def add_item(dataEntry):
    """
    adds an entry to the database. Returns 1 id the operation is successful, -1 otherwise.
    """
    sdata = json.dumps(dataEntry)
    return do_post('add_item_test', sdata)

def add_items(dataEntries):
    """
    adds multiple entries to the database. Returns 1 id the operation is successful, -1 otherwise.
    """
    sdata = json.dumps(dataEntries)
    return do_post('add_items_test', sdata)

def encode_entry(question, answer, relation, context, domains, c1, c2):
    return {'question' : question, 'answer' : answer, 'relation' : relation, 'context' : context, 'domains' : domains, 'c1' : c1, 'c2':c2}