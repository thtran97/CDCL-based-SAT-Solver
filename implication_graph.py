class Implication_Graph:

    def __init__(self):
        self.graph = dict()
        self.assigned_vars = []
        
    def add_node(self, literal, antecedent, decision_level):
        assert literal not in self.assigned_vars
        assert -literal not in self.assigned_vars
        self.graph[literal] = [antecedent, decision_level]
        self.assigned_vars = list(self.graph.keys())

    def remove_node(self, literal):
        if literal in self.graph.keys():
            self.graph.pop(literal)
        elif -literal in self.graph.keys():
            self.graph.pop(-literal)
        self.assigned_vars = list(self.graph.keys())
        assert (literal not in self.graph.keys()) and (-literal not in self.graph.keys())

    def backtrack(self, backtrack_level):
        assigned_list = list(self.graph.keys())
        for node in reversed(assigned_list):
            if self.graph[node][1] > backtrack_level:
                self.remove_node(node)
        list_lvl = [self.graph[item][1] for item in self.graph.keys()]
        if len(list_lvl)>0:
            assert max(list_lvl) <= backtrack_level

    def get_antecedent(self, literal):
        if  literal in self.graph.keys():
            return self.graph[literal][0]
        else:
            return None