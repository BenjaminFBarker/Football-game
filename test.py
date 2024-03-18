# import re

# def clean(text):
#     text = re.sub(r' ', '_zzzzzspacezzzzz_', text)
#     text = re.sub(r'-', '_zzzzzdashzzzzz_', text)
#     text = re.sub(r'[\W]', '', text)
#     text = re.sub(r'_zzzzzspacezzzzz_', ' ', text)
#     text = re.sub(r'_zzzzzdashzzzzz_', '-', text)
#     return text

# dirty_text = input("Give me some text to clean: ")
# print(clean(dirty_text))

import sqlite3

sql_connection = sqlite3.connect('sql_database.db')
sql_cursor = sql_connection.cursor()
print(sql_cursor.execute("SELECT cast(210.0 as integer)").fetchall())
print(sql_cursor.execute("SELECT cast(209.4 as integer)").fetchall())
print(sql_cursor.execute("SELECT cast(round(209.5,0) as integer)").fetchall())
print(sql_cursor.execute("SELECT cast(209.0 as integer)").fetchall())
print(sql_cursor.execute("SELECT cast(210 as integer)").fetchall())