import asyncio
import json
import aiohttp
import sqlite3
from understat import Understat
import re

async def main():
  async with aiohttp.ClientSession() as session:
    understat = Understat(session)
    all_players_stats = await understat.get_league_players(
      "epl", 2023,
    )
    return all_players_stats
  
def clean(text):
    text = re.sub(r' ', '_zzzzzspacezzzzz_', text)
    text = re.sub(r'-', '_zzzzzdashzzzzz_', text)
    text = re.sub(r'[\W]', '', text)
    text = re.sub(r'_zzzzzspacezzzzz_', ' ', text)
    text = re.sub(r'_zzzzzdashzzzzz_', '-', text)
    return text

def create_table(sql_connection,table_name,position,order_by,direction):
  sql_cursor = sql_connection.cursor()
  sql_cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM player_stats WHERE player_position LIKE '%{clean(position)}%' ORDER BY {clean(order_by)} {clean(direction)}")
  sql_connection.commit()
  # length = sql_cursor.execute(f'SELECT COUNT(*) FROM {clean(table_name)}').fetchone()[0]
  # sorted_player_stats = sql_cursor.execute(f"SELECT player_name,player_position,player_score FROM {clean(table_name)}")
  # for i in range(0,length):
  #   print(sorted_player_stats.fetchone())

def create_team(sql_connection,team_name):
  formation_complete = False
  while formation_complete == False:
    formation_complete = True
    formation = input('What formation do you want to choose:\n 4-3-3 (Enter 1)\n 4-4-2 (Enter 2)\n 5-4-1 (Enter 3)\n')
    if formation == '1':
      number_of_defenders = 4
      number_of_midfielders = 3
      number_of_forwards = 3
    elif formation == '2':
      number_of_defenders = 4
      number_of_midfielders = 4
      number_of_forwards = 2
    elif formation == '3':
      number_of_defenders = 5
      number_of_midfielders = 4
      number_of_forwards = 1
    else:
      formation_complete = False
      print('Pick a number from 1 to 3 corresponding to the formation you want to select.\n')
    if formation_complete == True:
      add_player(sql_connection,'goalkeeper',team_name)
      for i in range(0,number_of_defenders):
        add_player(sql_connection,'defence',team_name)
      for i in range(0,number_of_midfielders):
        add_player(sql_connection,'midfield',team_name)
      for i in range(0,number_of_forwards):
        add_player(sql_connection,'forward',team_name)

def add_player(sql_connection,table_name,team_name):
  sql_cursor = sql_connection.cursor()
  pick_complete = False
  while pick_complete == False:
    player_chosen = input(f'Choose your {table_name}: ')
    name_list = sql_cursor.execute(f'SELECT player_name FROM {clean(table_name)} WHERE player_name LIKE "%{clean(player_chosen)}%"').fetchall()
    if len(name_list) == 0:
      print('There is no player in this postition with this name. Make sure the name of the player you want is spelt correctly.')
    elif len(name_list) > 1:
      print('There are multiple players with a similar names.')
      for i in range(0,len(name_list)):
        print(f'Enter {i+1} for {name_list[i][0]}.')
      print('Enter (0) to select another player.')
      player_number = -1
      while player_number > len(name_list) or player_number < 0:
        try:
          player_number = int(input('Please select the number corresponding to the player you want: '))
        except ValueError:
          pass
      if player_number == 0:
        pass
      else:
        player_chosen = name_list[player_number-1][0]
        pick_complete = True
    elif len(name_list) == 1:
      player_chosen = name_list[0][0]
      pick_complete = True
    else:
      print('Unexpected error.')
    if pick_complete == True:
      player_check = sql_cursor.execute(f'SELECT COUNT(*) FROM {clean(team_name)} WHERE player_name LIKE "{clean(player_chosen)}"')
      player_check = player_check.fetchall()[0][0]
      if player_check != 0:
        pick_complete = False
        print(f'{clean(player_chosen)} is already in your team. Please choose another player.')
      else:
        print(f'{clean(player_chosen)} SELECTED')
        sql_cursor.execute(f'INSERT INTO {clean(team_name)} SELECT * FROM {clean(table_name)} WHERE player_name LIKE "{clean(player_chosen)}"')

loop = asyncio.get_event_loop()
all_players_stats = loop.run_until_complete(main())

sql_connection = sqlite3.connect('understat_player_stats.db')
sql_cursor = sql_connection.cursor()

sql_cursor.execute("DROP TABLE IF EXISTS player_stats")
sql_cursor.execute("DROP TABLE IF EXISTS goalkeeper")
sql_cursor.execute("DROP TABLE IF EXISTS defence")
sql_cursor.execute("DROP TABLE IF EXISTS midfield")
sql_cursor.execute("DROP TABLE IF EXISTS forward")

sql_cursor.execute('CREATE TABLE player_stats(id INTEGER,player_name,games INTEGER,\
                   minutes INTEGER,goals INTEGER,expected_goals FLOAT,assists INTEGER,expected_assists FLOAT,\
                   shots INTEGER,key_passes INTEGER,yellow_cards INTEGER,red_cards INTEGER,player_position,\
                   team_name,non_penalty_goals INTEGER,non_penalty_expected_goals FLOAT,\
                   expected_goals_chain FLOAT,expected_goals_build_up FLOAT)')

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
sql_cursor.execute("UPDATE player_stats SET player_score = round(player_score)")
sql_connection.commit()

length = sql_cursor.execute(f'SELECT COUNT(*) FROM player_stats').fetchone()[0]
sorted_player_stats = sql_cursor.execute(f"SELECT player_name,player_position,player_score FROM player_stats ORDER BY player_score DESC")

create_table(sql_connection,'goalkeeper','GK','player_score','DESC')
create_table(sql_connection,'defence','D','player_score','DESC')
create_table(sql_connection,'midfield','M','player_score','DESC')
create_table(sql_connection,'forward','F','player_score','DESC')

sql_cursor.execute('CREATE TABLE IF NOT EXISTS user_info(team_name,password,team_score)')
user_info_pointer = sql_cursor.execute('SELECT * FROM user_info')
user_info = user_info_pointer.fetchall()
print(user_info)

for i in range(len(user_info)):
  sql_cursor.execute(f'UPDATE {clean(user_info[i][0])} SET \
                      games = player_stats.games, \
                      minutes = player_stats.minutes, \
                      goals = player_stats.goals, \
                      expected_goals = player_stats.expected_goals, \
                      assists = player_stats.assists, \
                      expected_assists = player_stats.expected_assists, \
                      shots = player_stats.shots, \
                      key_passes = player_stats.key_passes, \
                      yellow_cards = player_stats.yellow_cards, \
                      red_cards = player_stats.red_cards, \
                      player_position = player_stats.player_position, \
                      team_name = player_stats.team_name, \
                      non_penalty_goals = player_stats.non_penalty_goals, \
                      non_penalty_expected_goals = player_stats.non_penalty_expected_goals, \
                      expected_goals_chain = player_stats.expected_goals_chain, \
                      expected_goals_build_up = player_stats.expected_goals_build_up, \
                      player_score = player_stats.player_score \
                      FROM player_stats WHERE {user_info[i][0]}.player_name = player_stats.player_name')                                                  # update individual player scores
  sql_cursor.execute(f'UPDATE user_info SET team_score = SUM(player_score) FROM {clean(user_info[i][0])} WHERE user_info.team_name = "{clean(user_info[i][0])}"')

print(sql_cursor.execute(f'SELECT * FROM player_stats WHERE player_name IN (SELECT player_name FROM {clean(user_info[0][0])}) ORDER BY goals DESC').fetchall())
print('/n/n/n')
print(sql_cursor.execute(f'SELECT * FROM {clean(user_info[0][0])} ORDER BY goals DESC').fetchall())


user_info_pointer = sql_cursor.execute('SELECT * FROM user_info')
user_info = user_info_pointer.fetchall()
print(user_info)

print("\n\n\033[1mLeaderboard\033[0m")
print(f"\033[4mUsername\033[0m               ""\033[4mTop Score\033[0m")
for i in range(0,len(user_info)):
  print(user_info[i][0].ljust(22),  user_info[i][2])
print("")

login_complete = False
while login_complete == False:
  team_name = re.sub(r' ', '_', input('Enter your team name: '))
  password = input('Enter your password: ')
  team_name_check_pointer = sql_cursor.execute(f'SELECT password,team_score FROM user_info WHERE team_name = "{clean(team_name)}"')
  team_name_check = team_name_check_pointer.fetchall()
  if len(team_name_check) == 0:
    new_team_confirmation = input('Enter Y to confirm you want to create a new team. Or enter any other key to re-enter login details for an existing team: ').lower()
    if new_team_confirmation == 'y':
      if len(team_name) > 20:
        print("Your team name is too long make sure it is a maximum of 20 charaters.\n")
      elif len(team_name) < 3:
        print("Your team name is too short make sure it is a minimum of 3 charaters.\n")
      elif len(password) > 20:
        print("Your password is too long make sure it is a maximum of 20 charaters.\n")
      elif len(password) < 5:
        print("Your password is too short make sure it is a minimum of 5 charaters.\n")
      else:
        sql_cursor.execute("INSERT INTO user_info VALUES(?,?,?)", (team_name,password,0))
        create_table(sql_connection,team_name,'T','player_score','DESC')
        create_team(sql_connection,team_name)
        sql_connection.commit()
        print(f'You have successfuly created a new team called {team_name}.')
        login_complete = True
  elif team_name_check[0][0] == password:
    print(f'You have logged in as {team_name}.')
    login_complete = True
  elif team_name_check[0][0] != password:
    print('Make sure to enter your password correctly. Be careful of capitals.')

print(f'Your team has the following players:')
team = sql_cursor.execute(f'SELECT player_name FROM {team_name}')
for i in range(0,11):
  print(team.fetchone()[0])
team_score = sql_cursor.execute(f'SELECT SUM(player_score) FROM {team_name}')
print(f'Your score is {team_score.fetchall()[0][0]}')
