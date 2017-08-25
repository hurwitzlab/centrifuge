#!/usr/bin/env python3

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

import argparse
import os
from Bio import SeqIO

def main():
    args    = get_args()
    fasta   = args.fasta
    out_dir = args.out_dir
    max_per = args.num

    if not os.path.isfile(fasta):
        print('--fasta "{}" is not valid'.format(fasta))
        exit(1)

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    if max_per < 1:
        print("--num cannot be less than one")
        exit(1)

    i     = 0
    nseq  = 0
    nfile = 0
    fh    = None
    basename, ext = os.path.splitext(os.path.basename(fasta))

    for record in SeqIO.parse(fasta, "fasta"):
        if i == max_per:
            i = 0
            if fh is not None:
                fh.close()
                fh = None

        i += 1
        nseq += 1
        if fh is None:
            nfile += 1
            path = os.path.join(out_dir, basename + '.' + str(nfile) + ext)
            fh = open(path, 'wt')

        SeqIO.write(record, fh, "fasta")

    print('Done, wrote {} sequence{} to {} file{}'.format(
        nseq, '' if nseq == 1 else 's',
        nfile, '' if nfile == 1 else 's'))

def get_args():
    parser = argparse.ArgumentParser(description='Split FASTA files')
    parser.add_argument('-f', '--fasta', help='FASTA input file',
        type=str, metavar='FILE', required=True)
    parser.add_argument('-n', '--num', help='Number of records per file',
        type=int, metavar='NUM', default=50)
    parser.add_argument('-o', '--out_dir', help='Output directory',
        type=str, metavar='DIR', default='fasplit')
    return parser.parse_args()

if __name__ == '__main__':
    main()
