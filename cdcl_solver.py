
from dimacs_parser import parse
import numpy as np
import random

class CDCL_Solver:
    
    def __init__(self,input_cnf_file, verbose):
        self.verbose = verbose
        self.formula, self.nvars = parse(input_cnf_file, verbose)
        self.nclauses = len(self.formula)
        self.dual_formula = [list() for i in range(len(self.formula))]
        self.learnt_clauses = []
        self.conflict_clause = []
        self.assignment = np.zeros(self.nvars)
        self.decision_level = 0
        self.branching_count = 1
        self.graph = dict()    

    def bcp(self, unit):
        for i, clause in enumerate(self.formula):
            if unit in clause:
                self.dual_formula[i] += clause
                self.formula[i] = [True]
            if -unit in clause:
                self.dual_formula[i].append(-unit)
                self.formula[i] = [x for x in clause if x != -unit]
                if len(self.formula[i]) == 0: 
                    self.conflict_clause = self.dual_formula[i]
                    self.formula[i] = [False] #CONFLICT
                    return -1
        return 0 # NO CONFLiCT

    def unit_propagate(self):
        c_i = 0
        while c_i < self.nclauses:
            if len(self.formula[c_i]) == 1 and self.formula[c_i][0] not in [True,False]: # c_i is a unit clause
                unit = self.formula[c_i][0]
                antecedent = self.dual_formula[c_i]
                self.branching_count += 1
                self.update_implication_graph(unit, antecedent)
                if self.bcp(unit) == -1: # CONFLICT
                    break
                c_i = 0
            else:
                c_i += 1
        return 0 # NO CONFLICT

    def pick_branching_variable(self):
        # In the first manner, we choose randomly an unassigned variable
        # Then assign TRUE 
        unassiged_variables = [i for i in range(self.nvars) if self.assignment[i] == 0]
        decision = random.choice(unassiged_variables)
        self.decision_level += 1
        self.branching_count = 0
        self.update_implication_graph(decision, [])


    def assign(self, litteral, dl):
        self.assignment[abs(litteral)-1] = litteral
        self.decision_level = dl
        self.branching_count = 0
        self.update_implication_graph(litteral, [])
        self.bcp(litteral)

    def update_implication_graph(self, node, antecedent):
        self.graph[node] = [antecedent, self.decision_level, self.branching_count] 
        self.assignment[abs(node)-1] = node

    def resolution_operator(self,clause1, clause2, var):
        # resolve operator for two clauses
        # iff var in one clause & -var in the another
        resolved_clause = []
        resolved_clause += [x for x in set(clause1+clause2) if abs(x) != abs(var)]
        return resolved_clause
        
    def conflict_analysis(self):
        backtrack_level = self.decision_level
        assert self.conflict_clause is not None
        learnt_clause = self.conflict_clause    
        previous_clause = []
        while learnt_clause != previous_clause:
            previous_clause = learnt_clause
            priori_order = [list(self.graph.keys()).index(-l) for l in previous_clause]
            last_recent_litteral = previous_clause[np.argmax(priori_order)]
            parent, current_dl, _ = self.graph[-last_recent_litteral]  
            if len(parent) > 0:
                learnt_clause = self.resolution_operator(previous_clause, parent, last_recent_litteral)
                backtrack_level = min(backtrack_level, current_dl)  
            else:
                learnt_clause = previous_clause
        if learnt_clause not in self.learnt_clauses:
            self.learnt_clauses.append(learnt_clause)
        return backtrack_level

    def backtracking(self, formula, assignment):
        # Clear all bcp at level >= backtrack_level
        # Change decision variable at backtrack_level
        # Repeat
        pass


#
# solver = CDCL_Solver("cnf_instances/test.cnf",1)
# solver.assign(-7,2)
# solver.unit_propagate()


    


    
    
         
