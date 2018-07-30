# Copyright (c) Roman Lutz. All rights reserved.
# The use and distribution terms for this software are covered by the
# Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
# which can be found in the file LICENSE.md at the root of this distribution.
# By using this software in any fashion, you are agreeing to be bound by
# the terms of this license.
# You must not remove this notice, or any other, from this software.

import pdb
import datetime
import nflgame

""" Map the team abbreviations in the JSON files to the team names
 Teams may relocate and/or change team abbreviations so only use team names
 without geographic reference when retrieving data from the JSON files when
 team names need to be stored
 - Updated for Chargers, Rams, Raiders
 - Updated for Jags: Necessary since abbreviation changes
   (JAC(2009) -> JAX(year > 2009)
 *NOTE: This code requires manual updates if teams change or are new teams added
 Return Type: String or ValueError
"""
def abbrev_to_name(team):
    # listed in alphabetical order for abbreviation
    if(team == 'ARI'):
        team = 'Cardinals'
    elif(team == 'ATL'):
        team = 'Falcons'
    elif(team == 'BAL'):
        team = 'Ravens'
    elif(team == 'BUF'):
        team = 'Bills'
    elif(team == 'CAR'):
        team = 'Panthers'
    elif(team == 'CHI'):
        team = 'Bears'
    elif(team == 'CIN'):
        team = 'Bengals'
    elif(team == 'CLE'):
        team = 'Browns'
    elif(team == 'DAL'):
        team = 'Cowboys'
    elif(team == 'DEN'):
        team = 'Broncos'
    elif(team == 'DET'):
        team = 'Lions'
    elif(team == 'GB'):
        team = 'Packers'
    elif(team == 'HOU'):
        team = 'Texans'
    elif(team == 'IND'):
        team = 'Colts'
    elif(team == 'JAX' or team == 'JAC'):
        team = 'Jaguars'
    elif(team == 'KC'):
        team = 'Chiefs'
    elif(team == 'LA' or team == 'STL'):
        team = 'Rams'
    elif(team == 'LAC' or team == 'SD'):
        team = 'Chargers'
    elif(team == 'MIA'):
        team = 'Dolphins'
    elif(team == 'MIN'):
        team = 'Vikings'
    elif(team == 'NE'):
        team = 'Patriots'
    elif(team == 'NO'):
        team = 'Saints'
    elif(team == 'NYG'):
        team = 'Giants'
    elif(team == 'NYJ'):
        team = 'Jets'
    elif(team == 'OAK' or team == 'LV' or team == 'LVR'):
        team = 'Raiders'
    elif(team == 'PHI'):
        team = 'Eagles'
    elif(team == 'PIT'):
        team = 'Steelers'
    elif(team == 'SEA'):
        team = 'Seahawks'
    elif(team == 'SF'):
        team = '49ers'
    elif(team == 'TB'):
        team = 'Buccaneers'
    elif(team == 'TEN'):
        team = 'Titans'
    elif(team == 'WAS'):
        team = 'Redskins'
    else:
        raise(ValueError('Unexpected Team Name %s' % (team)))
    return(team)


""" create dictionary consisting of all games in the used
year. All these games have a single attribute 'played'
set to False.
"""
def create_empty_entry():
    dict = {}
    for year in range(2009, 2018):
        dict[str(year)] = {}
        for week in range(1, 18):
            dict[str(year)][str(week)] = {'played': False}
    return dict

""" Returns a dictionary with the name, birthdate
and the number of years the player has spent as a
professional player.
"""
def get_static_data(id):
    player = nflgame.players[id]
    return {'name': player.full_name,
            'birthdate': player.birthdate,
            'years_pro': player.years_pro}


""" Checks if player had a single team in one season and
return team, if multiple teams: return None
"""
def determine_team(year_data):
    teams = {}
    games = 0
    for week in year_data.keys():
        if year_data[week]['played']:
            games += 1
            if year_data[week]['home'] in teams.keys():
                teams[year_data[week]['home']] += 1
            else:
                teams[year_data[week]['home']] = 1
            if year_data[week]['away'] in teams.keys():
                teams[year_data[week]['away']] += 1
            else:
                teams[year_data[week]['away']] = 1
    for team in teams.keys():
        #bp()
        # if one team occurs in every game, return game
        if teams[team] == games:
            return team
    # no team occurs in every game
    return None



""" Gets all QB statistics in a single dictionary.
The keys are the player names, the value for each player
is a dictionary with all his game statistics.
"""
def fetch_qb_stats():
    # statistics is a dictionary of all player stats
    # the keys are player names, the values are lists
    # each list contains dictionaries that contain single game stats
    statistics = {}
    teams = map(lambda x: x[0], nflgame.teams)
    # u'00-0019596' = Tom Brady
    for year in range(2009, 2018):
        for week in range(1, 18):
            games = nflgame.games(year=year, week=week)
            for index, game in enumerate(games):
                players = nflgame.combine([games[index]])
                # every player with at least 5 passing attempts
                # less than five is not taken into account
                for player in filter(lambda player: player.passing_att >= 5, players.passing()):
                    # if player has not been saved before create entry
                    # Only add the stats for tom Brady
                    # Brees = u'00-0020531'
                    # blake = u'00-0031407'
                    # cam = u'00-0027939'
                    # '00-0022924': 'Ben Roethlisberger'
                    if(player.playerid != u'00-0020531'):
                        continue
                    #pdb.set_trace()
                    if not(player.playerid in statistics.keys()):
                        statistics[player.playerid] = create_empty_entry()
                        statistics[player.playerid].update(get_static_data(id = player.playerid))
                    # save data in dictionary
                    #pdb.set_trace()
                    statistics[player.playerid][str(year)][str(week)] = {
                        'home': abbrev_to_name(game.home),
                        'away': abbrev_to_name(game.away),
                        'passing_attempts': player.passing_att,
                        'passing_yards': player.passing_yds,
                        'passing_touchdowns': player.passing_tds,
                        'passing_interceptions': player.passing_ints,
                        'passing_two_point_attempts': player.passing_twopta,
                        'passing_two_point_made': player.passing_twoptm,
                        'rushing_attempts': player.rushing_att,
                        'rushing_yards': player.rushing_yds,
                        'rushing_touchdowns': player.rushing_tds,
                        'rushing_two_point_attempts': player.rushing_twopta,
                        'rushing_two_point_made': player.rushing_twoptm,
                        'fumbles': player.fumbles_tot,
                        'played': True
                        }
    """if(year == 2017):
        pdb.set_trace() """
    return statistics





""" Get the game statistics of all 32 defenses of all
games in the observed time. The dictionary is indexed
by the team's abbreviation, e.g. ATL for Atlanta.
"""
def fetch_defense_stats():
    # team defense statistics
    statistics = {}
    #print(nflgame.teams)
    for team in map(lambda x: x[0], nflgame.teams):
        team = abbrev_to_name(team)
        statistics[team] = create_empty_entry()
    for year in range(2009, 2018):
        for week in range(1, 18):
            #import pdb; pdb.set_trace()
            for game in nflgame.games(year=year, week=week):
                home = abbrev_to_name(game.home)
                away = abbrev_to_name(game.away)
                s = "home: " + home + " " + "away: " + away
                #print(s)
                statistics[home][str(year)][str(week)] = {
                    'home': home,
                    'away': away,
                    'points_allowed': game.score_away,
                    'passing_yards_allowed': game.stats_away[2],
                    'rushing_yards_allowed': game.stats_away[3],
                    'turnovers': game.stats_away[6],
                    'played': True
                }
                statistics[away][str(year)][str(week)] = {
                    'home': home,
                    'away': away,
                    'points_allowed': game.score_home,
                    'passing_yards_allowed': game.stats_home[2],
                    'rushing_yards_allowed': game.stats_home[3],
                    'turnovers': game.stats_home[6],
                    'played': True
                }

    return statistics