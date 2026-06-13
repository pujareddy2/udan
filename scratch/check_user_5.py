import sqlite3

conn = sqlite3.connect('udaan_v2.db')
c = conn.cursor()

c.execute("SELECT DISTINCT module FROM opportunities")
print("Modules in opportunities:", c.fetchall())

c.execute("SELECT id, title, benefit_value, module FROM opportunities LIMIT 10")
print("First 10 opportunities:", c.fetchall())

conn.close()
