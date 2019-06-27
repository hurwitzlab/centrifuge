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
from dire import die

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
                        default='./out/bubble.png')

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
                        help='Show image', action='store_true')

    args = parser.parse_args()

    if not args.title:
        args.title = '{} abundance'.format(args.rank.title() or 'Organism')

    args.exclude = list(map(str.lower, args.exclude))

    return args

# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    rank_wanted = args.rank
    min_pct = args.min
    exclude = args.exclude
    assigned = {}

    below_genus = partial(re.search, '(species|leaf)')
    below_species = partial(re.search, '(subspecies|leaf)')
    is_virus = lambda name: re.search('(phage|virus)', name, re.IGNORECASE)

    for i, fh in enumerate(args.file, start=1):
        print('{:3}: {}'.format(i, fh.name))

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
                pct = float(rec.get('abundance'))
                reads = int(rec['numReads'])
            except:
                continue

            sample, _ = os.path.splitext(os.path.basename(fh.name))
            key = (sample, tax_name)
            if key in assigned:
                assigned[key]['pct'] += pct
                assigned[key]['reads'] += reads
            else:
                assigned[key] = {'pct': pct, 'reads': reads}

    if not assigned:
        die('No data')

    data = []
    for key, d in assigned.items():
        sample, tax_name = list(key)
        if min_pct and d['pct'] < min_pct:
            continue

        data.append({
            'sample': sample,
            'tax_name': tax_name,
            'pct': d['pct'],
            'reads': d['reads'],
        })

    num_found = len(data)
    print('Found {} at min {}%'.format(num_found, min_pct))

    df = pd.DataFrame(data)
    out_dir = os.path.dirname(os.path.abspath(args.outfile))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    basename, _ = os.path.splitext(os.path.basename(args.outfile))
    df.to_csv(os.path.join(out_dir, basename + '.csv'))

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
