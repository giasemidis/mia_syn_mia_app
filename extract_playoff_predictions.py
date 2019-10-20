import argparse
import pandas as pd
import regex
from auxiliary.io_json import read_json


def main(comments):
    '''
    Function that extracts the username and the predicted teams of the playoffs
    from the comments (of a facebok post) and converts them to a dataframe,
    which is saved to the disk.
    '''
    teams = ['Alba Berlin', 'Anadolu Efes', 'Armani Milano', 'Crvena Zvezda',
             'CSKA Moscow', 'FC Barcelona', 'FC Bayern Munich',
             'Fenerbahce Istanbul', 'Khimki Moscow region',
             'Baskonia Vitoria-Gasteiz', 'ASVEL Villeurbanne',
             'Maccabi Tel Aviv', 'Olympiakos Piraeus', 'Panathinaikos Athens',
             'Real Madrid', 'Valencia Basket', 'Zalgiris Kaunas',
             'Zenit St. Petersburg']
    regexps = ['(?e)(%s){e<=2}' % team for team in teams]
    n_pred_teams = 8
    header = ['team%d' % i for i in range(1, n_pred_teams + 1)]

    all_predictions = []
    usernames = []
    for comment in comments:
        text = comment['message']
        text_copy = text.replace('\n', '')
        pred_teams = []
        for team, rxp in zip(teams, regexps):
            r = regex.search(rxp, text)
            if r is not None:
                match = text[r.start():r.end()]
                pred_teams.append(team)
                text_copy = text_copy.replace(match, '').strip()
        username = text_copy.replace('-', '').strip()
        if len(pred_teams) == n_pred_teams:
            all_predictions.append(dict(zip(header, sorted(pred_teams))))
            usernames.append(username)
        else:
            print(text+'\n')

    # convert to dataframe
    df = pd.DataFrame(all_predictions, index=usernames)
    df.index.name = 'username'
    # save to file
    df.to_csv('output/playoffs_predictions.csv', index=True)
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
