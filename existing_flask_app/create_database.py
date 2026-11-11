import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS queries (

    query_id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_name TEXT,

    query_text TEXT,

    category TEXT,

    priority TEXT,

    assigned_team TEXT,

    recommendation TEXT,

    confidence_score INTEGER,

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
''')

conn.commit()

conn.close()

print("Database Created Successfully")