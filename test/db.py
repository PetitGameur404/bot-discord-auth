import sqlite3

db = sqlite3.connect("db.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT NOT NULL,
    nom TEXT NOT NULL,
    mail TEXT UNIQUE NOT NULL,
    code TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute(
    "INSERT OR IGNORE INTO users (prenom, nom, mail) VALUES (?, ?, ?)",
    ("Jean", "Daniel", "jean@gmail.com"),
)

db.commit()
db.close()