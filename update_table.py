import argparse
import pandas as pd
import numpy as np
import os
import sys
import logging
from auxiliary.io_json import read_json, write_json
from auxiliary.fuzzy_fix_names import fuzzy_fix_names
from auxiliary.get_playoffs_scores import get_playoffs_scores


def main(day, sort_by_final=0):
    '''To DO:
        1) Insert simple models for benchmarking
    '''
    logging.basicConfig(level=logging.INFO)

    if day < 1:
        logging.error('Round must be non-negative integer')
        sys.exit('Exit')

    config_file = 'config/config.json'
    configs = read_json(config_file)
    out_dir = configs['output_directory']
    fuzzy_thr = configs['fuzzy_threshold']
    season = configs['season']
    #
    if ('playoff_predictions_file' in configs.keys() and
            os.path.isfile(configs['playoff_predictions_file'])):
        playoff_pred_file = configs['playoff_predictions_file']
        penalties = (configs['playoff_predict_penalties']
                     if 'playoff_predict_penalties' in configs else {})
        playoffs_scores = get_playoffs_scores(playoff_pred_file, season, day,
                                              penalties=penalties,
                                              n_playoff_teams=8)
    else:
        logging.warning('Playoff predictions file not available.')

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
            logging.info('%s is a new player', name)

    # did not play this round
    ii = np.isnan(df_merged['Score'])
    dnp = []
    if any(ii):
        df_new.loc[ii, 'Score'] = min_score
        df_new.loc[ii, 'Missed Rounds'] += 1
        for name in df_new['Name'][ii].values:
            dnp.append(name)
            logging.warning('(DNP): %s did not play this round' % name)

    # check if user has missed more than four rounds.
    mm = df_new['Missed Rounds'] >= 4
    disq = []
    if any(mm):
        for name in df_new['Name'][mm].values:
            logging.warning('(DIS): User %s has missed four rounds and '
                            'is being disqualified', name)
            df_new.drop(df_new[df_new['Name'] == name].index, inplace=True)
            disq.append(name)

    # update points
    df_new['Points'] += df_new['Score'].astype(int)
    # update MVP
    df_new.loc[df_new['Score'] == mvp_score, 'MVP'] += 1
    # convert colums to int type.
    df_new[['Score', 'MVP', 'Points', 'Missed Rounds']] = df_new[
        ['Score', 'MVP', 'Points', 'Missed Rounds']].astype(int)

    new_table = df_new[['Name', 'Score', 'Points',
                        'MVP', 'Missed Rounds']].copy()
    new_table.rename(columns={'Score': 'Round Score'}, inplace=True)
    # merge the score table with the playoff table
    new_table = new_table.merge(playoffs_scores, how='left', left_on='Name',
                                right_index=True)
    new_table['Final_Score'] = new_table['Points'] + new_table['Playoff_Score']

    if sort_by_final == 1:
        # sort by final score (desc), points (desc), MVP (desc)
        # and finally by Name (asc).
        sort_list = ['Final_Score', 'Points', 'MVP', 'Name']
        asc_list = [False, False, False, True]
        new_table = new_table.sort_values(by=sort_list, ascending=asc_list)
        new_table.insert(0, 'Position',
                         np.arange(1, new_table.shape[0] + 1, dtype=int))
    else:
        # sort by points (desc), then by MVP (desc) and finally by name (asc)
        sort_list = ['Points', 'MVP', 'Name']
        asc_list = [False, False, True]
        new_table = new_table.sort_values(by=sort_list, ascending=asc_list)
        new_table.insert(0, 'Position',
                         np.arange(1, new_table.shape[0] + 1, dtype=int))
        # add the final rank
        ii = np.lexsort((new_table['Position'].values,
                         -new_table['Final_Score'].values))
        new_table['Final_Rank'] = ii.argsort() + 1

    if new_table['Playoff_Score'].isna().any():
        logging.warning('Users unknown')

    logging.debug(new_table)

    metadata_file = os.path.join(out_dir, 'metadata_day_%d.json' % day)
    metadata = read_json(metadata_file)
    metadata.update({'dnp': dnp, 'disq': disq})
    write_json(metadata_file, metadata)

    new_table.to_csv(out_file, index=False)

    return new_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--day', type=int, required=True,
                        help='the day (round) of the regular season')
    parser.add_argument('-s', '--sort-by', type=int, choices=[0, 1], default=0,
                        help='1 for sorting by final score, 0 otherwise')
    args = parser.parse_args()

    main(args.day, args.sort_by)
