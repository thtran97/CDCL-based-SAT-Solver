#!/usr/bin/env python

import numpy as np
from utils import get_args
# import dpll_solver
from cdcl_solver import CDCL_Solver


def main():
    try:
        args = get_args()
        input_cnf_file = args.input
        verbose = args.verbose
    except:
        print("missing or invalid arguments")
        exit(0)

    # dpll_solver.solve(input_cnf_file, verbose)
    solver = CDCL_Solver(input_cnf_file, verbose)
    solver.solve()

if __name__ == '__main__':
    main()