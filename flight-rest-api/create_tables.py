import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
cursor.execute(create_table)

insert_admin = "INSERT INTO users (id, username, password) VALUES (1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918')"
cursor.execute(insert_admin)

create_table = "CREATE TABLE IF NOT EXISTS flights (dest TEXT, from TEXT, date TEXT, flight_id INTEGER )"
cursor.execute(create_table)

connection.commit()
connection.close()
