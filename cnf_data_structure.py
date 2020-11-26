import numpy as np 
import random

class Clause:

    def __init__(self, clause):
        self.clause = clause
        self.value = 0 # 0 = UNASSIGNED, 1 =  TRUE, -1 = FALSE
        self.preprocess()
        self.decision_level = [-1 for _ in self.clause]
        self.size = len(self.clause)
    

    def set_decision_levels(self, decision_level):
        self.decision_level = decision_level
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)

    def print_info(self):
        print('[C] Remaining clause: ', self.clause[:self.size])
        # print('[C] Clause size ', self.size)
        # print('[C] Full clause: ', self.clause)
        # print('[C] Truth value: ', self.value, ' (0=unassigned, -1=unsat, 1=sat)')
        # print('[C] Decision level details: ', self.decision_level)
        # print('[C] Backtrack level: ', self.get_backtrack_level())

    def is_unit(self):
        return self.size == 1

    def is_empty(self):
        return self.size == 0

    def literal_at_level(self, lvl):
        res = []
        for i in range(len(self.clause)):
            if self.decision_level[i] == lvl:
                res.append(self.clause[i])
        return res

    def get_backtrack_level(self):
        # if len(self.decision_level) == 1:
        #     return -1 
        # else:
        m1, m2 = -1, -1
        for x in list(set(self.decision_level)):
            if x >= m1:
                m1, m2 = x, m1
            elif x > m2:
                m2 = x
        if m2 == -1:
            m2 = m1 - 1
        return m2

    def bcp(self, literal, decision_level,graph=None):
        if self.size > 0 and literal in self.clause[:self.size]:
            for i in range(self.size): 
                self.decision_level[i] = decision_level
            self.size = 0 
            self.value = 1 #TRUE
        elif self.size > 0 and -literal in self.clause[:self.size]:
            index = self.clause.index(-literal)
            self.clause[index] = self.clause[self.size-1]
            self.clause[self.size-1] = -literal
            self.decision_level[self.size-1] = decision_level
            self.size -= 1
            if self.size == 0:
                self.value = -1 #FALSE
                return -1
        return 0

    def preprocess(self):
        # remove redundant literals:
        # self.clause =  list(set(self.clause))
        # if contains two opposites literals => TRUE
        for l in self.clause:
            if -l in self.clause:
                self.value = 1 #TRUE
                break

    def restore(self, level):
        offset = 0
        for lvl in self.decision_level[self.size:]:
            if lvl > level:
                offset += 1
            else:
                break
        self.size += offset
        if offset > 0:
            self.value = 0
            self.decision_level[:self.size] = [-1 for _ in range(self.size)]

    def resolution_operate(self, other, literal):
        assert literal in self.clause
        assert -literal in other.clause
        index_literal = self.clause.index(literal)
        res = self.clause[:index_literal] + self.clause[index_literal+1:]
        dl = self.decision_level[:index_literal] + self.decision_level[index_literal+1:]
        for i,l in enumerate(other.clause):
            if (abs(l) != abs(literal)) and (l not in res):
                res.append(l)
                dl.append(other.decision_level[i])
        resolved_clause = Clause(res)
        resolved_clause.set_decision_levels(dl)
        resolved_clause.size = 0
        return resolved_clause

    def restart(self):
        self.value = 0
        self.decision_level = [-1 for _ in self.clause]
        self.size = len(self.clause)

class CNF_Formula:
    
    def __init__(self, list_clause):
        self.formula = [Clause(c) for c in list_clause]
        # self.formula = [Lazy_Clause(c) for c in list_clause]

        self.value = self.get_value()
        # self.nvars = nvars
        # self.assignment = Assignment(nvars)

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
        elif 0 in list_values:
            return 0
        else: 
            return 1 

    def get_counter(self,assigned_vars):
        counter = {}
        for clause in self.formula:
            for literal in clause.clause[:clause.size]:
                if literal in counter:
                    counter[literal] += 1
                else:
                    counter[literal] = 1 

        # ## Lazy counter
        # unassigned_refs = []
        # for clause in self.formula:
        #     if clause.refA not in assigned_vars:
        #         unassigned_refs.append(clause.refA)
        #     if clause.refB not in assigned_vars:
        #         unassigned_refs.append(clause.refB)

        # for literal in unassigned_refs:
        #     if literal in counter:
        #         counter[literal] += 1
        #     else:
        #         counter[literal] = 1 

        counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse= True)}
        return counter

    def is_sat(self):
        return self.value
    
    def bcp(self, literal, decision_level,graph):
        for clause in self.formula:
            if clause.bcp(literal, decision_level, graph) == -1:
                self.value = -1
                return clause
        self.value = self.get_value()
        return None 
            
    # def unit_propagate(self, decision_level, graph=None):
    #     for clause in self.formula:
    #         if clause.is_unit():
    #             unit_literal = clause.clause[0]
    #             if graph is not None:
    #                 graph.add_node(unit_literal, clause, decision_level)
    #             conflict_clause = self.bcp(unit_literal, decision_level, graph)
    #             if conflict_clause is not None:
    #                 return conflict_clause
    #             else:
    #                 return self.unit_propagate(decision_level, graph)
    #         else: continue
    #     return None 

    def unit_propagate(self, decision_level, graph=None):
        unit_clauses = [clause for clause in self.formula if clause.is_unit()]
        while len(unit_clauses)>0:
            clause = unit_clauses[0]
            unit_literal = clause.clause[0]
            if graph is not None and (unit_literal not in graph.assigned_vars):
                graph.add_node(unit_literal, clause, decision_level)
            conflict_clause = self.bcp(unit_literal, decision_level, graph)
            if conflict_clause is not None:
                return conflict_clause
            else:
                unit_clauses = [clause for clause in self.formula if clause.is_unit()]
        return None 

    def backtrack(self, backtrack_level):
        for clause in self.formula:
            clause.restore(backtrack_level)
        self.value = 0

    def add_clause(self, clause):
        # clause is a Clause type
        # TODO: Add strategy for adding/removing learnt clause HERE
        if clause not in self.formula:
            self.formula += [clause]
        
class Implication_Graph:

    def __init__(self):
        self.graph = dict()
        self.assigned_vars = []
        
    def add_node(self, literal, antecedent, decision_level):
        assert abs(literal) not in self.assigned_vars
        self.graph[literal] = [antecedent, decision_level]
        self.assigned_vars.append(abs(literal))

    def remove_node(self, literal):
        if literal in self.graph.keys():
            self.graph.pop(literal)
        elif -literal in self.graph.keys():
            self.graph.pop(-literal)
        self.assigned_vars.remove(abs(literal))

    def backtrack(self, backtrack_level):
        assigned_list = list(self.graph.keys())
        for node in reversed(assigned_list):
            if self.graph[node][1] > backtrack_level:
                self.remove_node(node)
            # else:
            #     break   

    def get_len(self):
        return len(self.assigned_vars)

    def get_antecedent(self, literal):
        if  literal in self.graph.keys():
            return self.graph[literal][0]
        else:
            return None

class Lazy_Clause:
    
    def __init__(self, list_literal):
        self.clause = list_literal
        self.decision_level = [-1 for _ in self.clause]
        self.value = 0 # 0 = UNASSIGNED, 1 =  TRUE, -1 = FALSE
        self.size = len(self.clause)
        if self.size > 1:
            self.refA, self.refB = random.sample(self.clause,2)
            self.indexA, self.indexB = self.clause.index(self.refA), self.clause.index(self.refB)
        elif self.size == 1: 
            self.refA = self.clause[0]
            self.refB = self.refA
            self.indexA, self.indexB = 0,0

    def print_info(self):
        print('[C] Remaining clause: ', self.clause[:self.size])
        print('[C] Refs: ', self.refA, self.refB)
        print('[C] Truth value: ', self.value)
        print('[C] Full clause ', self.clause)
        print('[C] Details on decision_level: ', self.decision_level)

    def is_unit(self):
        return self.size == 1

    def check_n_update(self, graph):
        offset = 0
        for i in range(len(self.clause)):
            if self.clause[i] in list(graph.graph.keys()):
                previous_decision_level = graph.graph[self.clause[i]][1]
                for i in range(self.size):
                    if self.decision_level[i] == -1:
                        self.decision_level[i] = previous_decision_level
                self.value = 1
                offset = self.size 
                break
            elif -self.clause[i] in list(graph.graph.keys()):
                self.decision_level[i] = graph.graph[-self.clause[i]][1]
                offset += 1
                if offset == self.size:
                    self.value = -1 
                    break

        self.size -= offset
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)
        self.clause = self.clause[-self.size:] + self.clause[:-self.size]
        self.decision_level = self.decision_level[-self.size:] + self.decision_level[:-self.size]
        self.indexA = self.clause.index(self.refA)
        self.indexB = self.clause.index(self.refB)

        return self.value

    def pick_new_ref(self):
        assert self.size > 0
        if self.size <= 1:
            return self.clause[0], 0
        
        new_ref = self.refA
        new_index = 0

        while (new_ref != self.refB and new_ref != self.refB):
            new_ref = random.choice(self.clause[:self.size])
            new_index = self.clause.index(new_ref)
            assert self.decision_level[new_index] == -1
    
        return new_ref, new_index

    def bcp(self, literal, decision_level, graph):

        if self.size == 0: 
            return self.value

        # If clause is unit
        if self.size == 1:
            if literal == self.refA:
                self.decision_level[self.indexA] = decision_level
                self.size = 0
                self.value = 1
                return 1
            elif -literal == self.refA:
                self.decision_level[self.indexA] = decision_level
                self.size = 0 
                self.value = -1
                return -1 
            else: 
                self.value = 0
                return 0

        # Assumption : clause is not unit => that's why we need to bcp
        if self.size > 1:
            if literal == self.refA or literal == self.refB:
                self.value = 1 
                self.decision_level[:self.size] = [decision_level for _ in range(self.size)]
                self.size = 0
                return 1
            elif -literal == self.refA or -literal == self.refB:
                # check and update other literals 
                # if there is one true -> SAT
                value =  self.check_n_update(graph)
                if self.size == 0: 
                    return value            
                elif value == 0:
                    if -literal == self.refA:
                        self.clause[self.indexA] = self.clause[self.size-1]
                        self.clause[self.size-1] = self.refA
                        self.decision_level[self.size-1] = decision_level
                        self.size -= 1
                        if self.size > 0:
                            self.refA, self.indexA = self.pick_new_ref()
                            return 0
                        else:
                            self.value = -1
                            return -1
                    elif -literal == self.refB:
                        self.clause[self.indexB] = self.clause[self.size-1]
                        self.clause[self.size-1] = self.refB
                        self.decision_level[self.size-1] = decision_level
                        self.size -= 1
                        if self.size > 0:
                            self.refB, self.indexB = self.pick_new_ref()
                            return 0
                        else: 
                            self.value = -1
                            return -1 
            else:
                self.value = 0
                return 0


    def restore(self, level):
        offset = 0
        for lvl in self.decision_level:
            if lvl > level:
                offset += 1
            else:
                break
        self.size = offset
        if self.size > 0:
            self.value = 0
            self.decision_level[:self.size] = [-1 for _ in range(self.size)]
            # if self.decision_level[self.indexA] > 0:
            self.refA, self.indexA = self.pick_new_ref()
            # if self.decision_level[self.indexB] > 0:
            self.refB, self.indexB = self.pick_new_ref()
 
    def literal_at_level(self, lvl):
        res = []
        for i in range(len(self.clause)):
            if self.decision_level[i] == lvl:
                res.append(self.clause[i])
        return res

    def get_backtrack_level(self):
        # if len(self.decision_level) == 1:
        #     return -1 
        # else:
        m1, m2 = -1, -1
        for x in list(set(self.decision_level)):
            if x >= m1:
                m1, m2 = x, m1
            elif x > m2:
                m2 = x
        if m2 == -1:
            m2 = m1 - 1
        return m2

    def resolution_operate(self, other, literal):
        assert (literal in self.clause and -literal in other.clause) # or  (-literal in self.clause and literal in other.clause)
        index_literal = self.clause.index(literal)
        res = self.clause[:index_literal] + self.clause[index_literal+1:]
        dl = self.decision_level[:index_literal] + self.decision_level[index_literal+1:]
        for i,l in enumerate(other.clause):
            if (abs(l) != abs(literal)) and (l not in res):
                res.append(l)
                dl.append(other.decision_level[i])
        resolved_clause = Lazy_Clause(res)
        resolved_clause.set_decision_levels(dl)
        resolved_clause.size = 0
        return resolved_clause

    def set_decision_levels(self, decision_level):
        self.decision_level = decision_level
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)
        

        