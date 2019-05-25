# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 18:14:07 2018

@author: Georgios
"""

import argparse
import pandas as pd
import numpy as np
import os
import sys
from auxiliary.io_json import read_json
from auxiliary.fuzzy_fix_names import fuzzy_fix_names
import win_unicode_console
win_unicode_console.enable()


def main(day):
    '''To DO:
        1) Insert simple models for benchmarking
    '''

    if day < 1:
        sys.exit('Round must be non-negative integer')

    config_file = 'config/config.json'
    configs = read_json(config_file)
    out_dir = configs['output_directory']
    fuzzy_thr = configs['fuzzy_threshold']

    table_file = os.path.join(out_dir, 'table_day_%d.csv' % (day-1))
    scores_file = os.path.join(out_dir, 'predictions_day_%d.csv' % day)
    out_file = os.path.join(out_dir, 'table_day_%d.csv' % day)

    scores = pd.read_csv(scores_file)
    if day == 1:
        # set initial table, all players have zero points, mvps, etc.
        table = pd.DataFrame(np.arange(1, scores.shape[0]+1, dtype=int),
                             columns=['Position'])
        table['Name'] = scores['Name'].values
        table['MVP'] = np.zeros((scores.shape[0], 1), dtype=int)
        table['Points'] = np.zeros((scores.shape[0], 1), dtype=int)
        table['Missed Rounds'] = np.zeros((scores.shape[0], 1), dtype=int)
    else:
        # read the table of the previous round
        table = pd.read_csv(table_file)

        # fix usernames via fuzzy search
        new_names = fuzzy_fix_names(scores['Name'].values,
                                    table['Name'].values,
                                    threshold=fuzzy_thr)
        scores['Name'] = new_names

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
        df_new.loc[jj, 'Missed Rounds'] = day - 1
        for name in df_new['Name'][jj].values:
            print('%s is a new player' % name)

    # did not play this round
    ii = np.isnan(df_merged['Score'])
    dnp = []
    if any(ii):
        df_new.loc[ii, 'Score'] = min_score
        df_new.loc[ii, 'Missed Rounds'] += 1
        for name in df_new['Name'][ii].values:
            dnp.append(name)
            print('Warning (DNP): %s did not play this round' % name)

    # check if user has missed more than four rounds.
    mm = df_new['Missed Rounds'] >= 4
    disq = []
    if any(mm):
        for name in df_new['Name'][mm].values:
            print('Warning (DIS): User %s has missed four rounds and is being '
                  'disqualified' % name)
            df_new.drop(df_new[df_new['Name'] == name].index, inplace=True)
            disq.append(name)

    # update points
    df_new['Points'] += df_new['Score'].astype(int)
    # update MVP
    df_new.loc[df_new['Score'] == mvp_score, 'MVP'] += 1
    # convert colums to int type.
    df_new[['MVP', 'Points', 'Missed Rounds']] = df_new[
        ['MVP', 'Points', 'Missed Rounds']].astype(int)

    new_table = df_new[['Name', 'MVP', 'Points', 'Missed Rounds']].copy()
    # sort by points (desc), then by MVP (desc) and finally by name (asc)
    new_table = new_table.sort_values(by=['Points', 'MVP', 'Name'],
                                      ascending=[False, False, True])
    new_table.insert(0, 'Position',
                     np.arange(1, new_table.shape[0] + 1, dtype=int))

    print(new_table)

    np.savez(os.path.join(out_dir, 'dnp'), dnp=dnp, disq=disq)

    new_table.to_csv(out_file, index=False)

    return new_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--day', type=int,
                        help='the day (round) of the regular season')
    args = parser.parse_args()
    if args.day is None:
        parser.print_help()
    else:
        main(args.day)
