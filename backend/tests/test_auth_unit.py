"""Unit tests for auth utilities — password hashing and JWT."""

import pytest

from app.modules.auth.password import hash_password, verify_password
from app.modules.auth.jwt import create_access_token, decode_token


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_hash_starts_with_bcrypt_prefix(self):
        hashed = hash_password("password123")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password_returns_true(self):
        hashed = hash_password("secure123")
        assert verify_password("secure123", hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = hash_password("secure123")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_empty_password_returns_false(self):
        hashed = hash_password("secure123")
        assert verify_password("", hashed) is False

    def test_same_password_produces_unique_hashes(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2

    def test_both_unique_hashes_verify_correctly(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert verify_password("password", h1) is True
        assert verify_password("password", h2) is True

    def test_case_sensitive(self):
        hashed = hash_password("Password")
        assert verify_password("password", hashed) is False
        assert verify_password("Password", hashed) is True


class TestJWT:
    def test_round_trip_user(self):
        token = create_access_token("user-123", "user")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "user"

    def test_round_trip_admin(self):
        token = create_access_token("admin-001", "admin")
        payload = decode_token(token)
        assert payload["sub"] == "admin-001"
        assert payload["role"] == "admin"

    def test_token_contains_exp_claim(self):
        token = create_access_token("user-123", "user")
        payload = decode_token(token)
        assert "exp" in payload

    def test_invalid_token_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_token("not.a.valid.token")

    def test_empty_token_raises_value_error(self):
        with pytest.raises(ValueError):
            decode_token("")

    def test_tampered_signature_raises_value_error(self):
        token = create_access_token("user-123", "user")
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.invalidsignature"
        with pytest.raises(ValueError):
            decode_token(tampered)

    def test_different_users_get_different_tokens(self):
        t1 = create_access_token("user-1", "user")
        t2 = create_access_token("user-2", "user")
        assert t1 != t2
