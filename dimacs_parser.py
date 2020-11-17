
'''
	DIMAC parser:  read CNF file and save in a list 
    Reference: https://github.com/marcmelis/dpll-sat/blob/master/solvers/original_dpll.py 
'''

def parse(filename):
    clauses = []
    for line in open(filename):
        if line.startswith('c'): continue
        if line.startswith('p'):
            nvars, nclauses = line.split()[2:4]
            print("Nb of variables: ", nvars)
            print("Nb of clauses: ", nclauses)
            continue
        clause = [int(x) for x in line[:-2].split()]
        clauses.append(clause)
    return clauses, int(nvars)

# # Unit test 
# cnf, maxvar = parse("cnf_instances/test.cnf")
# print(cnf, maxvar)
