"""Users service."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.users.models import User
from app.features.users.schemas import UserCreate, UserUpdate
from app.features.auth.security import get_password_hash


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()
        
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: UserCreate) -> User:
        if UserService.get_by_username(db, obj_in.username):
            raise HTTPException(status_code=409, detail="Username already exists")
            
        existing_email = db.query(User).filter(User.email == obj_in.email).first()
        if existing_email:
            raise HTTPException(status_code=409, detail="Email already exists")
            
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, user_id: str, obj_in: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
            
        if "username" in update_data and update_data["username"] != user.username:
            if UserService.get_by_username(db, update_data["username"]):
                raise HTTPException(status_code=409, detail="Username already exists")
                
        if "email" in update_data and update_data["email"] != user.email:
            if db.query(User).filter(User.email == update_data["email"]).first():
                raise HTTPException(status_code=409, detail="Email already exists")
                
        for field, value in update_data.items():
            setattr(user, field, value)
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: str) -> None:
        user = UserService.get_by_id(db, user_id)
        db.delete(user)
        db.commit()
