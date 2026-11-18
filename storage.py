import os
import sqlite3
from datetime import datetime

from models import SleepRecord, DEFAULT_FACTOR


def connect():
    # path is read on every call, so tests can use a temporary database
    conn = sqlite3.connect(os.environ.get("DB_PATH", "data.db"))
    conn.row_factory = sqlite3.Row
    # without this SQLite does not check links between tables
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init():
    # create tables if missing 
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, sleep TEXT NOT NULL,
            wake TEXT NOT NULL, quality INTEGER NOT NULL,
            factor_id INTEGER NOT NULL REFERENCES factors(id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            action TEXT NOT NULL,
            item_id INTEGER,
            details TEXT)""")
        conn.execute("INSERT OR IGNORE INTO factors (name) VALUES (?)", (DEFAULT_FACTOR,))
        # old database from lab 10 has no factor_id: it must be migrated first
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(records)")]
        if "factor_id" not in columns:
            raise RuntimeError("old database format: run 'py migrate.py' first")


def _get_or_create_factor(conn, name):
    """Return id of the factor, create it if it is new."""
    conn.execute("INSERT OR IGNORE INTO factors (name) VALUES (?)", (name,))
    return conn.execute("SELECT id FROM factors WHERE name = ?", (name,)).fetchone()["id"]


def _log(conn, action, item_id, details):
    """Write one line to the audit log."""
    conn.execute(
        "INSERT INTO audit_log (ts, action, item_id, details) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), action, item_id, details))


def load():
    """All records as SleepRecord objects, factor name comes from JOIN."""
    with connect() as conn:
        rows = conn.execute(
            """SELECT r.id, r.date, r.sleep, r.wake, r.quality, f.name AS factor
               FROM records r JOIN factors f ON f.id = r.factor_id
               ORDER BY r.id""").fetchall()
    return [SleepRecord.from_row(r) for r in rows]


def add(record):
    """Save a SleepRecord, return its new id."""
    # values only via ? 
    with connect() as conn:
        factor_id = _get_or_create_factor(conn, record.factor)
        cur = conn.execute(
            "INSERT INTO records (date, sleep, wake, quality, factor_id) VALUES (?, ?, ?, ?, ?)",
            (record.date, record.sleep, record.wake, record.quality, factor_id))
        new_id = cur.lastrowid
        _log(conn, "add", new_id,
             f"{record.date} {record.sleep}-{record.wake}, quality {record.quality}, "
             f"factor {record.factor}")
        return new_id


def delete(item_id):
    """Delete a record by id, return True if it existed."""
    with connect() as conn:
        row = conn.execute("SELECT date FROM records WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            return False
        conn.execute("DELETE FROM records WHERE id = ?", (item_id,))
        _log(conn, "delete", item_id, f"date {row['date']}")
        return True


def factor_report():
    """Report with JOIN: nights and average quality per factor."""
    with connect() as conn:
        rows = conn.execute(
            """SELECT f.name AS factor, COUNT(*) AS nights,
                      ROUND(AVG(r.quality), 1) AS avg_quality
               FROM records r JOIN factors f ON f.id = r.factor_id
               GROUP BY f.id
               ORDER BY avg_quality DESC, f.name""").fetchall()
    return [dict(r) for r in rows]


def load_log(limit=50):
    """Last lines of the audit log, newest first."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, ts, action, item_id, details FROM audit_log ORDER BY id DESC LIMIT ?",
            (limit,)).fetchall()
    return [dict(r) for r in rows]
