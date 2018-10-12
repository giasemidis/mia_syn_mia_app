# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 23:53:57 2018

@author: Georgios
"""
import argparse
import numpy as np
from datetime import datetime
import re
import pytz
import facebook as fb
import requests
from auxiliary.io_json import read_json, write_json
from auxiliary.read_results import read_results
from auxiliary.convert_timezone import convert_timezone


def main(post_id, results_file, out_file):
    '''TO DO: 
        1) come with a criterion to check whether a comment gives a prediction
            or just discusses things.
    '''
    # configuration file
    config_file = 'config.json'
    configs = read_json(config_file)
    token = configs['token']
    user_id = configs['user_id']

#    # username to user id 
#    usernames = read_json('usernames.csv')

    # read actual results
    results = read_results(results_file)
    
    n_games = 8
    fb_format = '%Y-%m-%dT%H:%M:%S+0000'

    # make graph
    graph = fb.GraphAPI(access_token=token, version=2.7)
    # graph id = user_id_post_id
    idd = user_id+'_'+post_id
    # get text of post
    post = graph.get_object(id=idd)
    message = post['message']

    # extract game times from the post
    pattern = '\d{2,2}\.\d{2,2}\. \d{2,2}:\d{2,2}'
    dt_format = '%Y.%d.%m. %H:%M' # '%Y-%m-%d %H:%M:%S'
#    end_time = re.search('\d{4,4}-\d{2,2}-\d{2,2} \d{2,2}:\d{2,2}:\d{2,2}', 
#                         message)
    end_times = re.findall(pattern, message)

    if end_times is None or end_times==[]:
        print('Warning: Deadline timestamp not found in post.')
        t_now = datetime.utcnow()
        game_times_utc = np.array([t_now.replace(tzinfo=pytz.UTC) for i in range(n_games)])
    else:
#        deadline = datetime.strptime(end_times, dt_format)
        game_times = [datetime.strptime('2018.'+t, dt_format) for t in end_times]
        game_times_utc = np.array([convert_timezone(t, 
                                        from_tz='Europe/Athens', to_tz='UTC')
                                  for t in game_times])

    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')

    users_dict = {}

    while True:
        for comment in comments['data']:
#            print(comment.keys())
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

            # find prediction
            pred = np.array([int(s) for s in text if s.isdigit()])
            
#            # check if 'from' info is in the fetched comment.
#            if 'from' in comment.keys():
#                print(text, user, time.astimezone())

            # chekc if number of prediction is correct
            if len(pred) != n_games:
                print('Warning: Incorrect number of predictions for user %s in comment %s' 
                      % (user, comment_id))
                score = 0

            # check if predictions are either 1 or 2
            elif not ((pred == 1) | (pred == 2)).all():
                print('Warning: Incorrect prediction for user %s in comment %s' 
                      % (user, comment_id))
                score = 0

            else:
                # check comment is prior game-times.
                ii = time < game_times_utc
                if not ii.all():
                    print('Warning: %d Prediction(s) off time for user %s in comment id %s' 
                          % (np.sum(~ii), user, comment_id))
                # if comment after any game started, give 0 points for this game
                score = np.sum(pred[ii] == results[ii])

            # TO DO: check if user has given prediction and decide what to do.
            # if user in users_dict.keys():
            users_dict[user] = int(score)

        if 'next' in comments['paging']:
            comments = requests.get(comments['paging']['next']).json()
        else:
            break

    write_json(out_file, users_dict)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--post_id', type=str,
                        help="the id of the post")
    parser.add_argument('-r', '--results_file', type=str,
                        help="file with the results")
    parser.add_argument('-o', '--output', type=str,
                        help="output file to write data")
    args = parser.parse_args()
    if args.post_id is None or args.results_file is None or args.output is None:
        parser.print_help()
    else:
        message = main(args.post_id, args.results_file, args.output)
