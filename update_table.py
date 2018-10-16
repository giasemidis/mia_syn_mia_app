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
        1) Insert simple models for benchmarking
    '''

    table = pd.read_csv(table_file)
    scores = read_json(scores_file)

    # check if there is a new user, give the lowest score.
    min_score = np.min(table.Points.values)
    new_users = [[0, u, 0, min_score, 0] for u in scores.keys() if u not in 
                 table.Name.values]
    if new_users:
        print('Warning: There are new players in the game.')
        for r in new_users:
            print(r[1])
        df_new = pd.DataFrame(data=new_users, columns=list(table.keys()))
    
        table = table.append(df_new, ignore_index=True)
#    print(table)
#    return

    points = table.Points.values
    mvps = table.MVP.values
    misses = table['Missed Rounds'].values

    # find mvp score
    mvp_score = max([scores[u] for u in scores.keys()])
    
    # update table
    for i, name in enumerate(table.Name.values):
        if name in scores.keys():
            score = scores[name]
            points[i] = points[i] + score
            if score == mvp_score:
                mvps[i] += 1
        else:
            misses[i] += 1
    
    # check if user has missed more than four rounds.
    mm = np.where(misses >= 4)[0]
    if mm:
        for m in mm:
            print('Warning: User %s has missed four rounds' % m)

    new_table = table[['Name', 'MVP', 'Points', 'Missed Rounds']].copy()
    new_table['MVP'] = mvps
    new_table['Points'] = points
    new_table['Missed Rounds'] = misses
    new_table = new_table.sort_values(by=['Points', 'MVP', 'Name'], 
                                      ascending=[False, False, True])
    new_table.insert(0, 'Position', 
                     np.arange(1, new_table.shape[0] + 1, dtype=int))

    print(new_table)
    
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