#!/usr/bin/env python3

"""unsplit centrifuge output"""

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

import argparse
import re
import os

# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    fasta_dir = args.fasta_dir
    reports_dir = args.reports_dir
    out_dir = args.out_dir

    if not os.path.isdir(fasta_dir):
        print('--fasta_dir "{}" is not valid'.format(fasta_dir))
        exit(1)

    if not os.path.isdir(reports_dir):
        print('--reports_dir "{}" is not valid'.format(reports_dir))
        exit(1)

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    fasta_files = os.listdir(fasta_dir)
    if len(fasta_files) < 1:
        print('Found no files in --fasta_dir {}'.format(fasta_dir))
        exit(1)

    split_files = os.listdir(reports_dir)
    if len(split_files) < 1:
        print('Found no files in --reports_dir {}'.format(reports_dir))
        exit(1)

    for i, fasta in enumerate(fasta_files):
        print('{}: {}'.format(i + 1, fasta))
        basename, ext = os.path.splitext(os.path.basename(fasta))
        splits = sorted([f for f in split_files if re.match(basename, f)])

        for file_type in ['.tsv', '.sum']:
            files = [f for f in splits if f.endswith(file_type)]
            if len(files) < 1:
                print('WARNING: No files ending with "{}" for "{}"',
                      file_type, fasta)
            else:
                out_path = os.path.join(out_dir, fasta + file_type)
                print('  Writing to "{}"'.format(out_path))
                out_fh = open(out_path, 'w')
                for fnum, file in enumerate(files):
                    print('  {}: {}'.format(fnum + 1, file))
                    in_fh = open(os.path.join(reports_dir, file))
                    hdr = in_fh.readline()
                    if fnum == 0:
                        out_fh.write(hdr)

                    for line in in_fh:
                        out_fh.write(line)


    print('Done, see output dir "{}"'.format(out_dir))

# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(description='Split FASTA files')
    parser.add_argument('-f', '--fasta_dir', help='FASTA dir',
                        type=str, metavar='STR', required=True)
    parser.add_argument('-r', '--reports_dir', help='Centrifuge reports dir',
                        type=str, metavar='STR', required=True)
    parser.add_argument('-o', '--out_dir', help='Output directory',
                        type=str, metavar='DIR', required=True)
    return parser.parse_args()

# --------------------------------------------------
if __name__ == '__main__':
    main()
