#!/usr/bin/env python3

"""unsplit centrifuge output"""

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

import argparse
import re
import os
import csv

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
        print('{:4}: {}'.format(i + 1, fasta))
        basename, ext = os.path.splitext(os.path.basename(fasta))
        splits = {'tsv': [], 'sum': []}
        for split in split_files:
            regex = '({})\.(\d+)\.({})\.(tsv|sum)'.format(basename, ext[1:])
            match = re.match(regex, split)
            if not match is None:
                _, num, _, type_ext = match.groups()
                if type_ext in splits:
                    # storing a tuple with the num first for sorting
                    splits[type_ext].append((int(num), os.path.join(reports_dir, split)))

        for file_type in splits:
            # sort on the fst of the tuple but take the snd
            files = [a[1] for a in sorted(splits[file_type], key=lambda a: a[0])]

            if len(files) < 1:
                print('WARNING: No files ending with "{}" for "{}"',
                      file_type, fasta)
            else:
                out_path = os.path.join(out_dir, fasta + '.' + file_type)
                print('      Writing to "{}"'.format(out_path))
                func = write_tsv if file_type == 'tsv' else write_sum
                func(files, open(out_path, 'w'))

    print('Done, see output dir "{}"'.format(out_dir))

# --------------------------------------------------
def write_tsv(files, out_fh):
    """collapse tsv files"""
    tax = dict()
    num_flds = ['numReads', 'numUniqueReads']

    for fnum, file in enumerate(files):
        print('    {:4}: {}'.format(fnum + 1, os.path.basename(file)))
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                tax_id = row['taxID']
                if not tax_id in tax:
                    tax[tax_id] = dict()
                    for fld in row.keys():
                        tax[tax_id][fld] = int(row[fld]) if fld in num_flds else row[fld]
                else:
                    for fld in num_flds:
                        tax[tax_id][fld] += int(row[fld])

    # Write the headers
    flds = ['name', 'taxID', 'taxRank', 'genomeSize'] + num_flds + ['abundance']
    out_fh.write("\t".join(flds) + '\n')

    total_reads = sum([tax[s]['numReads'] for s in tax])

    for tax_id in sorted(tax.keys(), key=int):
        species = tax[tax_id]

        species['abundance'] = round(species['numReads'] / total_reads, 2)

        out_fh.write('\t'.join([str(species[f]) for f in flds]) + '\n')

# --------------------------------------------------
def write_sum(files, out_fh):
    """collapse sum files"""
    for fnum, file in enumerate(files):
        print('    {:4}: {}'.format(fnum + 1, os.path.basename(file)))
        in_fh = open(file, 'r')
        hdr = in_fh.readline()
        if fnum == 0:
            out_fh.write(hdr)

        for line in in_fh:
            out_fh.write(line)

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
