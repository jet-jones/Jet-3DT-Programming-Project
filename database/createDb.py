
import sqlite3

con = sqlite3.connect("database/database.db")

with open("database/schema.sql") as schema:
    con.executescript(schema.read())