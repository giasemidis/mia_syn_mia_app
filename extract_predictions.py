# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 23:53:57 2018

@author: Georgios
"""
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import re
import os
import pytz
import facebook as fb
import requests
from auxiliary.io_json import read_json, write_json
from auxiliary.read_results import read_results
from auxiliary.convert_timezone import convert_timezone
import win_unicode_console
win_unicode_console.enable()


def main(post_id, results_file, nday):
    '''TO DO: 
        1) come with a criterion to check whether a comment gives a prediction
            or just discusses things.
    '''
    # tokens file
    tokens_file = 'tokens.json'
    tokens = tokens = read_json(tokens_file)
    token = tokens['token']
    user_id = tokens['user_id']
    
    # configuration file
    config_file = 'config.json'
    configs = read_json(config_file)
    n_games = configs['n_games']
    dt_format = configs['dt_format'] #'%Y.%d.%m. %H:%M' # '%Y-%m-%d %H:%M:%S'
    pattern = configs['dt_pattern']
    out_dir = configs['output_directory']

    fb_format = '%Y-%m-%dT%H:%M:%S+0000'
    
    # read actual results
    results = read_results(results_file)
    
    # make graph
    graph = fb.GraphAPI(access_token=token, version=2.7)
    # graph id = user_id_post_id
    idd = user_id+'_'+post_id
    # get text of post
    post = graph.get_object(id=idd)
    message = post['message']
    post_time = datetime.strptime(post['created_time'], fb_format)
  
    # extract game times from the post
#    pattern =  #'\d{2,2}\.\d{2,2}\. \d{2,2}:\d{2,2}'
#    end_time = re.search('\d{4,4}-\d{2,2}-\d{2,2} \d{2,2}:\d{2,2}:\d{2,2}', 
#                         message)
    end_times = re.findall(pattern, message)

    if end_times is None or end_times==[]:
        print('Warning: Deadline timestamp not found in post.')
        t_now = datetime.utcnow()
        game_times_utc = np.array([t_now.replace(tzinfo=pytz.UTC) for i in range(n_games)])
    else:
        game_times = [datetime.strptime(str(post_time.year)+'.'+t, dt_format) 
                        for t in end_times]
        game_times_utc = np.array([convert_timezone(t, 
                                        from_tz='Europe/Athens', to_tz='UTC')
                                  for t in game_times])

    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')

    score_dict = {}
    predict_dict = {}

    while True:
        for comment in comments['data']:
            comment_id = comment['id']
            text = comment['message']
            time = datetime.strptime(comment['created_time'], fb_format)
            # make the time variable datetime aware
            time = time.replace(tzinfo=pytz.UTC)

            # find username
            user = ''.join([s for s in text if s.isalpha() or s.isspace()]).strip()
            if user == '' or len(user) > 25:
                user = ''
                print('Warning: Username was not found, comment id %s' % comment_id)
                print(text)
                continue

            # find prediction
            pred = np.array([int(s) for s in text if s.isdigit()], dtype=int)

            if pred.size == 0:
                print('Warning: No prediction found, comment id %s' % comment_id)
                print(text)
                continue
            
#            # check if 'from' info is in the fetched comment.
#            if 'from' in comment.keys():
#                print(text, user, time.astimezone())

            # check if predictions are either 1 or 2
            if not ((pred == 1) | (pred == 2)).all():
                print('Warning: Incorrect prediction for user %s in comment %s' 
                      % (user, comment_id))
                print(text)
                tmp = pred.copy()
                tmp[~((pred == 1) | (pred == 2))] = 0

            # check if number of prediction is correct
            if len(pred) != n_games:
                print('Warning: Incorrect number of predictions for user %s in comment %s' 
                      % (user, comment_id))
                print(text)
                if len(pred) < n_games:
                    pred = np.append(pred, np.zeros(n_games-pred.shape[0], 
                                                    dtype=int))
                else:
                    pred = pred[:n_games]

            # check comment is prior game-times.
            ii = time < game_times_utc
            if not ii.all():
                print('Warning: %d Prediction(s) off time for user %s in comment id %s' 
                      % (np.sum(~ii), user, comment_id))
            # if comment after any game started, give 0 points for this game
            pred[~ii] = 0
            score = np.sum(pred[ii] == results[ii])

            # TO DO: check if user has given prediction and decide what to do.
            # if user in users_dict.keys():
            score_dict[user] = int(score)
            predict_dict[user] = pred

        if 'next' in comments['paging']:
            comments = requests.get(comments['paging']['next']).json()
        else:
            break

    # make dataframe from users' score dictionary
    df_scores = pd.DataFrame.from_dict(score_dict, orient='index', 
                                       columns=['Score'])
    # make dataframe from users' predictions dictionary
    df_pred = pd.DataFrame.from_dict(predict_dict, orient='index',
                                     columns=['game_%d' % s for s in 
                                              range(1, n_games+1)])

    # merge the two dataframe based on users' names.
    df = df_scores.merge(df_pred, left_index=True, right_index=True)
    # sort by score (descending) and by name (descending)
    df.rename_axis('Name', axis=0, inplace=True)
    df.sort_values(['Score', 'Name'], ascending=[False, True], inplace=True)
    
    # save dataframe
    df.to_csv(os.path.join(out_dir, 'predictions_day_%d.csv' % nday), sep=',', 
                     index=True, encoding='utf-8')
    
    # save scores json
#    write_json(os.path.join(out_dir, 'scores_day_%d.json' % nday), score_dict)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--post_id', type=str,
                        help="the id of the post")
    parser.add_argument('-r', '--results_file', type=str,
                        help="file with the results")
    parser.add_argument('-d', '--day', type=int,
                        help="day number")
#    parser.add_argument('-o', '--output', type=str,
#                        help="output file to write data")
    args = parser.parse_args()
    if args.post_id is None or args.results_file is None or args.day is None:
        parser.print_help()
    else:
        main(args.post_id, args.results_file, args.day)
