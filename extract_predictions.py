# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 23:53:57 2018

@author: Georgios
"""
import argparse
import numpy as np
from datetime import datetime
import re
import facebook as fb
import requests
from auxiliary.io_json import read_json, write_json
from auxiliary.read_results import read_results


def main(post_id, results_file, out_file):
    '''TO DO: 
        1) check time-zones
    '''
    # configuration file
    config_file = 'config.json'
    configs = read_json(config_file)
    token = configs['token']
    user_id = configs['user_id']

#    # username to user id 
#    username_id = read_json('usernames.json')

    # read actual results
    results = read_results(results_file)
    
    dt_format = '%Y-%m-%dT%H:%M:%S+0000'

    # make graph
    graph = fb.GraphAPI(access_token=token, version=2.7)
    # graph id = user_id_post_id
    idd = user_id+'_'+post_id
    # get text of post
    post = graph.get_object(id=idd)
    message = post['message']
    end_time = re.search('\d{4,4}-\d{2,2}-\d{2,2} \d{2,2}:\d{2,2}:\d{2,2}', 
                         message)
    if end_time is None:
        print('Warning: Deadline timestamp not found in post.')
        deadline = datetime.now()
    else:
        deadline = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')


    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')
#    comments = comments['comments']['data']
#    comments = comments['data']

    users_dict = {}
    i = 0
    while True:
        for comment in comments['data']:
            user = comment['id']
            text = comment['message']
            time = datetime.strptime(comment['created_time'], dt_format)
            pred = np.array([int(s) for s in text if s.isdigit()])

            # chekc if number of prediction is correct
            if len(pred) != 8:
                print('Warning: Incorrect number of predictions for user %s' % user)
                score = 0
            # check if predictions are either 1 or 2
            elif not ((pred == 1) | (pred == 2)).all():
                print('Warning: Incorrect prediction for user %s' % user)
                score = 0
            # check comment is in time
            elif time > deadline:
                print('Warning: User %s prediction off time' % user)
                print(time, deadline)
                score = 0
            else:
                score = np.sum(pred == results)

            users_dict[user] = int(score)

        if 'next' in comments['paging']:
            comments = requests.get(comments['paging']['next']).json()
        else:
            break

    write_json(out_file, users_dict)

    return users_dict


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
        users_dict = main(args.post_id, args.results_file, args.output)
