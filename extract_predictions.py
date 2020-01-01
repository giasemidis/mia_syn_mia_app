import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import re
import os
import sys
import pytz
import facebook as fb
import requests
import logging
from auxiliary.io_json import read_json
from auxiliary.read_results import read_results
from auxiliary.convert_timezone import convert_timezone
from auxiliary.valid_post import valid_post
from auxiliary.scrap_results import get_results


def main(post_id, results_file, nday):
    '''
    '''
    logging.basicConfig(level=logging.INFO)

    # tokens file
    tokens_file = 'config/tokens.json'
    tokens = read_json(tokens_file)
    token = tokens['token']
    user_id = tokens['user_id']

    # configuration file
    config_file = 'config/config.json'
    configs = read_json(config_file)
    n_games = configs['n_games']
    season = configs['season']
    dt_format = configs['dt_format']
    pattern = configs['dt_pattern']
    out_dir = configs['output_directory']
    team_mapping_file = configs['team_names_mapping_file']

    fb_format = '%Y-%m-%dT%H:%M:%S+0000'

    # make graph
    graph = fb.GraphAPI(access_token=token, version=3.0)
    # graph id = user_id_post_id
    idd = user_id+'_'+post_id
    # get text of post
    post = graph.get_object(id=idd)
    message = post['message']
    post_time = datetime.strptime(post['created_time'], fb_format)

    # fetch actual results from the web -- restrictions apply
    if results_file is None:
        results_file = os.path.join(out_dir, 'results_day_%d.txt' % nday)
    repat = re.compile(pattern)
    games_times = re.findall(pattern + r'[^\d\n]*', message)
    games = [[u.strip() for u in repat.sub('', game).split('-')] for
             game in games_times]
    if len(games) != n_games:
        # check if the number of games identified in the post is correct.
        logging.error('Number of games identified on FB post is incorrect')
        sys.exit('Exit')
    else:
        try:
            # fetch results from the web
            results = get_results(games, nday, season, team_mapping_file)
            # write results to file
            np.savetxt(results_file, results[None], delimiter=' ', fmt='%d')
        except (requests.exceptions.ConnectionError, AssertionError) as e:
            logging.error(e)
            # if there is a connection error, read results from file.
            logging.warning('Unable to fetch results from the internet. '
                            'Try from flat file.')
            # if file does not exist, exit program and ask for file of results.
            if not os.path.isfile(results_file):
                logging.error('Provide correct file with the results.')
                sys.exit('Exit')
            # read actual results
            results = read_results(results_file)

    logging.info(results)

    if results.shape[0] != n_games:
        logging.error('Results not valid')
        sys.exit('Exit')

    # extract game times from the post
    end_times = re.findall(pattern, message)

    if end_times is None or end_times == []:
        logging.warning('Deadline timestamp not found in post.')
        t_now = datetime.utcnow()
        game_times_utc = np.array([t_now.replace(tzinfo=pytz.UTC)
                                   for i in range(n_games)])
    else:
        game_times = [datetime.strptime(str(post_time.year)+'.'+t, dt_format)
                      for t in end_times]
        game_times_utc = np.array([convert_timezone(t, from_tz='Europe/Athens',
                                                    to_tz='UTC')
                                   for t in game_times])

    # Get the comments from a post.
    comments = graph.get_connections(id=idd, connection_name='comments')

    score_dict = {}
    predict_dict = {}
    offtime = []
    while True:
        for comment in comments['data']:
            comment_id = comment['id']
            text = comment['message']
            time = datetime.strptime(comment['created_time'], fb_format)
            # make the time variable datetime aware
            time = time.replace(tzinfo=pytz.UTC)

            is_valid, user, pred = valid_post(text, comment_id=comment_id,
                                              n_games=n_games)

            if is_valid is False:
                logging.debug('Comment id %s not valid' % comment_id)
                continue

            # check comment is prior game-times.
            ii = time < game_times_utc
            if not ii.all():
                offtime.append((user, np.sum(~ii)))
                logging.warning('%d Prediction(s) off time for user %s in '
                                'comment (id %s): %s',
                                np.sum(~ii), user, comment_id, text)
            # if comment after any game started, give 0 points for this game
            pred[~ii] = 0
            score = np.sum(pred[ii] == results[ii])

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

    np.save(os.path.join(out_dir, 'offtime'), offtime)
    np.savez(os.path.join(out_dir, 'mvp'),
             mvps=df[df['Score'] == df['Score'].max()].index.values,
             mvp_score=df['Score'].max(), dnp_score=df['Score'].min())

    # save dataframe
    df.to_csv(os.path.join(out_dir, 'predictions_day_%d.csv' % nday), sep=',',
              index=True, encoding='utf-8')

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--post_id', type=str, required=True,
                        help="the id of the post")
    parser.add_argument('-r', '--results_file', type=str,
                        help="file with the results", default=None)
    parser.add_argument('-d', '--day', type=int, required=True,
                        help="the day (round) of the regular season")
    args = parser.parse_args()

    main(args.post_id, args.results_file, args.day)
