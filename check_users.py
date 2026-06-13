import sqlite3
conn = sqlite3.connect('udaan_v2.db')
c = conn.cursor()
# Check student user
c.execute("SELECT u.id, u.email, u.module_type, p.full_name, p.mobile_number FROM users u LEFT JOIN user_profiles p ON p.user_id=u.id")
rows = c.fetchall()
print("All users with profiles:")
for r in rows:
    print(r)
conn.close()
