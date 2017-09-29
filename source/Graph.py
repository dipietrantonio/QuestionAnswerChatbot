"""
This module implements a Graph structure.
"""
class Graph:

    def __init__(self):
        self.outgoing = dict()
        self.incoming = dict()

    def get_neighbors(self, node):
        if node not in self.outgoing.keys():
            return []
        return list(self.outgoing[node].keys())
    
    def add_edge(self, node1, node2, value):
        
        neighbors = None
        incomings = None
        try:
            neighbors = self.outgoing[node1]
        except KeyError:
            self.outgoing[node1] = dict()
            neighbors = self.outgoing[node1]
        
        try:
            incomings = self.incoming[node2]
        except KeyError:
            self.incoming[node2] = dict()
            incomings = self.incoming[node2]
        
        try:
            neighbors[node2].append(value)
        except KeyError:
            neighbors[node2] = list()
            neighbors[node2].append(value)
        
        try:
            incomings[node1].append(value)
        except KeyError:
            incomings[node1] = list()
            incomings[node1].append(value)
        
    def __str__(self):
        rstring = ""
        for node in self.outgoing.keys():
            rstring += "{} -> ".format(node)
            for neigh in self.outgoing[node].keys():
                rstring += "({}, {}) ".format(neigh, self.outgoing[node][neigh])
            rstring += "\n"
        return rstring