"""Authentication and user management backed by Redis."""

from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from backend.config import settings
from backend.redis_client import get_redis_client


AUTH_USERS_KEY = "cluster:auth:users"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hashes a password with a cryptographic salt using SHA-256."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain password against a salt$hash string."""
    try:
        if "$" not in stored_hash:
            return False
        salt, expected_hash = stored_hash.split("$", 1)
        actual_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return secrets.compare_digest(expected_hash, actual_hash)
    except Exception:
        return False


def seed_default_admin() -> None:
    """Ensures default admin user 'wisrovi' exists in Redis on application startup."""
    try:
        client = get_redis_client()
        existing = client.hexists(AUTH_USERS_KEY, settings.DEFAULT_ADMIN_USER)
        if not existing:
            hashed = hash_password(settings.DEFAULT_ADMIN_PASSWORD)
            client.hset(AUTH_USERS_KEY, settings.DEFAULT_ADMIN_USER, hashed)
            print(
                f"[AUTH SEED] Initialized default admin user '{settings.DEFAULT_ADMIN_USER}' "
                f"in Redis key '{AUTH_USERS_KEY}'."
            )
        else:
            print(f"[AUTH SEED] Admin user '{settings.DEFAULT_ADMIN_USER}' already present in Redis.")
    except Exception as e:
        print(f"[AUTH SEED] Warning: Failed to seed admin user to Redis: {e}")


def authenticate_user(username: str, password: str) -> bool:
    """Authenticates username and password against Redis."""
    try:
        client = get_redis_client()
        stored_raw = client.hget(AUTH_USERS_KEY, username)
        if not stored_raw:
            return False
        stored_hash = stored_raw.decode("utf-8")
        return verify_password(password, stored_hash)
    except Exception as e:
        print(f"[AUTH] Error verifying user credentials: {e}")
        return False


def change_user_password(username: str, new_password: str) -> bool:
    """Updates password for a user in Redis."""
    try:
        client = get_redis_client()
        if not client.hexists(AUTH_USERS_KEY, username):
            return False
        new_hash = hash_password(new_password)
        client.hset(AUTH_USERS_KEY, username, new_hash)
        return True
    except Exception as e:
        print(f"[AUTH] Error changing password for {username}: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency to extract and validate the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    client = get_redis_client()
    if not client.hexists(AUTH_USERS_KEY, username):
        raise credentials_exception

    return username
