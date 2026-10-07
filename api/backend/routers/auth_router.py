"""Authentication endpoints for Cluster Control."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import (
    authenticate_user,
    change_user_password,
    create_access_token,
    get_current_user,
)
from backend.config import settings
from backend.schemas import (
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Logs in with username and password, validating against Redis credentials."""
    authenticated = authenticate_user(payload.username, payload.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": payload.username},
        expires_delta=access_token_expires,
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=payload.username,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    """Returns currently authenticated user."""
    return UserResponse(username=current_user, authenticated=True)


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user: str = Depends(get_current_user),
):
    """Changes password for the currently logged-in user."""
    # First verify current password
    if not authenticate_user(current_user, payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed",
        )

    success = change_user_password(current_user, payload.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password in Redis",
        )
    return {"status": "success", "message": "Password updated successfully"}
