#!/usr/bin/env python3

"""unsplit centrifuge output"""

# Author: Ken Youens-Clark <kyclark@email.arizona.edu>

import argparse
import csv
import os
import re
import sys

# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(description='Split FASTA files')
    parser.add_argument('-f', '--fasta_dir', help='FASTA dir',
                        type=str, metavar='STR')
    parser.add_argument('-l', '--file_list', help='File listing the input files',
                        type=str, metavar='STR')
    parser.add_argument('-r', '--reports_dir', help='Centrifuge reports dir',
                        type=str, metavar='STR', required=True)
    parser.add_argument('-o', '--out_dir', help='Output directory',
                        type=str, metavar='DIR', 
                        default=os.path.join(os.getcwd(), 'collapsed'))
    return parser.parse_args()

# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    fasta_dir = args.fasta_dir
    file_list = args.file_list
    reports_dir = args.reports_dir
    out_dir = args.out_dir

    if not fasta_dir and not file_list:
        print('--fasta_dir or --file_list is required')
        sys.exit(1)

    if fasta_dir and not os.path.isdir(fasta_dir):
        print('--fasta_dir "{}" is not a directory'.format(fasta_dir))
        sys.exit(1)

    if file_list and not os.path.isfile(file_list):
        print('--file_list "{}" is not a file'.format(file_list))
        sys.exit(1)

    if not os.path.isdir(reports_dir):
        print('--reports_dir "{}" is not a directory'.format(reports_dir))
        sys.exit(1)

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    fasta_files = []
    if fasta_dir:
        for root, _, filenames in os.walk(fasta_dir):
            for filename in filenames:
                fasta_files.append(os.path.join(root, filename))
        if len(fasta_files) < 1:
            print('Found no files in --fasta_dir {}'.format(fasta_dir))
            sys.exit(1)
    else:
        for file in open(file_list).read().splitlines():
            if os.path.isfile(file):
                fasta_files.append(file)

        if len(fasta_files) < 1:
            print('Found no files in --file_list {}'.format(file_list))
            sys.exit(1)


    split_files = os.listdir(reports_dir)
    if len(split_files) < 1:
        print('Found no files in --reports_dir {}'.format(reports_dir))
        sys.exit(1)

    for i, fasta in enumerate(fasta_files):
        basename = os.path.basename(fasta)
        print('{:4}: {}'.format(i + 1, basename))
        basename, ext = os.path.splitext(os.path.basename(fasta))
        splits = {'tsv': [], 'sum': []}
        for split in split_files:
            regex = r'({})\.(\d+)\.({})\.(tsv|sum)'.format(basename, ext[1:])
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
                msg = 'WARNING: No files ending with "{}" for "{}"'
                print(msg.format(file_type, basename))
            else:
                out_path = os.path.join(out_dir, basename + '.' + file_type)
                if os.path.isfile(out_path):
                    print('      "{}" exists, skipping'.format(out_path))
                else:
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
if __name__ == '__main__':
    main()
