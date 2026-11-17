"""Tests for security utilities."""
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Test bcrypt password hashing."""

    def test_hash_and_verify(self):
        """Should hash and then verify correctly."""
        password = "MySecureP@ss123"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password(self):
        """Should reject wrong passwords."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes(self):
        """Same password should produce different hashes (salt)."""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_and_decode(self):
        """Should create a token and decode it."""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"

    def test_invalid_token(self):
        """Should return None for invalid tokens."""
        result = decode_access_token("invalid.token.here")
        assert result is None

    def test_token_contains_expiry(self):
        """Token should contain expiry claim."""
        token = create_access_token({"sub": "user-123"})
        decoded = decode_access_token(token)
        assert "exp" in decoded
