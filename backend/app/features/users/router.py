"""Users API router."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.users.schemas import UserCreate, UserResponse, UserUpdate
from app.features.users.service import UserService
from app.features.auth.dependencies import require_admin, get_current_user
from app.features.users.models import User

# Users can only be managed by admins, so we require admin for most routes
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (Admin only)."""
    return UserService.create(db, user_in)


@router.get("", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (Admin only)."""
    return UserService.get_all(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get user by ID (Admin only)."""
    return UserService.get_by_id(db, id)


@router.patch("/{id}", response_model=UserResponse)
def update_user(
    id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user (Admin only)."""
    return UserService.update(db, id, user_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user (Admin only)."""
    UserService.delete(db, id)
