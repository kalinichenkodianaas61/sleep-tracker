"""One-time migration of data.db from lab 10 to lab 11 format.

Before: records(id, date, sleep, wake, quality)
After:  factors(id, name) + records(..., factor_id) + audit_log
Old records get the default factor. Run once: py migrate.py
"""
import datetime
import os
import pathlib
import shutil
import sqlite3

from models import DEFAULT_FACTOR

DB = os.environ.get("DB_PATH", "data.db")


def main():
    if not os.path.exists(DB):
        print("no database found, nothing to migrate")
        return

    conn = sqlite3.connect(DB)
    conn.isolation_level = None  # we control the transaction ourselves 
    columns = [row[1] for row in conn.execute("PRAGMA table_info(records)")]
    if not columns:
        print("no records table, nothing to migrate")
        return
    if "factor_id" in columns:
        print("already migrated, nothing to do")
        return

    # backup first 
    pathlib.Path("backups").mkdir(exist_ok=True)
    backup_path = f"backups/before-lab11-{datetime.date.today()}.db"
    shutil.copyfile(DB, backup_path)
    print("backup saved:", backup_path)

    before = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    conn.execute("BEGIN")
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE)""")
        conn.execute("INSERT OR IGNORE INTO factors (name) VALUES (?)", (DEFAULT_FACTOR,))
        conn.execute("ALTER TABLE records RENAME TO records_old")
        conn.execute("""CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, sleep TEXT NOT NULL,
            wake TEXT NOT NULL, quality INTEGER NOT NULL,
            factor_id INTEGER NOT NULL REFERENCES factors(id))""")
        conn.execute(
            """INSERT INTO records (id, date, sleep, wake, quality, factor_id)
               SELECT id, date, sleep, wake, quality,
                      (SELECT id FROM factors WHERE name = ?)
               FROM records_old""", (DEFAULT_FACTOR,))
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            action TEXT NOT NULL,
            item_id INTEGER,
            details TEXT)""")
        after = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        if after != before:
            raise RuntimeError(f"records lost: was {before}, now {after}")
        conn.execute("DROP TABLE records_old")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")  # nothing is changed if something went wrong 
        raise
    print(f"migrated {after} records, none lost")


if __name__ == "__main__":
    main()
