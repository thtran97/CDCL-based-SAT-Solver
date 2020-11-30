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
        m1, m2 = -1, -1
        for x in list(set(self.decision_level)):
            if x >= m1:
                m1, m2 = x, m1
            elif x > m2:
                m2 = x
        if m2 == -1:
            m2 = m1 - 1
        return m2

    def bcp(self, literal, decision_level, graph=None):
        if self.size > 0 and literal in self.clause:
            for i in range(self.size): 
                self.decision_level[i] = decision_level
            self.size = 0 
            self.value = 1 #TRUE
        elif self.size > 0 and -literal in self.clause:
            index = self.clause.index(-literal)
            self.clause[index] = self.clause[self.size-1]
            self.clause[self.size-1] = -literal
            self.decision_level[self.size-1] = decision_level
            self.size -= 1
            if self.size == 0:
                self.value = -1 #FALSE
        if self.size == 0: 
            assert self.value != 0
        if self.size > 0:
            assert self.value == 0
        return self.value

    def preprocess(self):
        # remove redundant literals:
        # self.clause =  list(set(self.clause))
        # if contains two opposites literals => TRUE
        for l in self.clause:
            if -l in self.clause:
                self.value = 1 #TRUE
                self.size = 0
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
