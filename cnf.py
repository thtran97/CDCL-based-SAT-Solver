from lazy_clause import Lazy_Clause

class CNF_Formula:
    
    def __init__(self, list_clause):
        # self.formula = [Clause(c) for c in list_clause]
        self.formula = [Lazy_Clause(c) for c in list_clause if len(c) > 0]
        self.value = self.get_value()
        self.nb_original_clauses = len(list_clause)
        self.MAX_NB_CLAUSE = 2*self.nb_original_clauses

    def print_info(self):
        for c in self.formula:
            c.print_info()
        print('[F] Truth value: ', self.value)

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
        ## Normal counter : Count the occurence of all unassigned literals
        # for clause in self.formula:
        #     for literal in clause.clause[:clause.size]:
        #         if literal in counter:
        #             counter[literal] += 1
        #         else:
        #             counter[literal] = 1 

        ## Lazy counter :  Count only the occurences of all unassigned references
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
                assert clause.size > 0
                # Implication graph is used when the lazy clause is visited
                if clause.bcp(literal, decision_level, graph) == -1:
                    self.value = -1
                    conflict_clause = clause
                    break
            elif clause.value == 1:
                continue
        self.value = self.get_value()
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
        # if len(clause.clause) < 10: 
        if len(self.formula) > self.MAX_NB_CLAUSE:
            self.formula.pop(self.nb_original_clauses)
        self.formula += [clause]
 