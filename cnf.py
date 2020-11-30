from lazy_clause import Lazy_Clause

class CNF_Formula:
    
    def __init__(self, list_clause):
        # self.formula = [Clause(c) for c in list_clause]
        self.formula = [Lazy_Clause(c) for c in list_clause if len(c) > 0]

        self.value = self.get_value()
        # self.nvars = nvars
        # self.assignment = Assignment(nvars)
        # self.nb_propagate = 0
        # self.max_UP = 100

    def print_info(self):
        for c in self.formula:
            # print(c.clause)
            c.print_info()
        print('[F] Truth value: ', self.value)
        # self.assignment.print_info()

    def get_value(self):
        list_values = [c.value for c in self.formula]
        if -1 in list_values:
            return -1
        else:
            if 0 in list_values:
                return 0
            else: 
                return 1 

    def get_counter(self):
        counter = {}
        # for clause in self.formula:
        #     for literal in clause.clause[:clause.size]:
        #         if literal in counter:
        #             counter[literal] += 1
        #         else:
        #             counter[literal] = 1 

        ## Lazy counter
        unassigned_refs = []
        for clause in self.formula:
            if clause.size == 1:
                unassigned_refs.append(clause.refA)
            elif clause.size > 1:
                unassigned_refs.append(clause.refA)
                unassigned_refs.append(clause.refB)
        for literal in unassigned_refs:
            if literal in counter:
                counter[literal] += 1
            else:
                counter[literal] = 1 
        counter = {k: freq for k, freq in sorted(counter.items(), key=lambda item: item[1], reverse= True)}
        assert len(counter) > 0
        return counter

    def is_sat(self):
        return self.value
    
    def bcp(self, literal, decision_level, graph):
        conflict_clause = None
        for clause in self.formula:
            if clause.value == -1:
                self.value = -1
                conflict_clause = clause
                break
            elif clause.value == 0:
                # clause.print_info()
                assert clause.size > 0
                # Implication graph is used when the lazy clause is visited
                if clause.bcp(literal, decision_level, graph) == -1:
                    self.value = -1
                    conflict_clause = clause
                    break
            elif clause.value == 1:
                continue
        self.value = self.get_value()
        # if self.value == 1:
        #     # list_values = [c.value for c in self.formula]
        #     # print(list_values)
        #     print('SAT after BCP')
        # if self.value == 0:
        #     print(len(graph.assigned_vars))
        return self.value, conflict_clause
            
    def unit_propagate(self, decision_level, graph=None):
        nb_clauses = len(self.formula)
        i = 0
        conflict_clause = None
        while i< nb_clauses and self.value == 0:
            clause = self.formula[i]
            if clause.is_unit():  
                # unit_literal = clause.clause[0]
                unit_literal = clause.refA
                # assert clause.decision_level[clause.indexA] == -1
                # if clause.decision_level[clause.indexA] != -1:
                #     clause.print_info()
                if graph is not None and (unit_literal not in graph.assigned_vars):
                    graph.add_node(unit_literal, clause, decision_level)
                is_sat, conflict_clause = self.bcp(unit_literal, decision_level, graph)
                if is_sat == -1:
                    self.value == -1
                else:
                    self.value, conflict_clause = self.unit_propagate(decision_level, graph) 
                    break
            else: 
                i += 1
        return self.value, conflict_clause

    # def unit_propagate(self, decision_level, graph=None):
    #     unit_clauses = [clause for clause in self.formula if clause.is_unit()]
    #     self.nb_propagate += 1
    #     while len(unit_clauses)>0 and self.nb_propagate <= self.max_UP:
    #         clause = unit_clauses[0]
    #         unit_literal = clause.clause[0]
    #         if graph is not None and (unit_literal not in graph.assigned_vars):
    #             graph.add_node(unit_literal, clause, decision_level)
    #         conflict_clause = self.bcp(unit_literal, decision_level, graph)
    #         if conflict_clause is not None:
    #             return conflict_clause
    #         else:
    #             unit_clauses = [clause for clause in self.formula if clause.is_unit()]
    #     if self.nb_propagate > self.max_UP:
    #         print("Looping error")
    #         return -1
    #     return None 

    def backtrack(self, backtrack_level, graph):
        for clause in self.formula:
            clause.restore(backtrack_level, graph)
        self.value = 0
        # self.nb_propagate = 0

    def add_clause(self, clause):
        # clause is a Clause type
        # TODO: Add strategy for adding/removing learnt clause HERE
        # list_current_clauses = [c.clause for c in self.formula]
        # if clause.clause not in list_current_clauses and len(clause.clause) <= 6:
        self.formula += [clause]
