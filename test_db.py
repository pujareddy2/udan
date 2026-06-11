import sqlite3

conn = sqlite3.connect("data/udaan.db")

cursor = conn.cursor()

cursor.execute("""
SELECT module_type, COUNT(*)
FROM opportunities
GROUP BY module_type;
""")

print(cursor.fetchone())

conn.close()