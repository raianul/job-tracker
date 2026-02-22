"""Security (JWT) unit tests."""
import pytest

from app.core.security import create_access_token, decode_access_token


def test_create_and_decode_access_token_roundtrip() -> None:
    payload = {"sub": "42", "extra": "data"}
    token = create_access_token(data=payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["extra"] == "data"
    assert "exp" in decoded


def test_decode_access_token_invalid_returns_none() -> None:
    assert decode_access_token("invalid.jwt.token") is None
    assert decode_access_token("") is None
    assert decode_access_token("not-even-dots") is None
