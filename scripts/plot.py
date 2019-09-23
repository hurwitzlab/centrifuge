#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@email.arizona.edu>
Date   : 2019-06-11
Purpose: Plot Centrifuge out
"""

import argparse
import csv
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from functools import partial
from collections import defaultdict
from dire import die, warn
from typing import List, Dict, TextIO


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Plot Centrifuge out',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        nargs='+',
                        help='Centrifuge .tsv file(s)')

    parser.add_argument('-r',
                        '--rank',
                        help='Tax rank',
                        metavar='str',
                        type=str,
                        choices=('class family genus kingdom leaf'
                                 'order phylum species subspecies'
                                 'superkingdom').split(),
                        default='species')

    parser.add_argument('-m',
                        '--min',
                        help='Minimum percentage',
                        metavar='float',
                        type=float,
                        default=0.)

    parser.add_argument('-M',
                        '--multiplier',
                        help='Multiply abundance',
                        metavar='float',
                        type=float,
                        default=1.)

    parser.add_argument('-x',
                        '--exclude',
                        help='Tax IDs or names to exclude',
                        metavar='str',
                        type=str,
                        nargs='+',
                        default='')

    parser.add_argument('-t',
                        '--title',
                        help='Figure title',
                        metavar='str',
                        type=str,
                        default='')

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='str',
                        type=str,
                        default='bubble.png')

    parser.add_argument('-p',
                        '--max_plot',
                        help='Max samples to plot',
                        metavar='int',
                        type=int,
                        default=1000)

    parser.add_argument('-H',
                        '--img_height',
                        help='Image height',
                        metavar='float',
                        type=float,
                        default=0.)

    parser.add_argument('-w',
                        '--img_width',
                        help='Image width',
                        metavar='float',
                        type=float,
                        default=0.)

    parser.add_argument('-O',
                        '--show_image',
                        help='Show image',
                        action='store_true')

    args = parser.parse_args()

    if not args.title:
        args.title = '{} abundance'.format(args.rank.title() or 'Organism')

    args.exclude = list(map(str.lower, args.exclude))

    return args


# --------------------------------------------------
def parse_files(files: List[TextIO], rank_wanted: str, exclude: List[str],
                min_pct: float) -> List[dict]:
    """Parse the files"""

    below_genus = partial(re.search, '(species|leaf)')
    below_species = partial(re.search, '(subspecies|leaf)')
    is_virus = lambda name: re.search('(phage|virus)', name, re.IGNORECASE)

    assigned = {}
    for i, fh in enumerate(files, start=1):
        print('{:3}: {}'.format(i, fh.name))

        sample, _ = os.path.splitext(os.path.basename(fh.name))
        if not sample in assigned:
            assigned[sample] = {}

        reader = csv.DictReader(fh, delimiter='\t')
        for rec in reader:
            tax_name = rec['name']
            tax_rank = rec['taxRank']

            if rank_wanted == 'genus' and below_genus(tax_rank):
                tax_rank = 'genus'
                if not is_virus(tax_name):
                    tax_name = tax_name.split()[0]
            elif rank_wanted == 'species' and below_species(tax_rank):
                tax_rank = 'species'
                if not is_virus(tax_name):
                    tax_name = ' '.join(tax_name.split()[:2])

            if rank_wanted and (rank_wanted != tax_rank):
                continue

            if rec['taxID'] in exclude or tax_name.lower() in exclude:
                continue

            try:
                reads = int(rec['numUniqueReads'])
                abundance = float(rec['abundance'])
            except:
                continue

            if reads == 0:
                continue

            if not tax_name in assigned[sample]:
                assigned[sample][tax_name] = {'reads': 0, 'abundance': 0}

            assigned[sample][tax_name]['reads'] += reads
            assigned[sample][tax_name]['abundance'] += abundance

    data = []
    for sample in assigned:
        total_reads = sum([
            assigned[sample][tax_name]['reads']
            for tax_name in assigned[sample]
        ])

        if total_reads == 0:
            warn('No reads for "{}"?'.format(sample))
            continue

        for tax_name, d in assigned[sample].items():
            pct = d['reads'] / total_reads

            if min_pct and pct < min_pct:
                continue

            data.append({
                'sample': sample,
                'tax_name': tax_name,
                'pct': pct,
                'reads': d['reads'],
                'abundance': d['abundance']
            })

    return data


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    print(args)
    data = parse_files(args.file, args.rank, args.exclude, args.min)

    num_found = len(data)
    print('Found {} at min {}%'.format(num_found, args.min))

    if num_found > 0:
        df = pd.DataFrame(data)
        out_dir = os.path.dirname(os.path.abspath(args.outfile))
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        basename, _ = os.path.splitext(os.path.basename(args.outfile))
        df.to_csv(os.path.join(out_dir, basename + '.csv'), index=False)

        if num_found > args.max_plot:
            print('Too many to plot (>{})!'.format(args.max_plot))
        else:
            x = df['sample']
            y = df['tax_name']
            img_width = args.img_width or 5 + len(x.unique()) / 5
            img_height = args.img_height or len(y.unique()) / 3
            plt.figure(figsize=(img_width, img_height))
            plt.scatter(x, y, s=df['pct'] * 100, alpha=0.5)
            plt.xticks(rotation=45, ha='right')
            plt.gcf().subplots_adjust(bottom=.4, left=.4)
            plt.ylabel('Organism')
            plt.xlabel('Sample')
            if args.title:
                plt.title(args.title)

            plt.savefig(args.outfile)
            if args.show_image:
                plt.show()
        print('Done, see csv/plot in out_dir "{}"'.format(out_dir))


# --------------------------------------------------
if __name__ == '__main__':
    main()
