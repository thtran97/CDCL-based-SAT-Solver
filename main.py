#!/usr/bin/env python

import numpy as np
from utils.get_args import get_args
import dpll_solver

def main():
    try:
        args = get_args()
        input_cnf_file = args.input

    except:
        print("missing or invalid arguments")
        exit(0)

    dpll_solver.solve(input_cnf_file)

if __name__ == '__main__':
    main()