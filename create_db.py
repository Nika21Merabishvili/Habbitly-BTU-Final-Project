import sqlite3

# Connect or create the database file
conn = sqlite3.connect("habits.db")
cursor = conn.cursor()

# Main habits table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit TEXT NOT NULL,
        created_date TEXT NOT NULL DEFAULT (date('now')),
        deleted_date TEXT DEFAULT NULL
    )
''')

# Habit completion tracking table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS habit_dates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_date TEXT NOT NULL,
        habit_id INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits(id),
        UNIQUE(habit_date, habit_id)
    )
''')

conn.commit()
conn.close()
