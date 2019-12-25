import argparse
import pandas as pd
import regex
import os
from datetime import datetime
import pytz
import logging
from auxiliary.io_json import read_json
from auxiliary.convert_timezone import convert_timezone


def main(comments):
    '''
    Function that extracts the username and the predicted teams of the playoffs
    from the comments (of a facebok post) and converts them to a dataframe,
    which is saved to the disk.
    '''
    logging.basicConfig(level=logging.INFO)

    # read config file
    config_file = 'config/config_playoff_pred.json'
    config = read_json(config_file)
    n_pred_teams = config['n_pred_teams']
    out_dir = config['output_directory']
    team_mappings_file = config['team_names_mapping_file']
    teams_dict = read_json(team_mappings_file)
    deadline = datetime.strptime(config['deadline'], '%Y-%m-%d %H:%M:%S')
    deadline = convert_timezone(deadline, from_tz='Europe/Athens', to_tz='UTC')
    fb_format = '%Y-%m-%dT%H:%M:%S+0000'

    teams = list(teams_dict.keys())
    regexps = ['(?e)(%s){e<=2}' % team for team in teams]
    header = ['team%d' % i for i in range(1, n_pred_teams + 1)]

    all_predictions = []
    usernames = []
    for comment in comments:
        comment_id = comment['id']
        text = comment['message']
        time = datetime.strptime(comment['created_time'], fb_format)
        # make the time variable datetime aware
        time = time.replace(tzinfo=pytz.UTC)
        # check if comment is off time.
        if time > deadline:
            logging.warning('Comment (id %s) is off time: "%s"',
                            comment_id, text)

        text_copy = text.replace('\n', '')
        pred_teams = []
        for team, rxp in zip(teams, regexps):
            r = regex.search(rxp, text)
            if r is not None:
                match = text[r.start():r.end()]
                pred_teams.append(teams_dict[team])
                text_copy = text_copy.replace(match, '').strip()
        username = text_copy.replace('-', '').strip()
        if len(pred_teams) == n_pred_teams:
            all_predictions.append(dict(zip(header, sorted(pred_teams))))
            usernames.append(username)
        else:
            logging.warning('Comment (id %s) is not valid: "%s"',
                            comment_id, text)

    # convert to dataframe
    df = pd.DataFrame(all_predictions, index=usernames)
    df.index.name = 'username'
    # save to file
    df.to_csv(os.path.join(out_dir, 'playoffs_predictions2.csv'), index=True)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str,
                        required=argparse.FileType('r'),
                        help="the file with facebook comments")
    args = parser.parse_args()

    # read comments
    comments = read_json(args.file)

    main(comments)
