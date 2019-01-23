# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 02:11:36 2018

@author: Georgios
"""
import argparse
import pandas as pd
import numpy as np
import os
import sys
import facebook as fb
from auxiliary.io_json import read_json
import win_unicode_console
win_unicode_console.enable()


def main(day, post=False):
    '''
    This function creates a text-based table with info about the round's MVP,
    etc., and posts it on the Facebook group.
    WARNING: After experimentation, the post is not visible to every member
    of the group, therefore this method was ignored. However, it is used for 
    producing the text of MVPs, DNPs, etc., to a flat file, from which it is 
    copied and manually posted on FB.
    If a user wants to post the table on FB, set post input to True.
    '''
    
    # tokens file
    tokens_file = 'config/tokens.json'
    tokens = tokens = read_json(tokens_file)
    token = tokens['token']
    user_id = tokens['user_id']
    group_id = tokens['mia_syn_mia_id']

    # configuration file
    config_file = 'config/config.json'
    configs = read_json(config_file)
    out_dir = configs['output_directory']
    n_games = configs['n_games']

    # read the latest table file
    table_file = os.path.join(out_dir, 'table_day_%d.csv' % day)
    # load the mvp, dnp and offtime usernames produced by other scripts.
    temp = np.load(os.path.join(out_dir, 'mvp.npz'))
    mvps = temp['mvps']
    mvp_score = temp['mvp_score']
    dnp_score = temp['dnp_score'] if 'dnp_score' in temp.keys() else None
    temp = np.load(os.path.join(out_dir, 'dnp.npz'))
    dnps = temp['dnp'] if 'dnp' in temp.keys() else []
    disqs = temp['disq'] if 'disq' in temp.keys() else []
    offtime = np.load(os.path.join(out_dir, 'offtime.npy'))

    # ask for input optional message
    optional = input('Optional message:')
    
    # form the string
    mvp_str = 'MVPs: ' + ', '.join(['@{}'.format(name) for name in mvps]) +\
                ' με {}/{} σωστές προβλέψεις.'.format(mvp_score, n_games)

    verb = 'λαμβάνει' if len(dnps) == 1 else 'λαμβάνουν'
    if len(dnps) >  0:
        dnp_str = 'DNP: ' + ', '.join(['@{}'.format(name) for name in dnps]) +\
           ' και {} τη χαμηλότερη βαθμολογία ({})'.format(verb, dnp_score) + '\n' 
    else:
        dnp_str = 'DNP: -' + '\n'

    if len(dnps) >  0:
        offtime_str = 'Off time: ' + ', '.join(['@{} ({})'.format(*u) for u 
                                                in offtime]) + '\n'
    else:
        offtime_str = 'Off time: -' + '\n'

    verb = 'συμπλήρωσε' if len(disqs) == 1 else 'συμπλήρωσαν'
    if len(disqs) > 0:
        disq_str = ', '.join(['@{}'.format(name) for name in disqs]) +\
                    ' καθώς {} 4 απουσίες.'.format(verb) + '\n'
    else:
        disq_str = ''
        

    # form the table
    table = pd.read_csv(table_file)
    maxlen = table['Name'].str.len().max()
    s = 'Rank--Name--MVP--Points--DNP\n'
    for row in table.values:
        fillin = maxlen - len(row[1]) + 2
        s1 = '%d---%s' % (row[0], row[1]) if row[0] < 10 else '%d--%s' % (row[0], row[1])
        s += s1 + '-'*fillin + '%d--%d--%d\n' % (row[2], row[3], row[4])
        if row[0] == 4:
            s += '-'*37 + '\n'
        elif row[0] == 12:
            s += '='*37 + '\n'
    table_str = s

    # concatenate the string
    stats = mvp_str + dnp_str + offtime_str + disq_str

    start = 'Αποτελέσματα Euroleague Day %d' % day
    end = '#feeldevotion #euroleague #day%d #mia_syn_mia #oneplusone' % day
    final = start + '\n\n' + optional + '\n\n' + stats + '\n' + table_str + '\n' + end

    # write the text to a text file for inspection
    with open('temp_table.txt', 'w', encoding='utf=8') as f:
        f.writelines(final)

    # post the final text to facebook.
    if post:
        graph = fb.GraphAPI(access_token=token, version=3.0)
        
        graph.put_object(parent_object=group_id, connection_name='feed',
                         message=final)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--day', type=int,
                        help='the day (round) of the regular season')
    parser.add_argument('-p','--post', type=bool,
                        help='a boolean (optional) that indicates whether the text is posted on FB. Default value is False')
    args = parser.parse_args()
    if args.day is None:
        parser.print_help()
    else:
        main(args.day, args.post)
