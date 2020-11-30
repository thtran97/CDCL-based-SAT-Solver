import random 

class Lazy_Clause:
    
    def __init__(self, list_literal):
        assert len(list_literal) > 0
        #### DELETE THIS AFTER TEST
        # self.normal_clause = Clause(list_literal)
        ####
        self.clause = list_literal
        self.decision_level = [-1 for _ in self.clause]
        self.value = 0 # 0 = UNASSIGNED, 1 =  TRUE, -1 = FALSE
        self.size = len(self.clause)
        # Pick two references for a new clauses
        # TODO WARNING: for learnt clauses, we need to update again the decision levels, size and pick new references
        if len(self.clause) > 1:
            self.refA, self.refB = random.sample(self.clause,2)
            self.indexA, self.indexB = self.clause.index(self.refA), self.clause.index(self.refB)
        elif len(self.clause) == 1:
            self.refA = self.clause[0]
            self.refB = self.refA
            self.indexA, self.indexB = 0,0

    def print_info(self):
        print('[C] Remaining clause: ', self.clause[:self.size])
        print('[C] Refs: ', self.refA, self.refB)
        print('[C] Index: ', self.indexA, self.indexB)
        print('[C] Truth value: ', self.value)
        print('[C] Full clause ', self.clause)
        print('[C] Details on decision_level: ', self.decision_level)

    def is_unit(self):
        if self.size == 1:
            assert self.refA == self.refB
            assert self.decision_level[self.indexA] == -1
            return 1
        else:
            return 0

    def update(self, graph):
        assigned_vars = graph.assigned_vars
        sat_dl = []
        for i in range(len(self.clause)):
            # If there is one true literal in list of assigned variables => SAT and break
            if self.clause[i] in assigned_vars:
                self.decision_level[i] = graph.graph[self.clause[i]][1]
                sat_dl.append(graph.graph[self.clause[i]][1])
            # Else if the literal is false, update info
            elif -self.clause[i] in assigned_vars and self.decision_level[i] == -1:
                self.decision_level[i] = graph.graph[-self.clause[i]][1]
            # Else continue checking next literal
            else: continue 
        
        if len(sat_dl)>0:
            self.value = 1
            for i in range(len(self.decision_level)):
                if self.decision_level[i] == -1:
                    self.decision_level[i] = min(sat_dl) 
                elif self.decision_level[i] > min(sat_dl):
                    self.decision_level[i] = min(sat_dl)

        self.size = self.decision_level.count(-1)
        if self.size == 0 and len(sat_dl) == 0:
            self.value = -1
        
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)
        self.clause = self.clause[-self.size:] + self.clause[:-self.size]
        self.decision_level = self.decision_level[-self.size:] + self.decision_level[:-self.size]
        # self.indexA = self.clause.index(self.refA)
        # self.indexB = self.clause.index(self.refB)

    def check_n_update(self, graph):
        # print('Before check')
        # self.print_info()
        # assert self.size > 0
        assigned_vars = graph.assigned_vars
        sat_dl = []
        for i in range(len(self.clause)):
            # If there is one true literal in list of assigned variables => SAT and break
            if self.clause[i] in assigned_vars:
                self.decision_level[i] = graph.graph[self.clause[i]][1]
                sat_dl.append(graph.graph[self.clause[i]][1])
                # for i in range(self.size):
                #     # if self.decision_level[i] == -1:
                    #     self.decision_level[i] = previous_decision_level
                #     self.decision_level[i] = previous_decision_level
                # self.value = 1
                # self.size = 0
                # self.remove_refs()
                # break
            # Else if the literal is false, update info
            elif -self.clause[i] in assigned_vars and self.decision_level[i] == -1:
                self.decision_level[i] = graph.graph[-self.clause[i]][1]
                # self.size -= 1
            # Else continue checking next literal
            else: continue 
        
        if len(sat_dl)>0:
            for i in range(len(self.decision_level)):
                if self.decision_level[i] == -1:
                    self.decision_level[i] = min(sat_dl) 
                elif self.decision_level[i] > min(sat_dl):
                    self.decision_level[i] = min(sat_dl)
            self.value = 1
            self.size = 0 
            self.remove_refs()

        self.size = self.decision_level.count(-1)
        ## Arrange the decision level and according literals
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)
        assert self.size >= 0

        if self.size > 0:
            ## But unassigned literals now are at the end (decision_level = -1) 
            ## So move them to the head
            # print('After check 1')
            # self.print_info()
            self.clause = self.clause[-self.size:] + self.clause[:-self.size]
            self.decision_level = self.decision_level[-self.size:] + self.decision_level[:-self.size]
            # self.print_info()
            ## After moving too many times, indexes and refs are also changes
            ## Update them !
            # self.print_info()
            self.indexA = self.clause.index(self.refA)
            self.indexB = self.clause.index(self.refB)
            self.pick_new_ref()

            assert self.value == 0
            if self.size == 1:
            #     # self.print_info()
            #     # print(assigned_vars)
                for l in self.clause[self.size:]:
                    assert -l in assigned_vars 
        else:
            if self.value != 1:
                self.value = -1
                self.remove_refs()

        assert self.size == self.decision_level.count(-1)

    def pick_new_ref(self):
        assert self.size > 0
        assert self.size == self.decision_level.count(-1)
        if self.size == 1: 
            assert self.decision_level[0] == -1
            self.refA = self.clause[0]
            self.refB = self.refA
        
        else: #self.size > 1
            if self.refA is None : 
                self.refA, self.refB = random.sample(self.clause[:self.size],2)
            else: 
                # self.print_info()
                pool_refs = self.clause[:self.size]
                A_ok, B_ok = False, False
                if self.refA in pool_refs: # keep refA
                    pool_refs.remove(self.refA)
                    A_ok = True
                if self.refB in pool_refs: # keep refB
                    pool_refs.remove(self.refB)
                    B_ok = True
                # print(pool_refs, self.refA, self.refB)
                if not A_ok:
                    assert len(pool_refs) > 0 
                    self.refA = random.choice(pool_refs)
                    pool_refs.remove(self.refA)
                    A_ok = True
                if not B_ok:
                    assert len(pool_refs) > 0 
                    self.refB = random.choice(pool_refs)
                    pool_refs.remove(self.refB)
                    B_ok = True
                
                assert A_ok and B_ok
            
        self.indexA = self.clause.index(self.refA)
        self.indexB = self.clause.index(self.refB)
       
        # # self.print_info()
        # if refA : #pick new refA
        #     # assert self.decision_level[self.indexA] != -1
        #     if self.size == 1:
        #         self.refA = self.clause[0]
        #         self.indexA = 0
        #     else: 
        #         # print(self.indexA, self.refB)
        #         if self.refA is None or self.decision_level[self.indexA] != -1:
        #             for i in range(self.size):
        #                 if self.clause[i] != self.refB:
        #                     assert self.decision_level[i] == -1
        #                     self.refA  = self.clause[i]
        #                     self.indexA = i
            
        # if refB: #pick new refB
        #     # assert self.decision_level[self.indexB] != -1
        #     if self.size == 1:
        #         self.refB = self.clause[0]
        #         self.indexB = 0
        #     else: 
        #         # print(self.indexB)
        #         if self.refB is None or self.decision_level[self.indexB] != -1:
        #             for i in range(self.size):
        #                 if self.clause[i] != self.refA:
        #                     assert self.decision_level[i] == -1
        #                     self.refB  = self.clause[i]
        #                     self.indexB = i

        # self.indexA = self.clause.index(self.refA)
        # self.indexB = self.clause.index(self.refB)

        # self.print_info()
        assert self.decision_level[self.indexA] == -1
        assert self.decision_level[self.indexB] == -1
        if self.size > 1:
            # print('after picking')
            # self.print_info()
            assert self.refA != self.refB

    def remove_refs(self):
        self.refA, self.refB = None, None
        self.indexA, self.indexB = None, None

    def bcp(self, literal, decision_level, graph):
        assert self.size >= 0
        assert self.size == self.decision_level.count(-1)
        # Lazy clause is visited only when Var(litteral) is Var(refA) or Var(refB)
        # Case 1: size == 0, all literals are assigned ! check its value
        if self.size == 0: 
            assert self.value != 0
            assert self.refA == None
            assert self.refB == None

        # Case 2: If clause is unit
        elif self.size == 1:
            assert self.refA != None
            assert self.refA == self.refB
            assert self.indexA == self.indexB 
            assert self.decision_level[self.indexA] == -1
            assert self.value == 0
            assert decision_level >= max(self.decision_level)
            for l in self.clause[self.size:]:
                # if -l not in graph.assigned_vars:
                #     self.print_info()
                #     print("", l)
                assert -l in graph.assigned_vars 

            if literal == self.refA: #SAT
                self.decision_level[self.indexA] = decision_level
                self.size = 0
                self.value = 1
                self.remove_refs()
            elif -literal == self.refA: #UNSAT
                self.decision_level[self.indexA] = decision_level
                self.size = 0 
                self.value = -1
                self.remove_refs()
            else:
                pass

        # Case 3: clause is not unit => we need to bcp
        elif self.size > 1:
            # self.print_info()
            assert self.refA != None
            assert self.refB != None
            assert self.refA != self.refB
            assert self.value == 0
            assert self.decision_level[self.indexA] == -1
            assert self.decision_level[self.indexB] == -1
            # if decision_level < max(self.decision_level):
            #     print(decision_level, max(self.decision_level))
            #     self.print_info()
            assert decision_level >= max(self.decision_level)
            if literal == self.refA or literal == self.refB: #SAT
                # Assume that every unassigned literal is assigned at this level
                # thanks to the BCP of litteral at this level
                # self.decision_level[:self.size] = [decision_level for _ in range(self.size)]
                # self.value = 1 
                # self.size = 0
                # self.remove_refs()
                self.check_n_update(graph)
            elif -literal == self.refA or -literal == self.refB: #CHECK CLAUSE
                # check and update other literals 
                # if there is one true -> SAT
                # print('Check at lvl ', decision_level)
                self.check_n_update(graph)
                # print('After check')
                # self.print_info()
                # else, clause is not resolved yet, update selected literal and replace references
                # if self.value == 0:
                #     self.print_info()
                #     assert self.size > 1
                    # Case 3.1: refA is False, replace refA
                    # if -literal == self.refA:
                    #     self.clause[self.indexA] = self.clause[self.size-1]
                    #     self.clause[self.size-1] = self.refA
                    #     self.indexA = self.size-1
                    #     self.decision_level[self.indexA] = decision_level
                    #     self.size -= 1
                    #     assert self.size > 0
                    #     self.pick_new_ref(refA=True, refB=False)
                    #     self.indexB = self.clause.index(self.refB)
                        # if self.size == 1:
                        #     self.refA = self.clause[0]
                        #     self.indexA = 0
                        #     self.refB = self.refA
                        #     self.indexB = self.indexA
                        # elif self.size > 1:
                        #     self.pick_new_ref(refA=True)
                        #     return 0
                        # else:
                        #     self.value = -1
                        #     return -1
                    # Case 3.2: refB is False, replace refB
                    # elif -literal == self.refB:
                    #     self.clause[self.indexB] = self.clause[self.size-1]
                    #     self.clause[self.size-1] = self.refB
                    #     self.indexB = self.size -1 
                    #     self.decision_level[self.indexB] = decision_level
                    #     self.size -= 1
                    #     assert self.size > 0
                    #     self.pick_new_ref(refA=False, refB=True)
                    #     self.indexA = self.clause.index(self.refA)
                        # if self.size == 1:
                        #     self.refB = self.clause[0]
                        #     self.indexB = 0
                        #     self.refA = self.refB
                        #     self.indexA = self.indexB
                        # elif self.size > 1:
                        #     self.pick_new_ref(refB=True)
                        #     return 0
                        # else: 
                        #     self.value = -1
                        #     return -1 
                    # assert self.value == 0
            else:  
                pass
        assert self.size == self.decision_level.count(-1)
        # full_clause = Clause(self.clause)
        # for i, l in enumerate(graph.assigned_vars):
        #     full_clause.bcp(l,i)
        # if self.value == 1 and full_clause.value == -1:
        #     print(self.clause, full_clause.value)
        #     print(graph.assigned_vars)
        return self.value
            

    def restore(self, level, graph):
        # print('Assignment: ', graph.graph)
        # print('Before restore at lvl ', level)
        # self.print_info()
        # print('Try to update before restore')
        self.update(graph)
        # self.print_info()
        offset = 0
        for lvl in self.decision_level:
            if lvl == -1 or lvl > level:
                offset += 1
            
        self.size = offset
        if self.size > 0:
            self.value = 0
            self.decision_level[:self.size] = [-1 for _ in range(self.size)]
            # if self.decision_level[self.indexA] >= 0:
            #     self.pick_new_ref(refA=True)
            # if self.decision_level[self.indexB] >= 0:
            #     self.pick_new_ref(refB=True)
            self.pick_new_ref()
        else:
            
            self.remove_refs()
            
        # print("After restore at lvl ", level)
        # self.print_info()
        assert self.size == self.decision_level.count(-1)
        assert max(self.decision_level) <= level
        # if self.size == 1:
        #     # print(level)
        #     # self.print_info()
        #     # for item in graph.graph.keys():
        #     #     print(item, graph.graph[item][1])
        #     for l in self.clause[self.size:]:
        #         assert -l in graph.assigned_vars 
        if self.size >= 1:
            for i,l in enumerate(self.clause):
                if i < self.size:
                    assert l not in graph.assigned_vars
                    assert -l not in graph.assigned_vars
                else:
                    assert -l in graph.assigned_vars
                    assert l not in graph.assigned_vars

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
            if (abs(l) != abs(literal)):
                if l not in res and -l not in res:
                    res.append(l)
                    dl.append(other.decision_level[i])
                elif l not in res and -l in res:
                    self.print_info()
                    print("and")
                    other.print_info()

                    res = []
                    dl = []
                    break
                elif l in res:
                    continue
        resolved_clause = Lazy_Clause(res)
        resolved_clause.set_decision_levels(dl)
        resolved_clause.size = resolved_clause.decision_level.count(-1)
        assert literal not in resolved_clause.clause
        assert -literal not in resolved_clause.clause
        return resolved_clause

    def set_decision_levels(self, decision_level):
        self.decision_level = decision_level
        self.clause = [x for _,x in sorted(zip(self.decision_level,self.clause), reverse=True)]
        self.decision_level.sort(reverse=True)