import random 

class Lazy_Clause:
    
    def __init__(self, list_literal):
        assert len(list_literal) > 0
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
        # print('[C] Refs: ', self.refA, self.refB)
        # print('[C] Index: ', self.indexA, self.indexB)
        # print('[C] Truth value: ', self.value)
        # print('[C] Full clause ', self.clause)
        # print('[C] Details on decision_level: ', self.decision_level)

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
        assigned_vars = graph.assigned_vars
        sat_dl = []
        for i in range(len(self.clause)):
            # If there is one true literal in list of assigned variables => SAT 
            if self.clause[i] in assigned_vars:
                self.decision_level[i] = graph.graph[self.clause[i]][1]
                sat_dl.append(graph.graph[self.clause[i]][1])
            # Else if the literal is false, update info
            elif -self.clause[i] in assigned_vars and self.decision_level[i] == -1:
                self.decision_level[i] = graph.graph[-self.clause[i]][1]
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
            self.clause = self.clause[-self.size:] + self.clause[:-self.size]
            self.decision_level = self.decision_level[-self.size:] + self.decision_level[:-self.size]
            ## After moving too many times, indexes and refs are also changes
            ## Update them !
            self.indexA = self.clause.index(self.refA)
            self.indexB = self.clause.index(self.refB)
            self.pick_new_ref()
            assert self.value == 0
            # if self.size == 1:
            #     for l in self.clause[self.size:]:
            #         assert -l in assigned_vars 
        else:
            if self.value != 1:
                self.value = -1
                self.remove_refs()
        # assert self.size == self.decision_level.count(-1)

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

        assert self.decision_level[self.indexA] == -1
        assert self.decision_level[self.indexB] == -1
        if self.size > 1:
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
            # for l in self.clause[self.size:]:
            #     assert -l in graph.assigned_vars 

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

            assert decision_level >= max(self.decision_level)
            if literal == self.refA or literal == self.refB: #SAT => Check
                self.check_n_update(graph)
            elif -literal == self.refA or -literal == self.refB: #Check 
                self.check_n_update(graph) 
            else:  
                pass
        assert self.size == self.decision_level.count(-1)

        return self.value
            

    def restore(self, level, graph):
        self.update(graph)
        offset = 0
        for lvl in self.decision_level:
            if lvl == -1 or lvl > level:
                offset += 1
            
        self.size = offset
        if self.size > 0:
            self.value = 0
            self.decision_level[:self.size] = [-1 for _ in range(self.size)]
            self.pick_new_ref()
        else:
            
            self.remove_refs()

        assert self.size == self.decision_level.count(-1)
        assert max(self.decision_level) <= level
        # if self.size >= 1:
        #     for i,l in enumerate(self.clause):
        #         if i < self.size:
        #             assert l not in graph.assigned_vars
        #             assert -l not in graph.assigned_vars
        #         else:
        #             assert -l in graph.assigned_vars
        #             assert l not in graph.assigned_vars

    def literal_at_level(self, lvl):
        res = []
        for i in range(len(self.clause)):
            if self.decision_level[i] == lvl:
                res.append(self.clause[i])
        return res

    def get_backtrack_level(self):
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