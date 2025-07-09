import sqlite3

conn = sqlite3.connect("habits.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit TEXT NOT NULL
)
""")
cursor.execute()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habit_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_date TEXT NOT NULL,
    habit TEXT NOT NULL
)
""")

conn.commit()
conn.close()

