import sqlite3
conn = sqlite3.connect('udaan_v2.db')
c = conn.cursor()
c.execute("SELECT id, email, password_hash, module_type FROM users WHERE email='job@gmail.com'")
rows = c.fetchall()
print("job@gmail.com user:", rows)

c.execute("SELECT id, email, password_hash, module_type FROM users LIMIT 5")
print("All users (first 5):", c.fetchall())

# Check profile status endpoint 
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())
conn.close()
