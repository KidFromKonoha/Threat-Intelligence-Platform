"""Auth router."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.auth.schemas import Token, RefreshTokenRequest
from app.features.auth.service import AuthService
from app.features.auth.dependencies import get_current_user
from app.features.users.models import User
from app.features.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate and obtain access and refresh tokens."""
    user = AuthService.authenticate(db, form_data.username, form_data.password)
    return AuthService.create_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh an access token using a refresh token."""
    return AuthService.refresh_tokens(db, request.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get the currently logged in user."""
    return current_user
