# webapp/init_db.py

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT,
    image_path TEXT,
    status TEXT DEFAULT 'pending'
)
''')

conn.commit()
conn.close()

print("✅ Database initialized at", db_path)
