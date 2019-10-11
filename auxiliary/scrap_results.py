# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:54:49 2018

@author: Georgios
"""
from bs4 import BeautifulSoup
import requests
import sys
import pandas as pd
import numpy as np
from auxiliary.io_json import read_json


def scrap_round_results(day, season):
    '''
    scrap the results from the euroleague web-page for a particular round.
    Returns results as a dataframe
    '''

    url = ('http://www.euroleague.net/main/results?gamenumber=%d'
           '&phasetypecode=RS&seasoncode=E%d' % (day, season))
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Warning: Connection Error. Check URL or internet connection')
        raise
        # sys.exit('Connection Error. Check URL or internet connection')

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    classstr = 'wp-module wp-module-asidegames wp-module-5lfarqnjesnirthi'
    query = soup.find('div', attrs={'class': classstr})
    results = query.find_all('div', attrs={'class': 'game played'})
    liveresults = query.find_all('div', attrs={'class': 'game',
                                               "data-played": "0"})
    if liveresults != []:
        print('Warning: %d games have not been played yet' % len(liveresults))
    results.extend(liveresults)

    assert (results != []), 'No results found, check if round is valid.'

    data = []
    for r in results:
        teams = r.find_all('span', attrs={'class': 'name'})
        home_team = teams[0].string
        away_team = teams[1].string
        h = r.find('span', {'class': 'score homepts'})['data-score']
        a = r.find('span', {'class': 'score awaypts'})['data-score']
        home_score = int(h) if h.isdigit() else 0
        away_score = int(a) if a.isdigit() else 0
        data.append([home_team, away_team, home_score, away_score])

    data = pd.DataFrame(data, columns=['Home Team', 'Away Team',
                                       'Home Score', 'Away Score'])

    return data


def get_results(games_fb, day, season, team_mapping_file):
    '''
    Finds the results of the games of a round as ordered on the fb post.
    It returns the results as an numpy array.
    '''
    # teams for round's games from the fb post. Convert lists to dataframe
    if isinstance(games_fb, list):
        games_fb = pd.DataFrame(games_fb, columns=['Home Team', 'Away Team'])

    # teams and games' results from web-page
    data = scrap_round_results(day, season)

    if games_fb.shape[0] != data.shape[0]:
        print('Warning: Number of games is inconsistent')

    # first map teams in greek to official english names
    mappednames = read_json(team_mapping_file)
    games_fb.replace(mappednames, inplace=True)

    # after converting the names of the teams, merge the two dataframes
    final = games_fb.merge(data, how='inner',
                           left_on=['Home Team', 'Away Team'],
                           right_on=['Home Team', 'Away Team'])

    if pd.isna(final.values).any():
        sys.exit('Error: nan values appeared after merging the DataFrames.')

    results = np.where(final['Home Score'] > final['Away Score'], 1, 2)
    results[final['Home Score'] == final['Away Score']] = 0

    if results.shape[0] != games_fb.shape[0]:
        # print("Warning: Shape of 'results' var is inconsistent")
        sys.exit("Error: Shape of 'results' var is inconsistent.")

    return results
