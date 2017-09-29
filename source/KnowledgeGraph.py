from Graph import Graph
from random import randint

class KnowledgeGraph:
    """
    This class is used to model the knowledge contained in KBS as a directed annotated graph.
    """
    def __init__(self, domains_to_relations):
        self._graph = Graph()
        # entry_counter is the next DataEntry ID expected to be added in the dataset.
        # In other words, is the number of DataEntry objects inserted in the graph.
        self.entry_counter = 0
        self.relations = set()
        self.domain_to_nodes = dict()
        self.domains_to_relations = domains_to_relations

    def update(self, data, total_downloaded):
        """
        Add nodes and edges to the Knowledge Graph according to new data available.

        Parameters:
        -----------
            -   `data`: json data fetched from the Knowledge Base Server that is also
            put under a process of data validation.
            -   `total_downloaded`: the total number of data entries downloaded, that
            may differ from the one of data entries passed to this function. This number
            is used to keep track of the last record fetched from the KBS.
        
        Returns:
        --------
        Nothing
        """
        for di in data:
            node1 = di['c1']
            node2 = di['c2']

            i1 = node1.rfind('bn:')
            i2 = node2.rfind('bn:')
            
            node1 = node1[i1:]
            node2 = node2[i2:]
            for dom in di['domains']:
                dom = dom.lower()
                nodes_in_domain = None
                try:
                    nodes_in_domain = self.domain_to_nodes[dom]
                except KeyError:
                    nodes_in_domain = set()
                    self.domain_to_nodes[dom] = nodes_in_domain
                nodes_in_domain.add(node1)

            self.relations.add(di['relation'].lower())
            self._graph.add_edge(node1, node2, di)

        self.entry_counter += total_downloaded
        self.nodes = list(set(self._graph.outgoing.keys()).union(set(self._graph.incoming.keys())))
        
    def pick_entity_and_relation(self, domain):
        """
        Search the Knowledge Graph for an entity we know little about.

        The aim of this function is to pick an entity that has no edge for a relation
        that the domain the entity belongs to admits.

        Parameters:
        -----------
            - `domain`: the domain the picked entity must belong to.
        
        Returns:
        --------
        a triple (entity id, entity name, relation) where
            - entity id is the babelnet id
            - entity name is the textual representation "entity::id" of the entity
            - relation is the chosen relation for the question
        """
        unseen_relations = set()
        chosenEntity = None
        nodesToChooseFrom = None
        entityName = None
        try:
            nodesToChooseFrom = list(self.domain_to_nodes[domain])
        except KeyError:
            print("No nodes in the current domain.")
            nodesToChooseFrom = list(self._graph.outgoing.keys())
        
        while len(unseen_relations) == 0 and len(nodesToChooseFrom) > 0:
            chosenEntity = nodesToChooseFrom[randint(0, len(nodesToChooseFrom)-1)]
            seen_relations = set()
            for other in self._graph.outgoing[chosenEntity].keys():
                for relation in self._graph.outgoing[chosenEntity][other]:
                    seen_relations.add(relation['relation'].lower())
                    entityName = relation['c1']
            try:
                unseen_relations = self.domains_to_relations[domain].difference(seen_relations)
            except KeyError:
                print("No specialized relations")
                unseen_relations = self.relations.difference(seen_relations)

        if len(unseen_relations) == 0:
            return None
        else:
            return (chosenEntity, entityName, list(unseen_relations)[randint(0, len(unseen_relations)-1)])

    def query(self, entities, relations):
        """
        query the Knowledge Graph in search for all the tuples `(e1, r, e2)` such that
        e1 = entities[0] or [e1, e2] = entities and r = relation.
        
        Parameters:
        -----------
            - `entities`: a list of tuples of the form (x, y) where x is a SpaCy dependency
            tag and y is a dictionary representing a BabelFy annotation.
            - `relation`: a string representing a relation between entities.
        
        Returns:
        --------
        A list of dictionaries, where each dictionary is in the KBS entry format.
        """
        result = list()

        if len(entities) == 1:
            ent_id = entities[0][1]['bab_id']
            try:
                outg = self._graph.outgoing[ent_id]
                for relation in relations:
                    if len(result) == 0:
                        for key in outg.keys():
                            for r in outg[key]:
                                if r['relation'].lower() == relation.lower():
                                    result.append( r )
            except KeyError:
                pass
            
        else:
            couples = list()

            for i in range(1, len(entities)):
                couples.append([entities[0], entities[i]])
            
            for entities in couples:
                # two entities
                ent_1 = entities[0][1]['bab_id']
                ent_2 = entities[1][1]['bab_id']
                
                try:
                    for relation in relations:
                        if len(result) == 0:
                            g_relations = self._graph.outgoing[ent_1][ent_2]
                            for r in g_relations:
                                if r['relation'] == relation:
                                    result.append( r )        
                except KeyError:
                    pass
            
        return result

    def stats(self):
        nodes = set(self._graph.incoming.keys()).union(set(self._graph.outgoing.keys()))
        return len(nodes)