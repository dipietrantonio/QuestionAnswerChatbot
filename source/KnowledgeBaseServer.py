"""
This module implements the interface to the Knowledge Base System. The KBS is located on a server
and it is accessible using REST API.
"""
import urllib3
from bs4 import BeautifulSoup
import json
import time
from Settings import KBS_host, KBS_path, KBS_port, BabelNetKEY

main_url = "http://" + KBS_host + ":" + KBS_port

# create an instance of request pool
_connection_pool = urllib3.connection_from_url(main_url)

def do_get(endpoint, params):
    """
    performs a GET request to the server.
    """
    return _connection_pool.request('GET', KBS_path + endpoint, params).data.decode('utf8', 'ignore')

def do_post(endpoint, post_data):
    """
    performs a POST request to the server.
    """
    return _connection_pool.request('POST', KBS_path + endpoint + "?key=" + BabelNetKEY, \
    body=post_data, headers={'Content-Type':'application/json'}).data.decode('utf8', 'ignore')

def items_number_from(id):
    """
    Returns the number of items that has an id greater or equal to the given id. The
    number of such items is returned as long.
    """
    params = {'id' : id, 'key' : BabelNetKEY}
    resp = do_get('items_number_from', params)
    return int(resp)

def items_from(start_id, nItems=1000):
    """
    returns the nItems items with id greater or equal to the given id.
    """
    counter = 0
    c_id = start_id
    final_resp = "["
    try:
        while counter < nItems:
            params = {'id' : c_id, 'key' : BabelNetKEY}
            resp = do_get('items_from', params)
            if len(resp) == 0:
                break
            ld = len(json.loads(resp))
            final_resp += resp[1:-1] + ","
            counter += ld
            c_id = c_id + ld
            print("{}/{}          ".format(counter, nItems), end='\r')
            time.sleep(0.5)
    except Exception:
        time.sleep(5)
    final_resp = (final_resp[:-1] if final_resp[-1] == ',' else final_resp) + "]"
    return json.loads(final_resp)

def get_all_items_from(start_id):
    """
    get all the items starting with the one with id start_id
    """
    total_new_entries = items_number_from(start_id)
    return items_from(start_id, total_new_entries)

def add_item(dataEntry):
    """
    adds an entry to the database. Returns 1 id the operation is successful, -1 otherwise.
    """
    sdata = json.dumps(dataEntry)
    return do_post('add_item', sdata)

def add_items(dataEntries):
    """
    adds multiple entries to the database. Returns 1 id the operation is successful, -1 otherwise.
    """
    sdata = json.dumps(dataEntries)
    return do_post('add_items', sdata)