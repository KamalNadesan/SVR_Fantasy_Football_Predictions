#!usr/local/bin/python

import nflgame
from get_data import fetch_defense_stats, fetch_qb_stats, test_players, determine_team
""" Purpose: Determine whether a game was a home game or away game and output result

"""


""" create dictionary consisting of all games in the used
year. All these games have a single attribute 'played'
set to False.
"""
def create_empty_entry():
    dict = {}
    for year in range(2009, 2015):
        dict[str(year)] = {}
        for week in range(1, 18):
            dict[str(year)][str(week)] = {'played': False}
    return dict
