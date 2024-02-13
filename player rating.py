import asyncio
import json
import aiohttp
import sqlite3
from understat import Understat


async def main():
  async with aiohttp.ClientSession() as session:
    understat = Understat(session)
    all_players_stats = await understat.get_league_players(
      "epl", 2023,
    )
    return all_players_stats


loop = asyncio.get_event_loop()
all_players_stats = loop.run_until_complete(main())

sql_connection = sqlite3.connect('understat_player_stats.db')
sql_cursor = sql_connection.cursor()

sql_cursor.execute("DROP TABLE IF EXISTS player_stats")
sql_cursor.execute("DROP TABLE IF EXISTS goalkeeper")
sql_cursor.execute("DROP TABLE IF EXISTS defence")
sql_cursor.execute("DROP TABLE IF EXISTS midfield")
sql_cursor.execute("DROP TABLE IF EXISTS forward")

sql_cursor.execute('CREATE TABLE player_stats(id,player_name,games,\
                   minutes,goals,expected_goals,assists,expected_assists,\
                   shots,key_passes,yellow_cards,red_cards,player_position,\
                   team_name,non_penalty_goals,non_penalty_expected_goals,\
                   expected_goals_chain,expected_goals_build_up)')

for i in range(len(all_players_stats)):
  formatted_stats = \
    all_players_stats[i].get('id'), \
    all_players_stats[i].get('player_name').replace("&#039;","'"), \
    all_players_stats[i].get('games'), \
    all_players_stats[i].get('time'), \
    all_players_stats[i].get('goals'), \
    all_players_stats[i].get('xG'), \
    all_players_stats[i].get('assists'), \
    all_players_stats[i].get('xA'), \
    all_players_stats[i].get('shots'), \
    all_players_stats[i].get('key_passes'), \
    all_players_stats[i].get('yellow_cards'), \
    all_players_stats[i].get('red_cards'), \
    all_players_stats[i].get('position'), \
    all_players_stats[i].get('team_title'), \
    all_players_stats[i].get('npg'), \
    all_players_stats[i].get('npxG'), \
    all_players_stats[i].get('xGChain'), \
    all_players_stats[i].get('xGBuildup')
  sql_cursor.execute("INSERT INTO player_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", formatted_stats)
sql_connection.commit()

sql_cursor.execute("ALTER TABLE player_stats ADD player_score")
sql_cursor.execute("UPDATE player_stats SET player_score = goals*7 + assists*10 + minutes/90 + yellow_cards*-2 + red_cards*-15 + non_penalty_goals + expected_goals_build_up*5")
sql_cursor.execute("UPDATE player_stats SET player_score = round(player_score)")      ## FIX (ROUND)
sql_connection.commit()

def create_table(sql_connection,table_name,position,order_by,direction):
  sql_cursor = sql_connection.cursor()
  sql_cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM player_stats WHERE player_position LIKE '%{position}%' ORDER BY {order_by} {direction}")
  sql_connection.commit()
  length = sql_cursor.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
  sorted_player_stats = sql_cursor.execute(f"SELECT player_name,expected_goals_build_up,assists,player_position,player_score FROM {table_name}")
  for i in range(0,length):
    print(sorted_player_stats.fetchone())

# length = sql_cursor.execute(f'SELECT COUNT(*) FROM player_stats').fetchone()[0]
# sorted_player_stats = sql_cursor.execute(f"SELECT player_name,minutes,player_position,player_score FROM player_stats ORDER BY player_score DESC")
# for i in range(0,length):
#   print(sorted_player_stats.fetchone())

# create_table(sql_connection,'goalkeeper','GK','player_score','DESC')
create_table(sql_connection,'defence','D','player_score','DESC')
# create_table(sql_connection,'midfield','M','player_score','DESC')
# create_table(sql_connection,'forward','F','player_score','DESC')

# sql_cursor.execute("DROP TABLE IF EXISTS team")
# create_table(sql_connection,'team','T','player_score','DESC')

# def build_team(sql_connection,table_name):
#   sql_cursor = sql_connection.cursor()
#   pick_complete = False
#   while pick_complete == False:
#     player_chosen = input(f'Choose your {table_name}: ')
#     name_list = sql_cursor.execute(f'SELECT player_name FROM {table_name} WHERE player_name LIKE "%{player_chosen}%"').fetchall()
#     if len(name_list) == 0:
#       print('There is no player in this postition with this name. Make sure the name of the player you want is spelt correctly.')
#     elif len(name_list) > 1:
#       print('There are multiple players with a similar names.')
#       for i in range(0,len(name_list)):
#         print(f'Enter {i+1} for {name_list[i][0]}.')
#       print('Enter (0) to select another player.')
#       player_number = -1
#       while player_number > len(name_list) or player_number < 0:
#         try:
#           player_number = int(input('Please select the number corresponding to the player you want: '))
#         except ValueError:
#           pass
#       if player_number == 0:
#         pass
#       else:
#         player_chosen = name_list[player_number-1][0]
#         pick_complete = True
#     elif len(name_list) == 1:
#       player_chosen = name_list[0][0]
#       pick_complete = True
#     else:
#       print('Unexpected error.')
#     if pick_complete == True:
#       player_check = sql_cursor.execute(f'SELECT COUNT(*) FROM team WHERE player_name LIKE "{player_chosen}"')
#       player_check = player_check.fetchall()[0][0]
#       if player_check != 0:
#         pick_complete = False
#         print(f'{player_chosen} is already in your team. Please choose another player.')
#       else:
#         print(f'{player_chosen} SELECTED')
#         sql_cursor.execute(f'INSERT INTO team SELECT * FROM {table_name} WHERE player_name LIKE "{player_chosen}"')

# sql_cursor.execute('CREATE TABLE user_info(team_name,password,team_score)')


# formation_complete = False
# while formation_complete == False:
#   formation_complete = True
#   formation = input('What formation do you want to choose:\n 4-3-3 (Enter 1)\n 4-4-2 (Enter 2)\n 5-4-1 (Enter 3) ').lower()
#   if formation == '1':
#     number_of_defenders = 4
#     number_of_midfielders = 3
#     number_of_forwards = 3
#   elif formation == '2':
#     number_of_defenders = 4
#     number_of_midfielders = 4
#     number_of_forwards = 2
#   elif formation == '3':
#     number_of_defenders = 5
#     number_of_midfielders = 4
#     number_of_forwards = 1
#   else:
#     formation_complete = False
#     print('Pick a number from 1 to 3 corresponding to the formation you want to select.')

# build_team(sql_connection,'goalkeeper')
# for i in range(0,number_of_defenders):
#   build_team(sql_connection,'defence')
# for i in range(0,number_of_midfielders):
#   build_team(sql_connection,'midfield')
# for i in range(0,number_of_forwards):
#   build_team(sql_connection,'forward')
# sql_connection.commit()

# team = sql_cursor.execute('SELECT * FROM team')
# for i in range(0,11):
#   print(team.fetchone())

# team_score = sql_cursor.execute('SELECT SUM(player_score) FROM team')
# print(team_score.fetchall())