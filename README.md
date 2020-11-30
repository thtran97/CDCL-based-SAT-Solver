# SAT-Solving

This repo includes my implementations for solving SAT problems as well as its variants. 
The core idea is to try to implement complete and imcomplete search algos. In particular, my work focuses on CDCL, Local Search and MaxSAT. 
Besides I hope to implement also some KC techniques in this repo. 

All implementations will be coded in Python. 

Let's start ! 

- [x] Download / create some CNF instances
- [x] Read and load input data => dimacs_parser.py
- [x] Create a common SAT solver e.g. original dpll_solver.py

In next steps => try to involve the original sat solver with its known variants and additional features in order to boost the search, e.g. CDCL-solver

- Add verbose option : if verbose mode is on, let's plot "problem statistics" and "search statistics" => like minisat

    + [ ] Search statistics: https://github.com/niklasso/minisat/blob/master/minisat/core/Solver.cc#L856

    + [ ] Problem statistics: https://github.com/niklasso/minisat/blob/master/minisat/core/Main.cc#L92 


# Updates
 
- [X] Implement function "Conflict analysis"
- [X] Implement function "Backtracking"
- [X] Implement fucntion "Search"
- [X] CDCL Search
- [X] Two-watched literals
- [X] Simple restart
- [X] Simple branching heuristics 


# Analytics

Solver now can answer correctly some simple instances. But with harder instances, the computational complexity seems to be a hard challenge => try to solve this issue by update new mechanisms and simplify the code 

# TODO

- [ ] Clean and simplify code if possible
- [ ] Add complex mechanism of restart and branching heuristics 
 

