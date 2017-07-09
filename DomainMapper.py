"""
This module is used to map a user specified domain to one of the predefined domains.
"""
predef_domains = [line.strip().lower() for line in open('domain_list.txt').readlines()]

def tell_domain(text):
    """
    associates to a user specified domain one of the predefined ones.

    Parameters:
    -------------
        -   text: user specified domain.
    """
    # keep a simple implementation, for now. Just check a partial match
    for i, e in enumerate(predef_domains):
        if text.lower() in e:
            return i
    
    # returns none if domain's not found
    return None