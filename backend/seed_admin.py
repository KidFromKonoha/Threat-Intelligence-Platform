import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.features.users.models import User
from app.features.auth.security import get_password_hash

db = SessionLocal()
if not db.query(User).filter(User.username == "admin").first():
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Admin user created.")
else:
    print("Admin user already exists.")
