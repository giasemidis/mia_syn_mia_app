# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 18:14:07 2018

@author: Georgios
"""

import argparse
import pandas as pd
import numpy as np
from auxiliary.io_json import read_json


def main(table_file, scores_file, out_file):
    '''To DO:
        1) Update usernames
        2) Insert simple models for benchmarking
    '''
    # username to user id
    username_id = read_json('usernames.json')
    table = pd.read_csv(table_file)
    scores = read_json(scores_file)

    points = table.Points.values
    mvps = table.MVP.values

    mvp_score = max([scores[u] for u in scores.keys()])
    for i, name in enumerate(table.team):
        score = scores[username_id[name]]
        points[i] = points[i] + score
        if score == mvp_score:
            mvps[i] += 1

    new_table = table.copy()
    new_table['Points'] = points
    new_table['MVP'] = mvps

    new_table = table.sort(['Points', 'MVP', 'Name'], ascending=[0, 0, 1])
    new_table.insert(0, 'Position', 
                     np.arange(1, new_table.shape[0] + 1, dtype=int))

    new_table.to_csv(out_file, index=False)

    return new_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--table_file', type=str,
                        help="the id of the post")
    parser.add_argument('-s', '--scores_file', type=str,
                        help="the id of the post")
    parser.add_argument('-o', '--output', type=str,
                        help="output file to write data")
    args = parser.parse_args()
    if args.table_file is None or args.scores_file is None or args.output is None:
        parser.print_help()
    else:
        main(args.table_file, args.scores_file, args.output)