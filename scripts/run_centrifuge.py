#!/usr/bin/env python3
"""Run Centrifuge"""

import argparse
import csv
import glob
import os
import re
import subprocess
import sys
import tempfile as tmp

# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-q', '--query',
                        help='File or directory of input',
                        metavar='str',
                        type=str,
                        nargs='+',
                        required=True)

    parser.add_argument('-r', '--reads_are_paired',
                        help='Expect forward/reverse (1/2) reads in --query',
                        action='store_true')

    parser.add_argument('-f', '--format',
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
                        help='Comma-separated list of tax ids to exclude',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-X', '--max_seqs_per_file',
                        help='Maxium num of sequences per file for split',
                        metavar='int',
                        type=int,
                        default=0)

    parser.add_argument('-t', '--threads',
                        help='Num of threads per instance of centrifuge',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-P', '--procs',
                        help='Max number of processes to run',
                        metavar='int',
                        type=int,
                        default=1)

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
def find_input_files(query, reads_are_paired):
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
            die('--query "{}" neither file nor directory'.format(qry))

    files.sort() # inplace

    forward = []
    reverse = []
    unpaired = []
    if reads_are_paired:
        re_tmpl = '.+[_-][Rr]?{}[_-].*'
        forward_re = re.compile(re_tmpl.format('1'))
        reverse_re = re.compile(re_tmpl.format('2'))

        for fname in files:
            if forward_re.search(fname):
                forward.append(fname)
            elif reverse_re.search(fname):
                reverse.append(fname)
            else:
                unpaired.append(fname)
    else:
        unpaired = files

    return {'forward': forward, 'reverse': reverse, 'unpaired': unpaired}

# --------------------------------------------------
def line_count(fname):
    """Count the number of lines in a file"""
    n = 0
    for _ in open(fname):
        n += 1

    return n

# --------------------------------------------------
def run_job_file(jobfile, msg='Running job', procs=1):
    """Run a job file if there are jobs"""
    num_jobs = line_count(jobfile)
    warn('{} (# jobs = {})'.format(msg, num_jobs))

    if num_jobs > 0:
        cmd = 'parallel --halt soon,fail=1 -P {} < {}'.format(procs, jobfile)
        warn(cmd)

        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            die('Error:\n{}\n{}\n{}\n'.format(err.output,
                                              err.stderr,
                                              err.stdout))
        finally:
            os.remove(jobfile)

    return True

# --------------------------------------------------
def split_files(out_dir, files, max_seqs, file_format, procs):
    """Split input files by max_sequences"""

    if max_seqs == 0:
        return files

    split_dir = os.path.join(out_dir, 'split')

    if not os.path.isdir(split_dir):
        os.makedirs(split_dir)

    jobfile = tmp.NamedTemporaryFile(delete=False, mode='wt')
    bin_dir = os.path.dirname(os.path.realpath(__file__))
    tmpl = '{}/fasplit.py -i {} -f {} -o {} -n {}\n'

    for input_file in files:
        out_file = os.path.join(split_dir, os.path.basename(input_file))
        if not os.path.isdir(out_file):
            jobfile.write(tmpl.format(bin_dir,
                                      input_file,
                                      file_format,
                                      out_file,
                                      max_seqs))

    jobfile.close()

    run_job_file(jobfile=jobfile.name,
                 msg='Splitting input files',
                 procs=procs)

    return list(filter(os.path.isfile,
                       glob.iglob(split_dir + '/**', recursive=True)))

# --------------------------------------------------
def run_centrifuge(**args):
    """Run Centrifuge"""

    file_format = args['file_format']
    files = args['files']
    exclude_ids = args['exclude_ids']
    index_name = args['index_name']
    index_dir = args['index_dir']
    out_dir = args['out_dir']
    threads = args['threads']
    procs = args['procs']

    reports_dir = os.path.join(out_dir, 'reports')

    if not os.path.isdir(reports_dir):
        os.makedirs(reports_dir)

    jobfile = tmp.NamedTemporaryFile(delete=False, mode='wt')
    exclude_arg = '--exclude-taxids ' + exclude_ids if exclude_ids else ''
    format_arg = '-f' if file_format == 'fasta' else ''

    cmd_tmpl = 'CENTRIFUGE_INDEXES={} centrifuge {} {} -p {} -x {} '
    cmd_base = cmd_tmpl.format(index_dir,
                               exclude_arg,
                               format_arg,
                               threads,
                               index_name)


    for file in files.unpaired:
        basename = os.path.basename(file)
        tsv_file = os.path.join(reports_dir, basename + '.tsv')
        sum_file = os.path.join(reports_dir, basename + '.sum')
        tmpl = cmd_base + '-U {} -S {} --report-file {}\n'
        if not os.path.isfile(tsv_file):
            jobfile.write(tmpl.format(file, sum_file, tsv_file))

    for i, file in files.forward:
        basename = os.path.basename(file)
        tsv_file = os.path.join(reports_dir, basename + '.tsv')
        sum_file = os.path.join(reports_dir, basename + '.sum')
        tmpl = cmd_base + '-1 {} -2 {} -S {} --report-file {}\n'
        if not os.path.isfile(tsv_file):
            jobfile.write(tmpl.format(file,
                                      files.reverse[i],
                                      sum_file,
                                      tsv_file))

    jobfile.close()

    run_job_file(jobfile=jobfile.name,
                 msg='Running Centrifuge',
                 procs=procs)

    return reports_dir

#    return list(filter(os.path.isfile,
#                       glob.iglob(reports_dir + '/**', recursive=True)))

# --------------------------------------------------
def get_excluded_tax(ids):
    """Verify the ids look like numbers"""
    tax_ids = []

    if ids:
        for s in [x.strip() for x in ids.split(',')]:
            if s.isnumeric():
                tax_ids.append(s)
            else:
                warn('tax_id "{}" is not numeric'.format(s))

    return ','.join(tax_ids)

# --------------------------------------------------
def collapse_reports(input_files, reports, out_dir):
    """Collapse the split reports"""
    collapse_dir = os.path.join(out_dir, 'collapsed')
    if not os.path.isdir(collapse_dir):
        os.makedirs(collapse_dir)

    for i, filename in enumerate(input_files):
        basename = os.path.basename(filename)
        print('{:4}: {}'.format(i + 1, basename))
        basename, ext = os.path.splitext(basename)
        splits = {'tsv': [], 'sum': []}

        for report in reports:
            regex = r'{}\.(\d+)\.{}\.(tsv|sum)'.format(basename, ext[1:])
            match = re.match(regex, os.path.basename(report))

            if match:
                num, type_ext = match.groups()
                # storing a tuple with the num first for sorting
                splits[type_ext].append((int(num), report))

        for file_type in splits:
            # sort on the fst of the tuple but take the snd
            files = [a[1] for a in \
                     sorted(splits[file_type], key=lambda a: a[0])]

            if len(files) < 1:
                msg = 'WARNING: No files ending with "{}" for "{}"'
                print(msg.format(file_type, basename))
            else:
                out_path = os.path.join(collapse_dir,
                                        basename + '.' + file_type)

                if os.path.isfile(out_path):
                    print('      "{}" exists, skipping'.format(out_path))
                else:
                    print('      Writing to "{}"'.format(out_path))
                    func = write_tsv if file_type == 'tsv' else write_sum
                    func(files, open(out_path, 'w'))


    return collapse_dir

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
                        tax[tax_id][fld] = int(row[fld]) \
                                if fld in num_flds else row[fld]
                else:
                    for fld in num_flds:
                        tax[tax_id][fld] += int(row[fld])

    # Write the headers
    flds = ['name', 'taxID', 'taxRank', 'genomeSize'] + \
            num_flds + ['abundance']
    out_fh.write("\t".join(flds) + '\n')

    total_reads = sum([tax[s]['numReads'] for s in tax])

    for tax_id in sorted(tax.keys(), key=int):
        species = tax[tax_id]

        species['abundance'] = round(species['numReads'] / total_reads, 2)

        out_fh.write('\t'.join([str(species[f]) for f in flds]) + '\n')

# --------------------------------------------------
def write_sum(files, out_fh):
    """Collapse sum files"""
    for fnum, file in enumerate(files):
        print('    {:4}: {}'.format(fnum + 1, os.path.basename(file)))
        in_fh = open(file, 'r')
        hdr = in_fh.readline()
        if fnum == 0:
            out_fh.write(hdr)

        for line in in_fh:
            out_fh.write(line)

# --------------------------------------------------
def make_bubble(reports_dir, out_dir):
    """Make bubble chart"""
    fig_dir = os.path.join(out_dir, 'figures')

    if not os.path.isdir(fig_dir):
        os.makedirs(fig_dir)

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    bubble = os.path.join(cur_dir, 'centrifuge_bubble.r')
    job = '{} --dir {} --outdir {}'.format(bubble,
                                           reports_dir,
                                           fig_dir)

    subprocess.run(job, shell=True)

    return fig_dir

# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    out_dir = args.out_dir
    index_dir = args.index_dir
    index_name = args.index

    if not index_dir:
        print('--index_dir is required')
        sys.exit(1)

    if not index_name:
        print('--index_name is required')
        sys.exit(1)

    if not os.path.isdir(index_dir):
        die('--index_dir "{}" is not a directory'.format(index_dir))

    valid_index = set(map(
        lambda s: re.sub(r'\.\d+\.cf$', '', os.path.basename(s)),
        os.listdir(index_dir)))

    if not index_name in valid_index:
        tmpl = '--index "{}" is not valid, please choose from: {}'
        die(tmpl.format(index_name, ', '.join(sorted(valid_index))))

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # returns a comma-delimited string of numerical values
    exclude_ids = get_excluded_tax(args.exclude_taxids)

    input_files = find_input_files(args.query, args.reads_are_paired)
    print(input_files)

    num_forward = len(input_files['forward'])
    num_reverse = len(input_files['reverse'])

    if num_forward and num_reverse and num_forward != num_reverse:
        msg = 'The number of forward ({}) and reverse ({}) reads do not match'
        die(msg.format(num_forward, num_reverse))

    reports_dir = run_centrifuge(file_format=args.format,
                                 files=input_files,
                                 out_dir=out_dir,
                                 exclude_ids=exclude_ids,
                                 index_dir=index_dir,
                                 index_name=index_name,
                                 threads=args.threads,
                                 procs=args.procs)

    fig_dir = make_bubble(reports_dir=reports_dir, out_dir=out_dir)
    print('Done, reports in "{}", figures in "{}"'.format(reports_dir,
                                                          fig_dir))

# --------------------------------------------------
if __name__ == '__main__':
    main()
