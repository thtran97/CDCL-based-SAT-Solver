from dimacs_parser import parse
import numpy as np
import random
import time
from cnf_data_structure import Clause, CNF_Formula, Implication_Graph


class CDCL_Solver: 
    def __init__(self, input_cnf_file, verbose):
        self.verbose = verbose
        self.list_clause, self.nvars = parse(input_cnf_file, self.verbose)
        self.formula = CNF_Formula(self.list_clause)
        self.graph = Implication_Graph()
        self.decision_level = 0
        # self.propagation_count = 0
        self.nb_learnt_clause = 0
        self.nb_decisions = 0
        self.restart_count = 0
        self.conflict_count = 0
        self.restart_rate = 100
    
    def restart(self):
        self.formula = CNF_Formula(self.list_clause)
        self.graph = Implication_Graph()
        self.decision_level = 0
        self.restart_count += 1
        self.conflict_count = 0
    
    def conflict_analysis(self, conflict_clause): 
        # RETURN : learnt clause, and backtrack_level
        # assert conflict_clause.size > 0
        w = conflict_clause
        pool_literal = w.literal_at_level(self.decision_level)
        if len(pool_literal) <= 1:
            return w, w.get_backtrack_level()
        else: 
            conflict_literal = pool_literal[0]
            antecedent = self.graph.get_antecedent(-conflict_literal)
            if antecedent is not None:
                w = w.resolution_operate(antecedent, conflict_literal)
                return self.conflict_analysis(w)
            else:
                return w, w.get_backtrack_level()

    def pick_branching_variable(self):
        # TODO: Updating heuristics for choosing next branching variables
        ## Random choice
        # unassigned_variables = [x+1 for x in range(self.nvars) if x+1 not in self.graph.assigned_vars]
        # decision = random.choice(unassigned_variables)
        # decision = random.choice([decision, -decision])
        ## Most frequent var first
        counter = self.formula.get_counter(self.graph.assigned_vars)
        assert len(counter) > 0
        # i = 0 
        # most_frequency = counter[list(counter.keys())[i]]
        # pool_literal = []
        # while len(pool_literal) == 0:
        #     for item in counter.keys():
        #         if counter[item] == most_frequency and (abs(item) not in self.graph.assigned_vars):
        #             pool_literal.append(item)
        #     if len(pool_literal)==0 and i<len(list(counter.keys())):
        #         i += 1
        #         most_frequency = counter[list(counter.keys())[i]]
        # decision =  random.choice(pool_literal)
        # i = 0 
        # decision = list(counter.keys())[i]
        # while i<len(counter) and abs(decision) in self.graph.assigned_vars:
        #     i += 1
        #     decision = list(counter.keys())[i]

        pool_literal = list(counter.keys())
        # decision = random.choice(pool_literal)
        for decision in pool_literal:
            if abs(decision) not in self.graph.assigned_vars:
                break
        
        # # Update info
        # self.decision_level += 1
        # self.graph.add_node(decision, None, self.decision_level)
        return decision

    def is_all_assigned(self):
        return self.nvars == self.graph.get_len()

    def solve(self):
        # Problem now is :
        # How to update the implication graph every unit propagation ! 
        # Some solved issues : a data structure helps store and backtrack easily ! 
        initial_time = time.time()
        if self.formula.unit_propagate(self.decision_level, self.graph) is not None:
            print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
            print('UNSAT')
            return -1 # UNSAT
        while not self.is_all_assigned() and len(self.formula.get_counter(self.graph.assigned_vars)) > 0:
            decision = self.pick_branching_variable()
            # self.nb_decisions += 1
            if decision in self.graph.assigned_vars:
                print('Restart: ', self.restart_count)
                print('Learnt clauses: ', self.nb_learnt_clause)
                print('Decisions: ', self.nb_decisions)
                print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
                print('SAT')
                return 1 #SAT  
            elif -decision in self.graph.assigned_vars:
                print('Restart: ', self.restart_count)
                print('Learnt clauses: ', self.nb_learnt_clause)
                print('Decisions: ', self.nb_decisions)
                print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
                print('UNSAT')
                return -1 #SAT 
            else:
                # Update info
                self.decision_level += 1
                self.graph.add_node(decision, None, self.decision_level)

            self.formula.bcp(decision, self.decision_level, self.graph)
            conflict = self.formula.unit_propagate(self.decision_level, self.graph)
            while conflict is not None:
                self.conflict_count += 1
                
                if self.conflict_count > self.restart_rate:
                    self.restart()
                    return self.solve()

                learnt_clause, backtrack_level = self.conflict_analysis(conflict)
                if backtrack_level < 0 :
                    print('Restart: ', self.restart_count)
                    print('Learnt clauses: ', self.nb_learnt_clause)
                    print('Decisions: ', self.nb_decisions)
                    print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
                    print('UNSAT')
                    return -1 #UNSAT 
                self.formula.add_clause(learnt_clause)
                self.nb_learnt_clause += 1
                self.formula.backtrack(backtrack_level)
                self.graph.backtrack(backtrack_level)
                self.decision_level = backtrack_level
                conflict = self.formula.unit_propagate(self.decision_level, self.graph)

        print('Restart: ', self.restart_count)
        print('Learnt clauses: ', self.nb_learnt_clause)
        print('Decisions: ', self.nb_decisions)
        print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
        print('SAT')
        return 1 #SAT        
    
        
    



