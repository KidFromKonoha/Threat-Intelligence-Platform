"""Auth service."""

from datetime import datetime, timezone
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.features.auth.schemas import Token
from app.features.auth.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.features.users.models import User
from app.features.users.service import UserService

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User:
        user = UserService.get_by_username(db, username)
        if not user:
            logger.warning(f"Failed login attempt for unknown user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
            
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        
        logger.info(f"Successful login for user: {username}")
        return user

    @staticmethod
    def create_tokens(user: User) -> Token:
        access_token = create_access_token(subject=user.username, role=user.role)
        refresh_token = create_refresh_token(subject=user.username, role=user.role)
        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode_token(refresh_token)
            username: str | None = payload.get("sub")
            token_type: str | None = payload.get("type")
            if username is None or token_type != "refresh":
                logger.warning("Invalid refresh token attempt")
                raise credentials_exception
        except JWTError:
            logger.warning("Invalid refresh token attempt")
            raise credentials_exception
            
        user = UserService.get_by_username(db, username=username)
        if user is None or not user.is_active:
            raise credentials_exception
            
        logger.info(f"Refresh token used by user: {username}")
        return AuthService.create_tokens(user)
