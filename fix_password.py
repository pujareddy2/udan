from app.core.db import engine
from sqlmodel import Session, select, update
from app.models.domain import User
import bcrypt

password = '123456'
# Create proper bcrypt hash
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

print(f'New hash for password "123456": {hashed}')

# Update the database
session = Session(engine)
statement = update(User).where(User.email == 'job@gmail.com').values(password_hash=hashed)
session.exec(statement)
session.commit()
print('Password updated successfully in database')

# Verify it was updated
user = session.exec(select(User).where(User.email == 'job@gmail.com')).first()
print(f'Updated user password hash: {user.password_hash}')

# Test login verification
from app.api.routers.auth import verify_password
result = verify_password(password, user.password_hash)
print(f'Login verification test: {result}')

session.close()
