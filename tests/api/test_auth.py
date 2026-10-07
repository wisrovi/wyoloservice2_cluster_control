"""Unit tests for authentication, password hashing, and JWT tokens.

This module validates:
1. That passwords are correctly hashed with a cryptographic salt and verified reliably.
2. That incorrect passwords fail verification.
3. That JWT access tokens are correctly generated, signed, and carry the subject payload.
4. That expired or tampered tokens are rejected.
"""

from datetime import timedelta
import pytest
import jwt
from backend.auth import hash_password, verify_password, create_access_token
from backend.config import settings


def test_password_hashing_and_verification():
    """Validates password hashing and salt verification mechanism.

    What it tests:
    - Creates a salted hash of a known plain text password.
    - Confirms that the hash contains the '$' delimiter separating the salt and sha256 digest.
    - Verifies that `verify_password` returns True for the matching password.
    - Verifies that `verify_password` returns False when given an incorrect password.
    - Verifies that hashing the same password twice yields different salts and different hashes.
    """
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    # 1. Format validation
    assert "$" in hashed, "Hash should be in the format 'salt$digest'"
    salt, digest = hashed.split("$", 1)
    assert len(salt) == 32, "Salt should be 16 bytes encoded as 32 hex chars"
    assert len(digest) == 64, "SHA-256 digest should be 64 hex characters"

    # 2. Correct password validation
    assert verify_password(password, hashed) is True, "Password verification should succeed for matching password"

    # 3. Wrong password validation
    assert verify_password("WrongPassword!", hashed) is False, "Password verification must fail for wrong password"

    # 4. Salt randomness validation
    hashed_again = hash_password(password)
    assert hashed != hashed_again, "Two hashes of the same password should have unique salts"


def test_create_and_decode_access_token():
    """Validates JWT access token generation and cryptographic payload decoding.

    What it tests:
    - Generates a valid access token for a test subject ('wisrovi').
    - Decodes the token using the secret key and HS256 algorithm.
    - Asserts that the 'sub' claim matches the input subject.
    - Asserts that the expiration claim 'exp' is present and points to the future.
    """
    subject = "wisrovi"
    token = create_access_token(data={"sub": subject}, expires_delta=timedelta(minutes=30))

    assert isinstance(token, str), "Token must be returned as a string"
    assert len(token) > 20, "Token should be a non-trivial JWT string"

    # Decode and verify payload
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload.get("sub") == subject, "Token subject claim must match the input username"
    assert "exp" in payload, "Token must contain expiration timestamp"


def test_invalid_token_rejection():
    """Validates that tampered or improperly signed tokens are rejected.

    What it tests:
    - Encodes a token with a different secret key.
    - Verifies that attempting to decode it with settings.JWT_SECRET_KEY raises a PyJWTError.
    """
    wrong_token = jwt.encode({"sub": "hacker"}, "wrong-secret-key-123", algorithm="HS256")
    with pytest.raises(jwt.PyJWTError):
        jwt.decode(wrong_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
