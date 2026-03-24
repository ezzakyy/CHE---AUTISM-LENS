import sqlite3
from config import DATABASE_NAME, USERS_TABLE

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()
cursor.execute(f"SELECT * FROM {USERS_TABLE}")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()