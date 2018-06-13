#!/usr/bin/env python3
"""Run Centrifuge"""

import argparse
import os
import sys

# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('positional', metavar='str',
                        help='A positional argument')

    parser.add_argument('-q', '--query',
                        help='File or directory of input',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-t', '--format',
                        help='Input file format',
                        metavar='str',
                        type=str,
                        default='fasta')

    parser.add_argument('-i', '--index',
                        help='Centrifuge index name',
                        metavar='str',
                        type=str,
                        default='p_compressed+h+v')

    parser.add_argument('-I', '--index_dir',
                        help='Centrifuge index directory',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-o', '--out_dir',
                        help='Output directory',
                        metavar='str',
                        type=str,
                        default=os.path.join(os.getcwd(), 'centrifuge-out'))

    parser.add_argument('-x', '--exclude_taxids',
                        help='Exclude tax ids',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-f', '--flag', help='A boolean flag',
                        action='store_true')
    return parser.parse_args()

# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)

# --------------------------------------------------
def die(msg='Something went wrong'):
    """Print a message to STDERR and exit with error"""
    warn('Error: {}'.format(msg))
    sys.exit(1)

# --------------------------------------------------
def find_input_files(query):
    """Find input files from list of files/dirs"""
    files = []
    for qry in query:
        if os.path.isdir(qry):
            for filename in os.scandir(qry):
                if filename.is_file():
                    files.append(filename.path)
        elif os.path.isfile(qry):
            files.append(qry)
        else:
            warn('--query "{}" neither file nor directory'.format(qry))
    return files

# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    out_dir = args.out_dir

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    input_files = find_input_files(args.query)

# --------------------------------------------------
if __name__ == '__main__':
    main()
