#!/usr/bin/env python3
"""Run Centrifuge/bubble plot"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from itertools import chain
from typing import Dict, List, Optional
from dataclasses import dataclass
import parallelprocs
from shutil import which


@dataclass
class Args:
    """Command-line args"""

    query: List[str]
    format: str
    index: str
    index_dir: str
    out_dir: str
    exclude_tax_ids: List[int]
    figure_title: str
    num_threads: int
    num_procs: int
    min_proportion: float
    verbose: bool
    reads_not_paired: bool
    num_halt: int


# --------------------------------------------------
def get_args() -> Args:
    """Get command-line args"""

    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-q',
                        '--query',
                        help='File or directory of input',
                        metavar='str',
                        type=str,
                        nargs='+',
                        required=True)

    parser.add_argument('-f',
                        '--format',
                        help='Input file format',
                        metavar='str',
                        type=str,
                        choices=['fasta', 'fastq'],
                        default='')

    parser.add_argument('-i',
                        '--index',
                        help='Centrifuge index name',
                        metavar='str',
                        type=str,
                        default='p_compressed+h+v')

    parser.add_argument('-I',
                        '--index_dir',
                        help='Centrifuge index directory',
                        metavar='str',
                        type=str,
                        required=True)

    parser.add_argument('-o',
                        '--out_dir',
                        help='Output directory',
                        metavar='str',
                        type=str,
                        default=os.path.join(os.getcwd(), 'centrifuge-out'))

    parser.add_argument('-x',
                        '--exclude_tax_ids',
                        help='Comma-separated list of tax ids to exclude',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-T',
                        '--figure_title',
                        help='Title for the bubble chart',
                        metavar='str',
                        type=str,
                        default='Species abundance by sample')

    parser.add_argument('-t',
                        '--threads',
                        help='Num of threads per instance of centrifuge',
                        metavar='int',
                        type=int,
                        default=1)

    parser.add_argument('-P',
                        '--procs',
                        help='Max number of processes to run',
                        metavar='int',
                        type=int,
                        default=4)

    parser.add_argument('-H',
                        '--num_halt',
                        help='Halt after this many failing jobs',
                        metavar='int',
                        type=int,
                        default=0)

    parser.add_argument('-m',
                        '--min_proportion',
                        help='Minimum proportion to show',
                        metavar='float',
                        type=float,
                        default=0.02)

    parser.add_argument('-u',
                        '--reads_not_paired',
                        help='Do not try to pair the reads',
                        action='store_true')

    parser.add_argument('-v',
                        '--verbose',
                        help='Verbose logging',
                        action='store_true')

    args = parser.parse_args()

    if not os.path.isdir(args.index_dir):
        parser.error(f'--index_dir "{args.index_dir}" is not a directory')

    valid_index = set(
        map(lambda s: re.sub(r'\.\d+\.cf$', '', os.path.basename(s)),
            os.listdir(args.index_dir)))

    if args.index not in valid_index:
        tmpl = '--index "{}" is not valid, please choose from: {}'
        parser.error(tmpl.format(args.index, ', '.join(sorted(valid_index))))

    exclude_ids = list(
        map(
            int,
            filter(
                str.isnumeric,
                chain(*map(str.split, re.split(r'\s*,\s*',
                                               args.exclude_tax_ids))))))

    return Args(query=args.query,
                format=args.format,
                index=args.index,
                index_dir=args.index_dir,
                out_dir=args.out_dir,
                exclude_tax_ids=exclude_ids,
                figure_title=args.figure_title,
                num_threads=args.threads,
                num_procs=args.procs,
                min_proportion=args.min_proportion,
                verbose=args.verbose,
                reads_not_paired=args.reads_not_paired,
                num_halt=args.num_halt)


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    logging.basicConfig(
        filename='.log',
        filemode='w',
        level=logging.DEBUG if args.verbose else logging.CRITICAL)

    files = group_input_files(check_sra(find_input_files(args.query)),
                              args.reads_not_paired)

    logging.debug(
        'Files found: forward = "%s", reverse = "%s", unpaired = "%s"',
        len(files['forward']), len(files['reverse']), len(files['unpaired']))

    reports_dir = run_centrifuge(files, args)
    fig_dir = make_bubble(reports_dir, args)

    print(f'Done, reports in "{reports_dir}", figures in "{fig_dir}"')


# --------------------------------------------------
def find_input_files(query: List[str]) -> List[str]:
    """Find input files from list of files/dirs"""

    files: List[str] = []
    for qry in query:
        if os.path.isdir(qry):
            for root, _, filenames in os.walk(qry):
                files.extend(map(lambda f: os.path.join(root, f), filenames))
        elif os.path.isfile(qry):
            files.append(qry)

    return sorted(files)


# --------------------------------------------------
def group_input_files(files: List[str],
                      reads_not_paired: bool = False) -> Dict[str, List[str]]:
    """Group into paired (forward/reverse) and unpaired"""

    ret: Dict[str, List[str]] = defaultdict(list)

    if reads_not_paired:
        ret['unpaired'] = files
    else:
        rm_dot = lambda s: re.sub(r'^[.]', '', s)
        extensions = map(rm_dot, set(map(get_extension, files)))
        re_tmpl = r'(.+)[_-][Rr]?{}\.(?:' + '|'.join(extensions) + ')$'
        forward_re = re.compile(re_tmpl.format('1'))
        reverse_re = re.compile(re_tmpl.format('2'))

        forward: Dict[str, str] = defaultdict(str)
        reverse: Dict[str, str] = defaultdict(str)

        for file in files:
            basename = os.path.basename(file)
            forward_match = forward_re.search(basename)
            reverse_match = reverse_re.search(basename)

            if forward_match:
                forward[forward_match.group(1)] = file
            elif reverse_match:
                reverse[reverse_match.group(1)] = file
            else:
                ret['unpaired'].append(file)

        for root in forward:
            if root in reverse:
                ret['forward'].append(forward[root])
                ret['reverse'].append(reverse[root])
            else:
                ret['unpaired'].append(forward[root])

    return ret


# --------------------------------------------------
def run_centrifuge(files: Dict[str, List[str]], args: Args) -> str:
    """Run Centrifuge"""

    reports_dir = os.path.join(args.out_dir, 'reports')
    if not os.path.isdir(reports_dir):
        os.makedirs(reports_dir)

    exclude_arg = '--exclude-taxids ' + ','.join(map(
        str, args.exclude_tax_ids)) if args.exclude_tax_ids else ''

    file_format = args.format or get_file_formats(list(chain(*files.values())))
    if not file_format:
        raise Exception(
            'Cannot guess file format from file extentions, please specify.')

    format_arg = '-f' if file_format == 'fasta' else ''

    cmd_tmpl = 'CENTRIFUGE_INDEXES={} centrifuge {} {} -p {} -x {} '
    cmd_base = cmd_tmpl.format(args.index_dir, exclude_arg, format_arg,
                               args.num_threads, args.index)

    commands = []
    for file in files['unpaired']:
        basename = os.path.basename(file)
        tsv_file = os.path.join(reports_dir, basename + '.tsv')
        sum_file = os.path.join(reports_dir, basename + '.sum')
        if not os.path.isfile(tsv_file):
            commands.append(
                cmd_base +
                f'-U "{file}" -S "{sum_file}" --report-file "{tsv_file}"')

    for i, file in enumerate(files['forward']):
        basename = os.path.basename(file)
        tsv_file = os.path.join(reports_dir, basename + '.tsv')
        sum_file = os.path.join(reports_dir, basename + '.sum')
        if not os.path.isfile(tsv_file):
            forward, reverse = files['reverse'][i]
            commands.append(cmd_base + f'-1 "{forward}" -2 "{reverse}" ' +
                            f'-S "{sum_file}" --report-file "{tsv_file}"')

    logging.debug('Running Centrifuge')
    logging.debug('\n'.join(commands))
    parallelprocs.run(commands,
                      msg='Running Centrifuge',
                      num_procs=args.num_procs,
                      verbose=args.verbose,
                      halt=args.num_halt)

    return reports_dir


# --------------------------------------------------
def make_bubble(reports_dir: str, args: Args) -> str:
    """Make bubble chart"""

    fig_dir = os.path.join(args.out_dir, 'figures')
    if not os.path.isdir(fig_dir):
        os.makedirs(fig_dir)

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    bubble = os.path.join(cur_dir, 'plot.py')

    if not os.path.isfile(bubble):
        raise Exception(f'Cannot find "{bubble}"')

    tmpl = '{} --title "{}" --outfile "{}" --min {} {}/*.tsv'
    job = tmpl.format(bubble, args.figure_title,
                      os.path.join(fig_dir, 'bubble.png'), args.min_proportion,
                      reports_dir)
    logging.debug('Running %s', job)

    subprocess.run(job, shell=True)

    return fig_dir


# --------------------------------------------------
def get_extension(file: str) -> str:
    """Return file extension"""

    return os.path.splitext(file)[1]


# --------------------------------------------------
def guess_file_format(ext: str) -> str:
    """Guess a single file's format from the extension"""

    if ext.startswith('.'):
        ext = ext[1:]

    return 'fasta' if re.search(
        r'^f(?:ast|n)?a$',
        ext) else 'fastq' if re.search(r'^f(?:ast)?q$', ext) else ext


# --------------------------------------------------
def get_file_formats(files: List[str]) -> Optional[str]:
    """Guess one format for all the files"""

    exts = set(map(guess_file_format, map(get_extension, files)))
    return exts.pop() if len(exts) == 1 else None


# --------------------------------------------------
def check_sra(files: List[str]) -> List[str]:
    """Unpack FASTA from any SRA files"""

    fastq_dump = which('fastq-dump')
    if not fastq_dump:
        raise Exception('Cannot find "fastq-dump"')

    tmpl = fastq_dump + ' --fasta --split-files -O {} {}'
    new_files = []

    for file in files:
        _, ext = os.path.splitext(file)
        if ext == '.sra':
            logging.debug('Extracting SRA file "%s"', os.path.basename(file))
            srcdir = os.path.dirname(file)
            tmpdir = tempfile.TemporaryDirectory()
            subprocess.run(tmpl.format(tmpdir.name, file), shell=True)

            for fasta in filter(lambda f: re.search('.f(?:ast|n)?a', f),
                                os.listdir(tmpdir.name)):
                new = os.path.join(srcdir, fasta)
                shutil.move(os.path.join(tmpdir.name, fasta), new)
                new_files.append(new)

            tmpdir.cleanup()
        else:
            new_files.append(file)

    return new_files


# --------------------------------------------------
if __name__ == '__main__':
    main()
