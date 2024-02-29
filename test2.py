import sqlite3
sql_connection = sqlite3.connect('understat_player_stats.db')
sql_cursor = sql_connection.cursor()

sql_cursor.execute("""
    DECLARE @count INT;
    SET @count = 1;
        
    WHILE @count<= 5
    BEGIN
    PRINT @count
    SET @count = @count + 1;
    END;
""")