import sqlite3

sql_connection = sqlite3.connect('sql_database.db')
sql_cursor = sql_connection.cursor()
sql_cursor.execute("DROP TABLE IF EXISTS users")

sql_cursor.execute('CREATE TABLE users (username varchar(30) ,admin boolean)')
sql_cursor.execute('INSERT INTO users (username, admin) VALUES ("ran", True),("haki", False)')
test = sql_cursor.execute('SELECT * FROM users')

sql_cursor.execute('SELECT COUNT(*) FROM users')
result = sql_cursor.fetchone()

# BAD EXAMPLE. DON'T DO THIS!
def is_admin(username: str) -> bool:
    sql_cursor.execute("""
        SELECT
            admin
        FROM
            users
        WHERE
            username = '%s'
    """ % username)
    result = sql_cursor.fetchone()

    if result is None:
        return 0

    admin, = result
    return admin

# print(sql_cursor.execute('SELECT True').fetchone())
# SAFE EXAMPLES. DO THIS!
username = 'ran'
sql_cursor.execute("SELECT admin FROM users WHERE username = ?", (username, ));
print(sql_cursor.fetchone())
