import argparse
# import numpy as np
# import pandas as pd
from datetime import datetime
# import re
# import os
# import sys
import pytz
import facebook as fb
import requests
from auxiliary.io_json import read_json, write_json


def main(post_id):
    tokens_file = 'config/tokens.json'
    tokens = read_json(tokens_file)
    token = tokens['token']
    user_id = tokens['user_id']

    fb_format = '%Y-%m-%dT%H:%M:%S+0000'

    # make graph
    graph = fb.GraphAPI(access_token=token, version=3.0)
    # graph id = user_id_post_id
    idd = user_id + '_' + post_id
    # get text of post
    # post = graph.get_object(id=idd)
    # message = post['message']
    # post_time = datetime.strptime(post['created_time'], fb_format)

    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')
    answers = []
    answers.extend(comments['data'])
    # %%
    while True:
        for comment in comments['data']:
            # comment_id = comment['id']
            # text = comment['message']
            time = datetime.strptime(comment['created_time'], fb_format)
            # make the time variable datetime aware
            time = time.replace(tzinfo=pytz.UTC)

        if 'next' in comments['paging']:
            comments = requests.get(comments['paging']['next']).json()
            answers.extend(comments['data'])
        else:
            break

    write_json('output/playoff_predictions_fb_comments.json', answers)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--post_id', type=str, required=True,
                        help="the id of the post")
    args = parser.parse_args()

    main(args.post_id)
