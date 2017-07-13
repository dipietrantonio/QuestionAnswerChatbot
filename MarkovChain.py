
class MarkovChain:

    def __init__(self):
        self.adj = dict()
        self.start_state_prob = dict()
        self.node_frequencies = dict()
        self.node_max_freq = 0

    def get_neighbors(self, node):
        if node not in self.adj.keys():
            return []

        return list(self.adj[node].keys())
    
    def add_initial_state_occurrence(self, node):
        self.increment_node_frequency(node)
        if node not in self.start_state_prob.keys():
            self.start_state_prob[node] = 1
        else:
            self.start_state_prob[node] += 1

    def increment_node_frequency(self, node1):
        if node1 not in self.node_frequencies.keys():
                self.node_frequencies[node1] = 1            
        else:
            self.node_frequencies[node1] += 1
        if self.node_max_freq < self.node_frequencies[node1]:
            self.node_max_freq = self.node_frequencies[node1]

    def add_occurrence(self, node1, node2, value = 1):
        if node1 not in self.adj.keys():
            self.adj[node1] = dict()

        neighbors = self.adj[node1]
        if node2 not in neighbors.keys():
            neighbors[node2] = value
        else:
            neighbors[node2] += value

    def __str__(self):
        rstring = ""
        for node in self.adj.keys():
            rstring += "{} -> ".format(node)
            for neigh in self.adj[node].keys():
                rstring += "({}, {}) ".format(neigh, self.adj[node][neigh])
            rstring += "\n"
        return rstring

    def normalize(self):
        new_chain = MarkovChain()
        total = 0
        for node in self.start_state_prob.keys():
            total += self.start_state_prob[node]
        
        for node in self.start_state_prob.keys():
            p = self.start_state_prob[node] / total
            new_chain.start_state_prob[node] = p

        for node in self.adj.keys():
            total = 0
            for neigh in self.adj[node].keys():
                total += self.adj[node][neigh]
                new_chain.adj[node] = dict()
            
            for neigh in self.adj[node].keys():
                p = self.adj[node][neigh] / total
                new_chain.adj[node][neigh] = p
        
        return new_chain

    def simplify(self, threshold = 'auto'):
        
        if threshold == 'auto':
            threshold = self.node_max_freq // 2
        else:
            threshold = self.node_max_freq * threshold

        for node in list(self.start_state_prob.keys()):
            self._bfs_simplify(node, threshold)
        self._merge_stars()

    
    def _iterate_path(path):
        while len(path) > 0:
            if path[1].startswith('_*_') and len(path[0]) > 0:
                continue 
            yield path[1]
            path = path[0]
    
    def _clear_path(path, star):
        while(len(path) > 0):
            t = path[0]
            path[1] = star
            path = t
    
    def _print_path(path):
        r = ""
        while(len(path) > 0):
            t = path[0]
            r = path[1] + r
            path = t
        return r

    def _compress_path(self, path, visited):
        if len(path) == 0:
            return
        #print("entering path compression with path", MarkovChain._print_path(path))
        star_name = "_*_"
        lpath = list(MarkovChain._iterate_path(path))
        merged_neighbors = dict()
        for nn in lpath:
            try:
                for ke in self.adj[nn].keys():
                    if ke in lpath:
                        continue
                    if ke not in merged_neighbors.keys():
                        merged_neighbors[ke] = self.adj[nn][ke]
                    else:
                        merged_neighbors[ke] += self.adj[nn][ke]
            except KeyError:
                pass
            star_name += nn
        if len(merged_neighbors) > 0:
            self.adj[star_name] = merged_neighbors
        #print("new node", star_name, merged_neighbors)
        self.node_frequencies[star_name] = self.node_max_freq #TODO CHECK THIS
        visited.add(star_name)

        # fix every node that points to a node in the path
        # redirect edges to a new node
        initial = path[-1] in self.start_state_prob.keys()
        for node in list(self.adj.keys()):
            if node in lpath:
                continue
            l = list(self.adj[node].keys())
            total = 0
            for nn in lpath:
                if nn in l:
                    initial = False
                    total += self.adj[node][nn]
                    del self.adj[node][nn]
            if total > 0:
                self.adj[node][star_name] = total
        if initial:
            del self.start_state_prob[path[-1]]
            self.start_state_prob[star_name] = 1
        # delete every node in path from adj dictionary, so that
        # they exist no more
        for nn in MarkovChain._iterate_path(path):
            if nn in self.adj.keys():
                del self.adj[nn]
        MarkovChain._clear_path(path, star_name)

    def _bfs_simplify(self, start_node, nf_threshold):
        queue = list()
        fathers = dict()
        visited = set()
        visited.add(start_node)
        queue.insert(0, (start_node, list()))

        while len(queue) > 0:
            c, path = queue.pop()
            #print("dequeued", c)
            f = self.node_frequencies[c]
            newPath = list()
            if len(path) > 0 and f > nf_threshold:
                # case when a relevant node is encountered a first time
                #print("relevant new node encountered:", c, "path:", MarkovChain._print_path(path))
                # create a new star node that has outgoing edges collected
                # from the nodes in path
                self._compress_path(path, visited)            
                
                #print("after relevant compression: ")
            
            elif f <= nf_threshold:
                # case when an irrelevant node is encountered a first time
                newPath = [path, c]
                #print("irrelevant node encountered first time", c)
            
            # check if there are neighbors
            neighbors = self.get_neighbors(c)
            
            if len(neighbors) == 0:
                # simplify here
                #print("no neighbor compress", c)
                self._compress_path(newPath, visited)           
            else:
                for neigh in neighbors:
                    #print("checking neighbor", neigh, visited) 
                    if neigh not in visited:
                        queue.insert(0, (neigh, newPath))
                        visited.add(neigh)
                    else:
                        # if it is a less frequent node
                        #  then neigh should be in path, since all the other
                        # visited "less frequent" nodes are all converted in
                        # star nodes
                        # else
                        # it is a frequent node. Since it is a frequent node,
                        # it cant be in path[1:] by definition. It could be the
                        # initial node in path though.
                        self._compress_path(newPath, visited)
    
    def _merge_stars(self):
        
        #first, merge initial stars

        self.adj["_*_"] = dict()
        total_sprob = 0
        listOfNodes = list(self.adj.keys())

        initial_nodes = list(self.start_state_prob.keys())
        star_initial_nodes = list()
        for node in initial_nodes:
            if node.startswith("_*_"):
                star_initial_nodes.append(node)
                try:
                    for k in list(self.adj[node].keys()):
                        if k in self.adj["_*_"].keys():
                            self.adj["_*_"][k] += self.adj[node][k]
                        else:
                            self.adj["_*_"][k] = self.adj[node][k]
                        del self.adj[node]
                    total_sprob += self.start_state_prob[node]
                    
                except KeyError:
                    pass
                del self.start_state_prob[node]
                
        # redirect incoming edge in node to stars
        for onode in listOfNodes:
            for node in star_initial_nodes:
                try:
                    if node in self.adj[onode].keys():
                        if '_*_' in list(self.adj[onode].keys()):
                            self.adj[onode]['_*_'] += self.adj[onode][node]
                        else:
                            self.adj[onode]['_*_'] += self.adj[onode][node]
                        del self.adj[onode][node]
                except KeyError:
                    pass
            
        stars = 0
            
        for c in listOfNodes:
            
            neighbors = self.get_neighbors(c)
            
            merged_star = None
            merged_neigh = dict()
            for neigh in neighbors:
                
                if neigh.startswith("_*_"):
                    merged_star = "_*_" + str(stars)
                    # get outgoing edges
                    try:
                        for k in self.adj[neigh].keys():
                            if k not in merged_neigh.keys():
                                merged_neigh[k] = self.adj[neigh][k]
                            else:
                                merged_neigh[k] += self.adj[neigh][k]
                        del self.adj[neigh]
                    except KeyError:
                        pass
                
                    # now transfer ingoing edges
                    for node in self.adj.keys():
                        node_neighbors = list(self.adj[node].keys())
                        if neigh in node_neighbors:
                            if merged_star in node_neighbors:
                                self.adj[node][merged_star] += self.adj[node][neigh]
                            else:
                                self.adj[node][merged_star] = self.adj[node][neigh]
                            del self.adj[node][neigh]
                
            if merged_star is not None:
                self.adj[merged_star] = merged_neigh
                stars += 1
                
    def add_sample(self, sentence):
        if len(sentence) == 0:
            return
        self.add_initial_state_occurrence(sentence[0])
        for i in range(1, len(sentence)):
            self.add_occurrence(sentence[i-1], sentence[i])
            self.increment_node_frequency(sentence[i])

    def train_model(self, X):
        for x in X:
            self.add_sample(x)
        self.simplify()
        self.normalize()
    
    def sample_probability(self, sample):
        p = 0
        try:
            p = self.start_state_prob[sample[0]]
        except KeyError:
            p = self.start_state_prob["_*_"]
        
        if p == 0:
            return 0
        
        for i in range(1, len(sample)):
            pass

m = MarkovChain()

s = [ "x where is y".split(), "z where is f".split()]

m.train_model(s)
m = m.normalize()
print(m)