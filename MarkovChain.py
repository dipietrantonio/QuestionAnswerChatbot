from math import exp

class MarkovChain:

    def __init__(self):
        self.outgoing = dict()
        self.incoming = dict()
        self.start_state_prob = dict()
        self.node_frequencies = dict()
        self._star_path_len = dict()
        self.node_max_freq = 0
        self._defined_as_star = set()

    def get_neighbors(self, node):
        if node not in self.outgoing.keys():
            return []
        return list(self.outgoing[node].keys())
    
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

    def add_edge(self, node1, node2, value = 1):
        if node1 not in self.outgoing.keys():
            self.outgoing[node1] = dict()
        
        if node2 not in self.incoming.keys():
            self.incoming[node2] = dict()

        neighbors = self.outgoing[node1]
        incomings = self.incoming[node2]

        if node2 not in neighbors.keys():
            neighbors[node2] = value
        else:
            neighbors[node2] += value

        if node1 not in incomings.keys():
            incomings[node1] = value
        else:
            incomings[node1] += value
        
    def remove_edge(self, node1, node2):
        try:
            del self.incoming[node2][node1]
            del self.outgoing[node1][node2]
        except KeyError:
            print("ERROR: impossible remove edge")

    def __str__(self):
        rstring = ""
        for node in self.outgoing.keys():
            rstring += "{} -> ".format(node)
            for neigh in self.outgoing[node].keys():
                rstring += "({}, {}) ".format(neigh, self.outgoing[node][neigh])
            rstring += "\n"
        return rstring

    def normalize(self):
        total = 0
        for node in self.start_state_prob.keys():
            total += self.start_state_prob[node]
        
        for node in self.start_state_prob.keys():
            p = self.start_state_prob[node] / total
            self.start_state_prob[node] = p

        for node in self.outgoing.keys():
            total = 0
            for neigh in self.outgoing[node].keys():
                total += self.outgoing[node][neigh]
                
            for neigh in self.outgoing[node].keys():
                p = self.outgoing[node][neigh] / total
                self.outgoing[node][neigh] = p
        return

    def simplify(self, threshold = 'auto'):
        
        if threshold == 'auto':
            threshold = self.node_max_freq // 2
        else:
            threshold = self.node_max_freq * threshold
        istates = list(self.start_state_prob.keys())
        for node in istates:
            self._bfs_simplify(threshold)
        self._merge_stars(threshold)

    def _merge_nodes(self, node1, node2):
        #print("let's merge", node1, node2)
        if node1 == node2:
            return
        # transfer outgoing edges
        try:
            outg = self.outgoing[node2]
            #print("outgoing edges of node", node2, "that must be transferred:", outg)
            #print("outgoing edges of node before tranferring", node1, ":", self.outgoing[node1])
            for neigh in outg.keys():
                try:
                    self.outgoing[node1][neigh] += self.outgoing[node2][neigh]
                except KeyError:
                    self.outgoing[node1][neigh] = self.outgoing[node2][neigh]
                # now we have to update the incoming edge in neighbor
                try:
                    self.incoming[neigh][node1] += self.incoming[neigh][node2]
                except KeyError:
                    self.incoming[neigh][node1] = self.incoming[neigh][node2]
                
                del self.incoming[neigh][node2]
        except KeyError:
            pass
        # now change incoming edges
        try:
            #print("inside incoming")
            inc = self.incoming[node2]
            for inc_neigh in inc.keys():
                #print("lets consider this income edge", inc_neigh, "in ", node2, ". Its outgoing edge must be put to ", node1)
                #print("But first update incomings. Before where these", self.incoming[node1])
            
                try:
                    self.incoming[node1][inc_neigh] += self.incoming[node2][inc_neigh]
                except KeyError:
                    try:
                        self.incoming[node1][inc_neigh] = self.incoming[node2][inc_neigh]
                    except KeyError:
                        self.incoming[node1] = dict()
                        self.incoming[node1][inc_neigh] = self.incoming[node2][inc_neigh]
                # now we have to update the outgoing edge in inc_neigh
                try:
                    self.outgoing[inc_neigh][node1] += self.outgoing[inc_neigh][node2]
                except KeyError:
                    self.outgoing[inc_neigh][node1] =  self.outgoing[inc_neigh][node2]
            
                        
                
                #print("now we delete", inc_neigh, "->", node2)
                del self.outgoing[inc_neigh][node2]
                #print("outgoing edges of node after", node1, ":", self.outgoing[node1])
        except KeyError:
            pass
        try:
            del self.start_state_prob[node2]
        except KeyError:
            pass
        try:
            del self.outgoing[node2]
        except KeyError:
            pass
        try:
            del self.incoming[node2]
        except KeyError:
            pass
        
    def _bfs_simplify(self, nf_threshold):
        visited = set()
        remaining_nodes = set(self.outgoing.keys())
        
        while len(remaining_nodes) > 0:
            start = remaining_nodes.pop()
            self._component_bfs_simplify(start, nf_threshold, visited)
            remaining_nodes = set(self.outgoing.keys()).difference(visited)
    
    def _component_bfs_simplify(self, start_node, nf_threshold, visited):
        queue = list()
        visited.add(start_node)
        queue.insert(0, start_node)
        
        while len(queue) > 0:
            c = queue.pop()
            if self.node_frequencies[c] <= nf_threshold:
                # case when an irrelevant node is encountered a first time
                irrelevants_present = True
                loop_count = 0
                while irrelevants_present:
                    irrelevants_present = False
                    neighbors = list(self.get_neighbors(c))
                    #print(neighbors)
                    for n in neighbors:
                        if n == c:
                            continue
                        if self.node_frequencies[n] <= nf_threshold:
                            irrelevants_present = True
                            try:
                                if n in self._star_path_len.keys():
                                    self._star_path_len[c] += self._star_path_len[n]
                            except KeyError:
                                    self._star_path_len[c] = self._star_path_len[n]
                            self._merge_nodes(c, n)
                    loop_count += 1
                try:
                    self._star_path_len[c] += loop_count
                except KeyError:
                    self._star_path_len[c] = loop_count

            for neigh in self.get_neighbors(c):
                if neigh not in visited:
                    queue.insert(0, neigh)
                    visited.add(neigh)

    def _merge_stars(self, nf_threshold):
        #first, merge initial stars
        self.outgoing["_*_"] = dict()
        self.node_frequencies["_*_"] = self.node_max_freq
        self._star_path_len['_*_'] = 0
        total_sprob = 0
        initial_nodes = list(self.start_state_prob.keys())

        star_initial_nodes = list()
        for node in initial_nodes:
            if self.node_frequencies[node] <= nf_threshold:
                star_initial_nodes.append(node)
                self._star_path_len['_*_'] += self._star_path_len[node]
                total_sprob += self.start_state_prob[node]
                self._merge_nodes('_*_', node)
        
        isnlen = len(star_initial_nodes)
        self._star_path_len['_*_'] = (self._star_path_len['_*_']/isnlen) if isnlen > 0 else 0
        self.start_state_prob['_*_'] = total_sprob

        stars = 0
        listOfNodes = list(self.outgoing.keys())
        
        for c in listOfNodes: # for every node in the graph
                
            neighbors = self.get_neighbors(c)          
            merged_star = None
            merged_neigh = dict()
            count = 0
            sum_star_path_length = 0

            for neigh in neighbors:
                
                if self.node_frequencies[neigh] <= nf_threshold:
                    count += 1
                    merged_star = "_*_" + str(stars)
                    if count == 1:
                        self.outgoing[merged_star] = dict()
                        self.incoming[merged_star] = dict()

                    sum_star_path_length += self._star_path_len[neigh]
                    self._merge_nodes(merged_star, neigh)

            if merged_star is not None:
                self._star_path_len[merged_star] = sum_star_path_length / count
                stars += 1
                self.node_frequencies[merged_star] = 0
                
    def add_sample(self, sentence):
        if len(sentence) == 0:
            return
        self.add_initial_state_occurrence(sentence[0])
        for i in range(1, len(sentence)):
            self.add_edge(sentence[i-1], sentence[i])
            self.increment_node_frequency(sentence[i])

    def train_model(self, X, threshold = 0.1):
        for x in X:
            self.add_sample(x)
        #print("Samples added. Number of nodes: {}".format(len(self.outgoing)))
        self.simplify(threshold)
        #print("Model simplified. Number of nodes: {}".format(len(self.outgoing)))
        self = self.normalize()
    
    def sample_probability(self, sample, penality=0.1):
        #print(sample)
        p = 0
        try:
            p = self.start_state_prob[sample[0]]
        except KeyError:
            p = self.start_state_prob["_*_"]
            sample[0] = "_*_"
        
        if p == 0:
            return 0
        
        for i in range(1, len(sample)):
            try:
                outg = self.outgoing[sample[i-1]]
                try:
                    p *= outg[sample[i]] #both present
                except KeyError:
                    found = False
                    # lets see if there is a star node in neighbors
                    for k in outg.keys():
                        if k.startswith("_*_"): # admit a transition
                            p *= outg[k] * penality
                            found = True
                            sample[i] = k
                            break
                    
                    if not found:
                        p = 0
                        break
                        # # se if I can stay in previous node, if it is *
                        # if sample[i-1].startswith("_*_"):
                        #     sample[i] = sample[i-1]
                        #     stay_p = 0
                        #     if i >= 2:
                        #         stay_p = self.outgoing[sample[i-2]][sample[i-1]]
                        #     else:
                        #         stay_p = self.start_state_prob[sample[i-1]]
                        #     # add the penality of stay in star
                        #     balance = 0.0
                        #     v2 = (1-balance)*(1/(1 + 0.1*self._star_path_len[sample[i-1]]))
                        #     #print("part 2", v2)
                        #     stay_p = balance*stay_p + v2
                        #     p *= v2
            except KeyError:
                p = 0
        
        print(p)
        return p

    def predict(self, X):
        predicted = list()
        for x in X:
            predicted.append(self.sample_probability(x))
        return predicted


# tset = ["What is the carrucola ?".split(), "What is music ?".split(), "How this is done ?".split(),  "What is love ?".split()]

# m = MarkovChain()
# m.train_model(tset)

# print(m)