#!/usr/bin/env python3
"""split FASTA/Q files"""

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

import argparse
import os
import sys
import gzip
from Bio import SeqIO

# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(
        description="Split FASTA files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--infile',
                        help='Input file',
                        type=str,
                        metavar='FILE',
                        required=True)

    parser.add_argument('-f', '--input_format',
                        help='Input format (fasta, fastq)',
                        type=str,
                        metavar='FILE',
                        default='fasta')

    parser.add_argument('-F', '--output_format',
                        help='Output format (same as input)',
                        type=str,
                        metavar='FILE',
                        default='')

    parser.add_argument('-n', '--num',
                        help='Number of records per file',
                        type=int,
                        metavar='NUM',
                        default=100_000)

    parser.add_argument('-o', '--out_dir',
                        help='Output directory',
                        type=str,
                        metavar='DIR',
                        default='split-files')

    return parser.parse_args()

# --------------------------------------------------
def warn(msg):
    print(msg, file=sys.stderr)

# --------------------------------------------------
def die(msg):
    warn(msg)
    sys.exit(1)

# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    infile = args.infile
    input_format = args.input_format.lower()
    output_format = args.output_format.lower()
    out_dir = args.out_dir
    max_per = args.num

    if not os.path.isfile(infile):
        die('--infile "{}" is not valid'.format(infile))

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    if max_per < 1:
        die("--num cannot be less than one")

    valid_format = set(['fasta', 'fastq'])
    if not input_format in valid_format:
        die('--input_format ({}) must be in {}'.format(input_format,
                                                       ', '.join(valid_format)))

    if not output_format:
        output_format = input_format

    if not output_format in valid_format:
        die('--output_format ({}) must be in {}'.format(output_format,
                                                        ', '.join(valid_format)))

    i = 0
    nseq = 0
    nfile = 0
    basename, ext = os.path.splitext(os.path.basename(infile))

    handle = None
    if ext == ".gz":
        handle = gzip.open(infile, "rt")
        basename, ext = os.path.splitext(basename)
    else:
        handle = open(infile, "rt")

    out_fh = None
    for record in SeqIO.parse(handle, input_format):
        if i == max_per:
            i = 0
            if out_fh is not None:
                out_fh.close()
                out_fh = None

        i += 1
        nseq += 1
        if out_fh is None:
            nfile += 1
            path = os.path.join(out_dir, basename + '.' + str(nfile) + ext)
            out_fh = open(path, 'wt')

        SeqIO.write(record, out_fh, output_format)

    if out_fh is not None:
        out_fh.close()

    print('Done, wrote {} sequence{} to {} file{} in "{}"'.format(
        nseq, '' if nseq == 1 else 's',
        nfile, '' if nfile == 1 else 's',
        out_dir))

# --------------------------------------------------
if __name__ == '__main__':
    main()
