import datetime
import pathlib
import sqlite3

# Create the backups folder if needed 
pathlib.Path("backups").mkdir(exist_ok=True)

src = sqlite3.connect("data.db")
dst = sqlite3.connect(f"backups/data-{datetime.date.today()}.db")
# Safe online copy of a working database 
src.backup(dst)
dst.close()
src.close()
print("backup done")
