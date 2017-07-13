
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

        # lets start with the initial transitions
        s_count = 0
        s_total = 0
        keys = list(self.start_state_prob.keys())
        
        for node in keys:
            if self.start_state_prob[node] < threshold:
                s_total += self.start_state_prob[node]
                s_count += 1
                del self.start_state_prob[node]
        
        # _*_ is a special value to address "any initial value"
        self.start_state_prob["_*_"] = (s_total // s_count) if s_count > 0 else 0
        self.node_frequencies["_*_"] = self.start_state_prob["_*_"]
        # now lets proceed to replace with "*" all the unimportant words in the pattern
        for node in self.start_state_prob.keys():
            self._bfs_simplify(node, threshold)
        
        self._merge_stars(None)

    
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

        self.adj[star_name] = merged_neighbors
        #print("new node", star_name, merged_neighbors)
        self.node_frequencies[star_name] = self.node_max_freq #TODO CHECK THIS
        visited.add(star_name)

        # fix every node that points to a node in the path
        # redirect edges to a new node
        for node in list(self.adj.keys()):
            if node in lpath:
                continue
            l = list(self.adj[node].keys())
            total = 0
            for nn in lpath:
                if nn in l:
                    total += self.adj[node][nn]
                    del self.adj[node][nn]
            if total > 0:
                self.adj[node][star_name] = total
        
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
            if len(path) > 0 and f >= nf_threshold:
                # case when a relevant node is encountered a first time
                #print("relevant new node encountered:", c, "path:", MarkovChain._print_path(path))
                # create a new star node that has outgoing edges collected
                # from the nodes in path
                self._compress_path(path, visited)            
                
                #print("after relevant compression: ")
            
            elif f < nf_threshold:
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
    
    def _merge_stars(self, start_node):
        stars = 0
        for c in self.adj.keys():
            
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
                queue.insert(0, merged_star)
                visited.add(merged_star)
                stars += 1
                
    def add_sample(self, sentence):
        if len(sentence) == 0:
            return
        self.add_initial_state_occurrence(sentence[0])
        for i in range(1, len(sentence)):
            self.add_occurrence(sentence[i-1], sentence[i])
            self.increment_node_frequency(sentence[i])

ch = MarkovChain()

ch.add_sample("Where th matteo is".split())
ch.add_sample("Where c cristian is".split())

print(ch.node_max_freq)

ch.simplify()
print("----")
print(ch)