import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
cursor.execute(create_table)

insert_admin = "INSERT INTO users (id, username, password) VALUES (1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918')"
cursor.execute(insert_admin)

create_table = "CREATE TABLE IF NOT EXISTS flights (flight_id INTEGER PRIMARY KEY AUTOINCREMENT, to_where TEXT, from_where TEXT, date TEXT)"
cursor.execute(create_table)

# create_table = "CREATE TABLE IF NOT EXISTS {} (PNR TEXT UNIQUE, seat_number INTEGER DEFAULT 0, flight_id INTEGER DEFAULT {}, FOREIGN KEY (flight_id) REFERENCES flights(group_id))"
create_table = "CREATE TABLE IF NOT EXISTS tickets (PNR TEXT PRIMARY KEY, seat_number INTEGER DEFAULT 0, to_where TEXT, from_where TEXT, date TEXT, flight_id INTEGER NOT NULL, FOREIGN KEY (flight_id) REFERENCES flights(group_id))"
cursor.execute(create_table)

connection.commit()
connection.close()
