import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.features.users.models import User
from app.features.auth.security import get_password_hash

def seed_roles():
    db = SessionLocal()
    roles = ["analyst", "executive"]
    
    for role in roles:
        if not db.query(User).filter(User.username == role).first():
            user = User(
                username=role,
                email=f"{role}@example.com",
                password_hash=get_password_hash("password123"),
                role=role,
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"{role.capitalize()} user created.")
        else:
            print(f"{role.capitalize()} user already exists.")

if __name__ == "__main__":
    seed_roles()
