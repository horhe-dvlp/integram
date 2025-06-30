import pytest
from fastapi import HTTPException
from app.auth.auth import verify_token


def test_verify_token_success():
    data = verify_token("Bearer secret-token")
    assert data["role"] == "admin"


def test_verify_token_missing():
    with pytest.raises(HTTPException) as exc:
        verify_token("")
    assert exc.value.status_code == 401


def test_verify_token_invalid():
    with pytest.raises(HTTPException) as exc:
        verify_token("Bearer wrong")
    assert exc.value.status_code == 403
