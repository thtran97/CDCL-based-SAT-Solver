import argparse

def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-i', '--input',
        metavar='I',
        default='cnf_instances/test.cnf',
        help='The DIMACS file')
    args = argparser.parse_args()
    return args