import sqlite3

conn = sqlite3.connect('udaan_v2.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]

for table in sorted(tables):
    try:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        if count > 0:
            print(f"Table: {table:35} | Rows: {count}")
    except Exception as e:
        print(f"Error reading {table}: {e}")

conn.close()
