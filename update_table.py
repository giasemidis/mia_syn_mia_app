# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 18:14:07 2018

@author: Georgios
"""

import argparse
import pandas as pd
import numpy as np
from auxiliary.io_json import read_json
import win_unicode_console
win_unicode_console.enable()


def main(table_file, scores_file, out_file):
    '''To DO:
        1) Insert simple models for benchmarking
    '''

    table = pd.read_csv(table_file)
#    scores = read_json(scores_file)
    scores = pd.read_csv(scores_file)
    
    # check if there is a new user, give the lowest score.
    min_points = np.min(table.Points.values)
    
    # find mvp score of the round
    mvp_score = np.nanmax(scores['Score'].values)
    
    # find min score of the round
    min_score = np.nanmin(scores['Score'].values)
    
    # merge datasets
    df_merged = table.merge(scores, how='outer', 
                            left_on='Name', right_on='Name')
    df_new = df_merged.copy()

    # new players
    jj = np.isnan(df_merged['Points'])
    if any(jj):
        df_new.loc[jj, 'Points'] = min_points
        df_new.loc[jj, 'MVP'] = 0
        df_new.loc[jj, 'Missed Rounds'] = 0        
        for name in df_new['Name'][jj].values:
            print('%s is a new player' % name)

    # did not play this round
    ii = np.isnan(df_merged['Score'])
    if any(ii):
        df_new.loc[ii, 'Score'] = min_score
        df_new.loc[ii, 'Missed Rounds'] += 1
        for name in df_new['Name'][ii].values:
            print('Warning: %s did not play this round' % name)

    # check if user has missed more than four rounds.
    mm = df_new['Missed Rounds'] >= 4
    if any(mm):
        for name in df_new['Name'][mm].values:
            print('Warning: User %s has missed four rounds' % name)
        
    # update points
    df_new['Points'] += df_new['Score'].astype(int)
    # update MVP
    df_new.loc[df_new['Score']==mvp_score, 'MVP'] += 1
    # convert colums to int type.
    df_new[['MVP', 'Points', 'Missed Rounds']] = df_new[['MVP', 'Points', 'Missed Rounds']].astype(int)
    
    new_table = df_new[['Name', 'MVP', 'Points', 'Missed Rounds']].copy()
    # sort by points (desc), then by MVP (desc) and finally by name (asc)
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