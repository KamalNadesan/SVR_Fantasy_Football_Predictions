# Copyright (c) Roman Lutz. All rights reserved.
# The use and distribution terms for this software are covered by the
# Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
# which can be found in the file LICENSE.md at the root of this distribution.
# By using this software in any fashion, you are agreeing to be bound by
# the terms of this license.
# You must not remove this notice, or any other, from this software.








































import pdb
from pdb import set_trace as bp
import datetime
from get_data import fetch_defense_stats, fetch_qb_stats, determine_team
import numpy as np
from bs4 import BeautifulSoup
import requests
import time


# players to test in models.py, filled by create_row
test_players = {
    
}


""" Returns stats of the player or team corresponding to the id
for the last game before the given week in the given year
"""
def last_game(statistics, id, year, week):
    # if the week was the first, go back by one week
    week -= 1
    if(week == 0):
        week = 17
        year -= 1
    # check if there are previous years
    # NOTE: data unavailable from NFL GameCenter if year < 2009
    # check if the
    if year < 2009 or year > 2017:
        return None, None, None
    #print(statistics[id][str(year)][str(week)])
    # check if the team/player played in the given week
    # if not played, recursively call previous week to check
    if not(statistics[id][str(year)][str(week)]['played']):
        return last_game(statistics, id, year, week)
    # team/player played in the given week, return stats
    else:
        return statistics[id][str(year)][str(week)], year, week

""" Returns the statistics of the last k games for the given
player or team corresponding to the id. If there are less than
k games, only the existing ones are returned.
"""
def last_k_games(k, statistics, id, year, week):
    stats, year, week = last_game(statistics, id, year, week)
    last_k = [stats]
    k -= 1
    # case 1: no prior games
    if stats == None:
        return []
    # case 2: only one game requested
    if k == 0:
        return last_k

    # case 3: multiple games requested
    # repeatedly check if there are further games
    while last_k[-1] != None and k > 0:
        stats, year, week = last_game(statistics, id, year, week)
        last_k.append(stats)
        k -= 1
    # if None appears in the list, remove it
    return last_k[:-1] if last_k[-1] == None else last_k

""" Calculates the average stats of a defense over the games
handed over to the function.
"""
def average_defense_stats(games):
    points = 0
    passing_yards = 0
    rushing_yards = 0
    turnovers = 0

    n_games = len(games)

    if n_games == 0:
        return None

    for game in games:
        points += game['points_allowed']
        passing_yards += game['passing_yards_allowed']
        rushing_yards += game['rushing_yards_allowed']
        turnovers += game['turnovers']

    return {
        'points_allowed': float(points)/float(n_games),
        'passing_yards_allowed': float(passing_yards)/float(n_games),
        'rushing_yards_allowed': float(rushing_yards)/float(n_games),
        'turnovers': float(turnovers)/float(n_games),
    }

""" Calculates the average QB stats over the games
handed over to the function.
"""
def average_qb_stats(games):
    passing_attempts = 0
    passing_yards = 0
    passing_touchdowns = 0
    passing_interceptions = 0
    passing_two_point_attempts = 0
    passing_two_point_made = 0
    rushing_attempts = 0
    rushing_yards = 0
    rushing_touchdowns = 0
    rushing_two_point_attempts = 0
    rushing_two_point_made = 0
    fumbles = 0

    n_games = len(games)

    if n_games == 0:
        return None

    for game in games:
        passing_attempts += game['passing_attempts']
        passing_yards += game['passing_yards']
        passing_touchdowns += game['passing_touchdowns']
        passing_interceptions += game ['passing_interceptions']
        passing_two_point_attempts += game['passing_two_point_attempts']
        passing_two_point_made += game['passing_two_point_made']
        rushing_attempts += game['rushing_attempts']
        rushing_yards += game['rushing_yards']
        rushing_touchdowns += game['rushing_touchdowns']
        rushing_two_point_attempts += game['rushing_two_point_attempts']
        rushing_two_point_made += game['rushing_two_point_made']
        fumbles += game['fumbles']

    return {
        'passing_attempts': float(passing_attempts)/float(n_games),
        'passing_yards': float(passing_yards)/float(n_games),
        'passing_touchdowns': float(passing_touchdowns)/float(n_games),
        'passing_interceptions': float(passing_interceptions)/float(n_games),
        'passing_two_point_attempts': float(passing_two_point_attempts)/float(n_games),
        'passing_two_point_made': float(passing_two_point_made)/float(n_games),
        'rushing_attempts': float(rushing_attempts)/float(n_games),
        'rushing_yards': float(rushing_yards)/float(n_games),
        'rushing_touchdowns': float(rushing_touchdowns)/float(n_games),
        'rushing_two_point_attempts': float(rushing_two_point_attempts)/float(n_games),
        'rushing_two_point_made': float(rushing_two_point_made)/float(n_games),
        'fumbles': float(fumbles)/float(n_games)
    }

""" Calculates the age of a player for a given game.
"""
def calculate_age(birthdate, game_week, game_year):
    if birthdate[1] == '/':
        birthdate = '0' + birthdate
    birth_month = int(birthdate[0:2])
    if birthdate[4] == '/':
        birthdate = birthdate[:3] + '0' + birthdate[3:]
    birth_day = int(birthdate[3:5])
    birth_year = int(birthdate[6:10])
    total_days = 1 + (game_week - 1) * 7
    game_month = 9 + int(total_days / 31)
    game_day = total_days % 31
    age = game_year - birth_year
    age += float(game_month - birth_month) / 12
    age += float(game_day - birth_day) / 365
    return age



""" Determines if the player is playing in a home game or an away game.
Returns a string value by comparing qb_team with home_team and away_team
in which the result will be a float, 1.0 if "Home" or  0.0 if "Away" if qb_team has a match
An exception is raised if qb_team does not match home_team or away_team
"""
def is_last_game_home(qb_team, home_team, away_team):
    if (qb_team == home_team):
        return 1.0
    elif (qb_team == away_team):
        return 0.0
    else:
        raise ValueError("Unexpected value in is_home: qb_team does not match home or away team")


def map_opponent(team):
    # listed in alphabetical order for abbreviation
    if(team == 'Cardinals'):
        team = 0.0
    elif(team == 'Falcons'):
        team = 1.0
    elif(team == 'Ravens'):
        team = 2.0
    elif(team == 'Bills'):
        team = 3.0
    elif(team == 'Panthers'):
        team = 4.0
    elif(team == 'Bears'):
        team = 5.0
    elif(team == 'Bengals'):
        team = 6.0
    elif(team == 'Browns'):
        team = 7.0
    elif(team == 'Cowboys'):
        team = 8.0
    elif(team == 'Broncos'):
        team = 9.0
    elif(team == 'Lions'):
        team = 10.0
    elif(team == 'Packers'):
        team = 11.0
    elif(team == 'Texans'):
        team = 12.0
    elif(team == 'Colts'):
        team = 13.0
    elif(team ==  'Jaguars'):
        team = 14.0
    elif(team == 'Chiefs'):
        team = 15.0
    elif(team == 'Rams'):
        team = 16.0
    elif(team == 'Chargers'):
        team = 17.0
    elif(team == 'Dolphins'):
        team = 18.0
    elif(team == 'Vikings'):
        team = 19.0
    elif(team == 'Patriots'):
        team = 20.0
    elif(team == 'Saints'):
        team = 21.0
    elif(team == 'Giants'):
        team = 22.0
    elif(team == 'Jets'):
        team = 23.0
    elif(team == 'Raiders'):
        team = 24.0
    elif(team == 'Eagles'):
        team = 25.0
    elif(team == 'Steelers'):
        team = 26.0
    elif(team == 'Seahawks'):
        team = 27.0
    elif(team == '49ers'):
        team = 28.0
    elif(team == 'Buccaneers'):
        team = 29.0
    elif(team == 'Titans'):
        team = 30.0
    elif(team == 'Redskins'):
        team = 31.0
    else:
        raise(ValueError('Unexpected Team Name %s' % (team)))
    return(float(team))



""" Creates a row for the dataset. It is assumed
that the player with the given ID actually played
in the given week and year.
"""
def create_row(qb_statistics, defense_statistics, rookie_statistics, id, year, week):
    age = calculate_age(qb_statistics[id]['birthdate'], week, year)
    years_pro = (qb_statistics[id]['years_pro'] - (2017 - year)) - 1

    #years_pro = qb_statistics[id]['years_pro'] 
    last_game_qb_stats = average_qb_stats(last_k_games(1, qb_statistics, id, year, week))
    if last_game_qb_stats == None:
        # replace last_game_stats with rookie stats
        last_game_qb_stats = rookie_statistics

    last_10_games_qb_stats = average_qb_stats(last_k_games(10, qb_statistics, id, year, week))
    if last_10_games_qb_stats == None:
        # replace last_10_games with rookie stats
        last_10_games_qb_stats = rookie_statistics

    # find out the opposing team by determining which team the QB plays for
    # the API does only allow to query the current team (as of 2015) -> Until I fixed it now it works for 2015-
    qb_team = determine_team(qb_statistics[id][str(year)])
    # if QB had multiple teams in the given year, don't include QB stats
    if(qb_team == None):
        return None
    home_team = qb_statistics[id][str(year)][str(week)]['home']
    away_team = qb_statistics[id][str(year)][str(week)]['away']
    # take other team as opponent
    if(away_team == qb_team):
        opponent = home_team
    else:
        opponent = away_team
    #opponent = home_team if away_team == qb_team else away_team
    # the defense stats should only be used based on some data
    # it cannot be substituted by 'rookie' stats
    last_game_defense_stats     = average_defense_stats(last_k_games(1, defense_statistics, opponent, year, week))
    last_10_games_defense_stats = average_defense_stats(last_k_games(10, defense_statistics, opponent, year, week))
    
    """ should add opponent"""
    # row consists of
    # 0: QB id
    # 1: QB name
    # 2: QB age
    # 3: QB years pro
    # 4: Last game home(1.0) or away(0.0)
    # 5-16: last game QB stats
    # 17-28: last 10 games QB stats
    # 29-32: last game defense stats
    # 33-36: last 10 games defense stats
    # 37: actual fantasy score = target

     # add all quarterbacks to test_data for models.py
    """if(year == 2017 and id not in test_players):
        test_players[id] = qb_statistics[id]['name']
       """ 
    if(id != u'00-0020531'):
        raise ValueError("Not Tom Brady")
    test_players[id] = qb_statistics[id]['name'],

    """ should add opponent"""
    # row consists of
    # 0: QB id
    # 1: QB name
    # 2: QB age
    # 3: QB years pro
    # 4: Last game opponent (values in map_opponent(opponent))
    # 5: Last game home(1.0) or away(0.0)
    # 6-18: last game QB stats
    # 19-31: last 10 games QB stats
    # 32-35: last game defense stats
    # 36-39: last 10 games defense stats
    # 40: actual fantasy score = target
    
    last_game_yards_per_attempt     = (float(last_game_qb_stats['passing_yards']) / float(last_game_qb_stats['passing_attempts']))
    last_10_games_yards_per_attempt = (float(last_10_games_qb_stats['passing_yards']) / float(last_10_games_qb_stats['passing_attempts']))
    last_game_opponent = map_opponent(opponent)
    #pdb.set_trace()
    """ ADD PASSING COMPLETION 
    add first down completion rate
    add overall completion rate
    """
    return [id,
            qb_statistics[id]['name'],
            age,
            years_pro,
            last_game_opponent,
            is_last_game_home(qb_team, home_team, away_team),
            last_game_qb_stats['passing_attempts'],
            last_game_qb_stats['passing_yards'],
            last_game_yards_per_attempt,
            last_game_qb_stats['passing_touchdowns'],
            last_game_qb_stats['passing_interceptions'],
            last_game_qb_stats['passing_two_point_attempts'],
            last_game_qb_stats['passing_two_point_made'],
            last_game_qb_stats['rushing_attempts'],
            last_game_qb_stats['rushing_yards'],
            last_game_qb_stats['rushing_touchdowns'],
            last_game_qb_stats['rushing_two_point_attempts'],
            last_game_qb_stats['rushing_two_point_made'],
            last_game_qb_stats['fumbles'],
            last_10_games_qb_stats['passing_attempts'],
            last_10_games_qb_stats['passing_yards'],
            last_10_games_yards_per_attempt,
            last_10_games_qb_stats['passing_touchdowns'],
            last_10_games_qb_stats['passing_interceptions'],
            last_10_games_qb_stats['passing_two_point_attempts'],
            last_10_games_qb_stats['passing_two_point_made'],
            last_10_games_qb_stats['rushing_attempts'],
            last_10_games_qb_stats['rushing_yards'],
            last_10_games_qb_stats['rushing_touchdowns'],
            last_10_games_qb_stats['rushing_two_point_attempts'],
            last_10_games_qb_stats['rushing_two_point_made'],
            last_10_games_qb_stats['fumbles'],
            last_game_defense_stats['points_allowed'],
            last_game_defense_stats['passing_yards_allowed'],
            last_game_defense_stats['rushing_yards_allowed'],
            last_game_defense_stats['turnovers'],
            last_10_games_defense_stats['points_allowed'],
            last_10_games_defense_stats['passing_yards_allowed'],
            last_10_games_defense_stats['rushing_yards_allowed'],
            last_10_games_defense_stats['turnovers'],
            fantasy_score(qb_statistics[id][str(year)][str(week)]['passing_yards'],
            qb_statistics[id][str(year)][str(week)]['passing_touchdowns'],
            qb_statistics[id][str(year)][str(week)]['passing_interceptions'],
            qb_statistics[id][str(year)][str(week)]['rushing_yards'],
            qb_statistics[id][str(year)][str(week)]['rushing_touchdowns'],
            qb_statistics[id][str(year)][str(week)]['fumbles'],
            qb_statistics[id][str(year)][str(week)]['rushing_two_point_made'] + qb_statistics[id][str(year)][str(week)]['passing_two_point_made'])
            ]

""" Calculate the fantasy score based on NFL standard rules.
"""
def fantasy_score(passing_yards, passing_touchdowns, interceptions, rushing_yards, rushing_touchdowns, fumbles, two_point):
    score = (
          (float(passing_yards) / 25.0) 
           + (float(passing_touchdowns) * 4.0) 
           - (float(interceptions) * 2.0) 
           + (float(rushing_yards) / 10.0) 
           + (float(rushing_touchdowns) * 6.0) 
           - (float(fumbles) * 2.0) 
           + (float(two_point) * 2.0) 
          )
    """if(breaky == True):
        #pdb.set_trace()"""
    return(-1.0)





# the two lists contain all the fantasy scores
#2010-2016
training_data_scores = []
# 2017
testing_data_scores = []
def retrieve_fantasy_scores_backup(qb_link, qb_name):
    print("Retrieving Fantasy Scores For " + qb_name)
    rk_year = int(player_directory[qb_name + " Rk_Year"])
    start_year = 2010
    if(rk_year > 2010):
        start_year = rk_year

    for year in range(start_year, 2016+1):
        print(year)
        year_link = qb_link + str(year) 
        time.sleep(5)
        request = requests.get(year_link)
        if(request.status_code != 200):
            raise ValueError("Cannot Retreive Stats For: " + year_link)
        soup = BeautifulSoup(request.content, 'html.parser')
        table = soup.find('tbody')
        rows = table.find_all('tr')
        for row in rows:
            # Find all the fantasy scores from 2010-2016 and save them in the global list
            score = float(row.find_all('td')[-3].get_text())
            training_data_scores.append(score)
        print(training_data_scores)

    # testing data
    time.sleep(5)
    request = requests.get(qb_link + str(2017))
    if(request.status_code != 200):
        raise ValueError("Cannot Retreive Stats For: " + year_link)
    soup = BeautifulSoup(request.content, 'html.parser')
    table = soup.find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        # Find all the fantasy scores from 2017 and save them in the other global list
        score = float(row.find_all('td')[-3].get_text())
        testing_data_scores.append(score)
    print(testing_data_scores)

    print("All Scores Retrieved For QB: " + qb_name)
    return


def retrieve_fantasy_scores(qb_name):
    main_link = "https://www.pro-football-reference.com"
    qb_link = player_directory[qb_name]
    request = requests.get(qb_link)
    retrieve_fantasy_scores_backup(qb_link, qb_name)
    return
    """
    if(request != 200):
        retrieve_fantasy_scores_backup(qb_link)
        return
    soup = BeautifulSoup(request.content, 'html.parser')
    body = soup.find('tbody')
    rows = body.find_all('tr')
    # list to store all links [2010-2017]
    year_links = []
    for row in rows:
        # get all the relative year links 
        # (includes all years QB's played, will soon be filtered in next for loop)
        row_data = row.find_all('td')
        year_link = row_data[-1]
        relative_link = year_link.find('a')['href']
        year_links.append(relative_link)

    valid_training_links = []
    for link in year_links:
        # filter links by year for training set, only include if year is in [2010-2016]
        # NOTE: year will always be in this position
        year = link[-5:-1]
        year = int(year)
        if(year==2010 or year==2011 or year==2012 or year==2013 or year==2014 or year==2015 or year==2016):
            valid_training_links.append(link)

    valid_testing_links = []
    for link in year_links:
        # filter links by year for training set, only include if year is 2017
        year = link[-5:-1]
        year = int(year)
        if(year==2017):
            valid_testing_links.append(link)

    """ 
    #TRAINING SET 
    """
    year_links = valid_training_links
    # Combine the main site link with the relative to get full link for each valid year
    year_links = [main_link + link for link in year_links]
    for link in year_links:
        #make new soup object for each link
        time.sleep(7)
        link_request = requests.get(link)
        soup_link = BeautifulSoup(link_request.content, 'html.parser')
        link_table = soup_link.find('tbody')
        table_rows = link_table.find_all('tr')
        for row in table_rows:
            # Find all the fantasy scores from 2010-2016 and save them in the global list
            score = float(row.find_all('td')[-3].get_text())
            training_data_scores.append(score)

    """ 
    #TESTING SET 
    """
    year_links = valid_testing_links
    year_links = [main_link + link for link in year_links]
    for link in year_links:
        time.sleep(7)
        link_request = requests.get(link)
        soup_link = BeautifulSoup(link_request.content, 'html.parser')
        link_table = soup_link.find('tbody')
        table_rows = link_table.find_all('tr')
        for row in table_rows:
            # Find all the fantasy scores from 2017 and save them in the other global list
            score = float(row.find_all('td')[-3].get_text())
            testing_data_scores.append(score)

    print(training_data_scores)
    print(testing_data_scores)
    print("SCORES RETRIEVED")
"""









    
   







    






""" Calculate the average stats of all Rookie QBs in the
observed years.
"""
def rookie_qb_average(qb_statistics):
    games = []
    for qb in qb_statistics.keys():
        """ CHANGED 2015 to 2018 """
        rookie_year = 2017 - qb_statistics[qb]['years_pro'] 
        if(rookie_year >= 2009):
            # data on rookie_year is available
            for week in range(1, 18):
                if(qb_statistics[qb][str(rookie_year)][str(week)]['played']):
                    games.append(qb_statistics[qb][str(rookie_year)][str(week)])
    return(average_qb_stats(games))

""" Create the dataset by determining all rows
"""
breaky = False
def create_all_rows(qb_statistics, defense_statistics, start_year, end_year):
    rows = []
    rookie_qb_stats = rookie_qb_average(qb_statistics)
    # year 2009 should be left such that some previous defense data is available
    for year in range(start_year, end_year):
        for week in range(1, 18):
            for qb in qb_statistics.keys():
                if qb_statistics[qb][str(year)][str(week)]['played']:
                    row = create_row(qb_statistics, defense_statistics, rookie_qb_stats, qb, year, week)
                    # if stats are inconclusive, don't use them
                    # for more information see create_row documentation
                    if row != None:
                        rows.append(row)
    return rows



# player_directory should be global
def make_player_directory():
    main_link_players = "https://www.pro-football-reference.com/players/"
    main_link = "https://www.pro-football-reference.com"
    for ascii_value in range(97, 122+1):
        # Search players by last name (A-Z)
        time.sleep(5)
        print("Retrieving Quarterbacks For Last Initial: " + str(unichr(ascii_value)).upper())
        # letter_link should look like https://www.pro-football-reference.com/players/B/
        letter_link = main_link_players + str(unichr(ascii_value)).upper() + str('/')
        request = requests.get(letter_link)
        print(letter_link)
        soup = BeautifulSoup(request.content, 'html.parser')
        letter_players = (soup.find("div", {"id": "div_players"}))
        Players_Links = [a["href"] for a in letter_players.find_all("a")]
        Players_Names = [a.get_text() for a in letter_players.find_all("a")]
        # Get Player Years and Filter
        paragraph_players = soup.find('div', 'section_content')
        paragraphs = paragraph_players.get_text()
        split_paragraphs = paragraphs.split(" ")
        Players_Years = [] 
        for i in range(len(split_paragraphs)):
            if(str(split_paragraphs[i][0]) == "1" or str(split_paragraphs[i][0]) == "2"):
                rookie_year = int(split_paragraphs[i][:4])
                Players_Years.append(rookie_year)
        Players_Positions = [] 
        for i in range(len(split_paragraphs)):
            if(str(split_paragraphs[i][0]) == "("):
                positions = str(split_paragraphs[i])
                positions = positions.find('Q')
                Players_Positions.append(positions)
        if( (len(Players_Links) != len(Players_Names)) or (len(Players_Links) != len(Players_Positions)) or (len(Players_Names) != len(Players_Years)) ):
            raise ValueError("Mismatch in length of Links, Names, Years, Positions")
        for i in range(0, len(Players_Links)):
            "Combine relative link with actual link and att the fantasy relative link"
            # remove the '.htm' part of the link
            Players_Links[i] = Players_Links[i][:-4]
            # append the fantasy sublink
            Players_Links[i] = (Players_Links[i] + str("/fantasy/"))
            # first part of link is "https://www.pro-football-reference.com" and append previous result
            Players_Links[i] = main_link + Players_Links[i]
        for i in range(0, len(Players_Links)):
            "Fill in the global player directory"
            # Currently doesn't include QB's drafted in 2018
            if( (Players_Positions[i] != -1) and (Players_Years[i] > 1998) ):
                player_directory[str(Players_Names[i])] = str(Players_Links[i])
                player_directory[str(Players_Names[i]) + " Rk_Year"] = str(Players_Years[i])
                print(str(Players_Names[i]))
        print('\n')
    print("Player Directory Generated")
    #pdb.set_trace()


# make player directory
player_directory = {}
make_player_directory()




# save data sets to files
train_data = create_all_rows(fetch_qb_stats(), fetch_defense_stats(), 2010, 2017)
retrieve_fantasy_scores('Drew Brees')
# Add the actual fantasy scores from [2010-2016] for each respective row
i = 0
for row in train_data:
    #pdb.set_trace()
    row[40] = training_data_scores[i]
    i = i + 1
pdb.set_trace() 
np.save('train.npy', np.array(train_data))
train_output = open('train_output.txt', 'w')
train_output.write(str(train_data))
train_output.close()
print('TRAIN DATA STORED')

breaky = True
test_data = create_all_rows(fetch_qb_stats(), fetch_defense_stats(), 2017, 2018)
# TODO: replace the fantasy score in each row  for train and test
# Add the actual fantasy scores from [2017] for each respective row

j = 0
for row in test_data:
    row[40] = testing_data_scores[j]
    j = j + 1
pdb.set_trace() 
test_output = open('test_output.txt', 'w')
test_output.write(str(test_data))
test_output.close()
np.save('test.npy', np.array(test_data))
print('TEST DATA STORED')