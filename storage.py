import sqlite3

DB = "data.db"

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  
    return conn

def init():
    # create table if missing 
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, sleep TEXT NOT NULL,
            wake TEXT NOT NULL, quality INTEGER NOT NULL)""")

def load():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM records ORDER BY id").fetchall()
    return [dict(r) for r in rows]

def add(date, sleep, wake, quality):
    # values only via ? 
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO records (date, sleep, wake, quality) VALUES (?, ?, ?, ?)",
            (date, sleep, wake, quality))
        return cur.lastrowid

def delete(item_id):
    with connect() as conn:
        cur = conn.execute("DELETE FROM records WHERE id = ?", (item_id,))
        return cur.rowcount > 0  # true if it existed 