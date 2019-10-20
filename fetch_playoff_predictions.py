import argparse
from os import path
import facebook as fb
import requests
from auxiliary.io_json import read_json, write_json


def main(post_id):
    '''
    This function fetches the comments from a facebook post and stores them
    in a json file.
    '''
    # read token's file
    tokens_file = 'config/tokens.json'
    tokens = read_json(tokens_file)
    token = tokens['token']
    user_id = tokens['user_id']

    # set output directory
    config_file = 'config/config_playoff_pred.json'
    if path.isfile(config_file):
        out_dir = read_json(config_file)['output_directory']
    else:
        print('Warning: Configuration file not found.',
              'Save to working directory')
        out_dir = '.'

    # make graph
    graph = fb.GraphAPI(access_token=token, version=3.0)
    # graph id = user_id_post_id
    idd = user_id + '_' + post_id

    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')
    answers = []
    answers.extend(comments['data'])
    # %%
    while True:
        if 'next' in comments['paging']:
            comments = requests.get(comments['paging']['next']).json()
            answers.extend(comments['data'])
        else:
            break

    # write comments to json file.
    write_json(path.join(out_dir, 'playoff_predictions_fb_comments.json'),
               answers)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--post_id', type=str, required=True,
                        help="the id of the post")
    args = parser.parse_args()

    main(args.post_id)
