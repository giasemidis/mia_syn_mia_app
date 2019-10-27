import pandas as pd
import re
import sys
import requests
from bs4 import BeautifulSoup


def scrap_standings(season, n_round):
    '''
    Scraps the standings of the Euroleague games from the Euroleague's official
    site for the input season.
    '''

    url = ('http://www.euroleague.net/main/standings?gamenumber=%d&'
           'phasetypecode=RS++++++++&seasoncode=E%d'
           % (n_round, season))
    try:
        r = requests.get(url)
    except ConnectionError:
        sys.exit('Connection Error. Check URL')
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    tbl_cls = ('table responsive fixed-cols-1 table-left-cols-1 '
               'table-expand table-striped table-hover table-noborder '
               'table-centered table-condensed')
    table = soup.find('table', attrs={'class': tbl_cls})
    body = table.find('tbody')
    data = []
    for row in body.find_all('tr'):
        pos_team = row.find('a').string.strip()
        pos = int(re.findall(r'\d{1,2}', pos_team)[0])
        team = re.findall(r'[a-zA-Z\s-]+', pos_team)[0].strip()
        data.append([pos, team])

    df = pd.DataFrame(data, columns=['Rank', 'Team'])
    return df


def compute_playoff_scores(pred_df, actual_table, n_playoff_teams=8):
    '''
    This functions converts the playoff predictions
    and the actual standings into a playoffs score for every
    player.
    Scoring system:
        1) 8 playoff teams.
        2) +1 for every correct answer, -1 for every wrong.
    Returns a DataFrame with the players name and their play-off pred score.
    '''
    out_df = (pred_df.isin(actual_table['Team']
              .values[:8]).sum(axis=1)).to_frame('Playoff_Score')
    # +1 for every correct, -1 for every wrong prediction
    out_df = 2 * out_df - 8
    return out_df


def get_playoffs_scores(playoff_pred_file, season, n_round,
                        penalties={}, n_playoff_teams=8):
    '''
    This function gets the playoff scores of the users/players.
    Returns a DataFrame with the users and their score
    '''
    pred_df = pd.read_csv(playoff_pred_file, index_col='username')
    actual_table = scrap_standings(season, n_round)
    df = compute_playoff_scores(pred_df, actual_table, n_playoff_teams)

    # apply penalties to correspnding users.
    for username in penalties.keys():
        if penalties[username] != 0:
            df.loc[username] -= penalties[username]
        else:
            df.loc[username] = 0

    return df
