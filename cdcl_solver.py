from dimacs_parser import parse
import numpy as np
import random
import time
# from cnf_data_structure import Clause, CNF_Formula, Implication_Graph
from clause import Clause
from lazy_clause import Lazy_Clause
from cnf import CNF_Formula
from implication_graph import Implication_Graph

class CDCL_Solver: 
    def __init__(self, input_cnf_file, verbose):
        self.assert_mode = False
        self.verbose = verbose
        self.list_clause, self.nvars = parse(input_cnf_file, self.verbose)
        self.formula = CNF_Formula(self.list_clause)
        self.graph = Implication_Graph()
        self.decision_level = 0
        # self.propagation_count = 0
        self.nb_clauses = len(self.list_clause)
        self.nb_learnt_clause = 0
        self.nb_decisions = 0
        self.restart_count = 0
        self.conflict_count = 0
        self.analysis_count = 0
        self.restart_rate = 100
        self.is_sat = 0 
        self.conflict = None
    
    def restart(self):
        self.formula = CNF_Formula(self.list_clause)
        self.graph = Implication_Graph()
        self.decision_level = 0
        self.restart_count += 1
        self.conflict_count = 0
        self.is_sat = 0
        self.conflict = None
    
    def conflict_analysis(self, conflict_clause): 
        # RETURN : learnt clause, and backtrack_level
        # assert conflict_clause.size > 0
        self.analysis_count += 1
        if self.analysis_count >= 100:
            self.analysis_count = 0
            return None, -100
        w = conflict_clause
        pool_literal = w.literal_at_level(self.decision_level)
        # print(self.decision_level)
        # w.print_info()
        assert len(pool_literal) > 0
        if len(pool_literal) == 1:
            self.analysis_count = 0
            return w, w.get_backtrack_level()
        else: 
            i = 0
            antecedent = None
            while i< len(pool_literal) and antecedent is None:
                conflict_literal = pool_literal[i]
                antecedent = self.graph.get_antecedent(-conflict_literal)
                i += 1
            if antecedent is None:
                w.print_info()
                print(pool_literal)
                for i in pool_literal:
                    print(self.graph.graph[i])
            assert antecedent is not None
            w = w.resolution_operate(antecedent, conflict_literal)
            return self.conflict_analysis(w)

    def pick_branching_variable(self):
        # TODO: Updating heuristics for choosing next branching variables
        ## Random choice
        # unassigned_variables = [x+1 for x in range(self.nvars) if x+1 not in self.graph.assigned_vars]
        # # decision = random.choice(unassigned_variables)
        # decision = random.choice([decision, -decision])
        ## Most frequent var first
        counter = self.formula.get_counter()
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
        decision = random.choice(pool_literal)
        i = 0
        while i < len(pool_literal):
            decision = pool_literal[i]
            if decision not in self.graph.assigned_vars:
                break
            i += 1
        # print(pool_literal)
        if decision in self.graph.assigned_vars or -decision in self.graph.assigned_vars:
            def unassigned_criterion_sat(x): 
                return (x not in self.graph.assigned_vars) and (-x not in self.graph.assigned_vars)
            unassigned_variables = [x+1 for x in range(self.nvars) if unassigned_criterion_sat(x+1)]
            # print(unassigned_variables)
            decision = random.choice(unassigned_variables)        # print(pool_literal)
            # print(self.graph.assigned_vars)
            # print(decision)
        assert decision not in self.graph.assigned_vars
        assert -decision not in self.graph.assigned_vars
        # # Update info
        # self.decision_level += 1
        # self.graph.add_node(decision, None, self.decision_level)
        return decision

    def is_all_assigned(self):
        return self.nvars == len(self.graph.assigned_vars)

    def solve(self):
        # Problem now is :
        # How to update the implication graph every unit propagation ! 
        # Some solved issues : a data structure helps store and backtrack easily ! 
        stop = False
        initial_time = time.time()
        self.is_sat, self.conflict =  self.formula.unit_propagate(self.decision_level, self.graph)
        if self.verbose:
            print('=====================[  Search Statistics ]=====================')
            

        while self.is_sat == 0 and not stop: # and not self.is_all_assigned(): #and len(self.formula.get_counter(self.graph.assigned_vars)) > 0:
            assert self.formula.get_value() == self.is_sat
            assert self.conflict is None
            if self.is_all_assigned():
                print(self.is_sat)
                print(self.graph.assigned_vars)
                print(list(set(self.graph.assigned_vars)))
            assert not self.is_all_assigned() 
            decision = self.pick_branching_variable()
            self.nb_decisions += 1
            self.decision_level += 1
            self.graph.add_node(decision, None, self.decision_level)
            self.is_sat, self.conflict = self.formula.bcp(decision, self.decision_level, self.graph)
            
            if self.is_sat == 0:
                if self.is_all_assigned():
                    list_value = [c.value for c in self.formula.formula]
                    ind = list_value.index(0)
                    self.formula.formula[ind].print_info()
                    print(list_value[:])
                    print(self.graph.assigned_vars)    
                    print(decision)
                assert not self.is_all_assigned()
                self.is_sat, self.conflict = self.formula.unit_propagate(self.decision_level, self.graph)

            if self.is_sat == 0:
                assert not self.is_all_assigned()

            if self.is_sat == 1:
                assert self.formula.get_value() == self.is_sat
                break

            while self.is_sat == -1 and not stop:
                assert self.conflict is not None
                learnt_clause, backtrack_level = self.conflict_analysis(self.conflict)
                if backtrack_level == -100:
                    self.restart()      
                elif backtrack_level == -1 :
                    self.is_sat = -1 
                    stop = True
                else:
                    self.formula.add_clause(learnt_clause)
                    self.nb_learnt_clause += 1
                    self.graph.backtrack(backtrack_level)
                    self.formula.backtrack(backtrack_level, self.graph)
                    # print("Backtrack to ", backtrack_level)
                    self.decision_level = backtrack_level
                    # self.conflict = None
                    self.is_sat, self.conflict = self.formula.unit_propagate(self.decision_level, self.graph)
                    # if self.conflict is not None:
                        # self.conflict.print_info()
                    if self.is_sat == 0: 
                        assert not self.is_all_assigned()
                ## If too much conflicts, RESTART IT NOW !
                self.conflict_count += 1
                if self.conflict_count > self.restart_rate:
                    self.restart()


            # print(stop, self.is_sat, self.conflict)
            # assert self.conflict is None

        assert self.is_sat != 0
        assert self.is_sat == self.formula.get_value()
        if self.is_all_assigned():
            print('All vars assigned !')
        else: 
            print('Early quit !')
            

        print('Restart: ', self.restart_count)
        print('Learnt clauses: ', self.nb_learnt_clause)
        print('Decisions: ', self.nb_decisions)
        print('CPU time: {0:10.6f}s '.format(time.time()-initial_time))
        
        if stop: 
            assert self.is_sat == -1
            print('UNSAT')
        elif not stop and self.is_sat == 1:
            print('SAT')
        elif not stop and self.is_sat == -1:
            print('UNSAT')
        else: #But practically, this should not happen !
            print('UNRESOLVED !')

        ## Check it

        assigned_vars = self.graph.assigned_vars
        test_formula = CNF_Formula(self.list_clause)
        test_formula.formula = [Clause(c) for c in self.list_clause if len(c) > 0]
        test_graph = Implication_Graph()
        for i, literal in enumerate(assigned_vars):
            test_formula.bcp(literal, i, test_graph)

        # if conflict is not None:
        #     conflict.print_info()

        if self.is_sat == 1:
            # print(test_formula.value)
            # test_list_value = [c.value for c in test_formula.formula]
            # list_value = [c.value for c in self.formula.formula]
            # print(list_value[:])
            # print(test_list_value)
            # print(assigned_vars)
            assert test_formula.get_value() == 1
        print('Verified !')
            

        return self.formula.get_value    
        
    



