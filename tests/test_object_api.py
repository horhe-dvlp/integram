import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status

from app.api import objects
from app.middleware import auth_middleware
from app.db import db
from app.models.objects import ObjectCreateRequest


@pytest.mark.asyncio
async def test_post_object_success(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1, "role":"admin"}))
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (777, "1")
    mock_conn = AsyncMock()
    mock_conn.__aenter__.return_value.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn
    monkeypatch.setattr(objects, "engine", mock_engine)
    monkeypatch.setattr(db, "engine", mock_engine)

    resp = await objects.create_object(ObjectCreateRequest(id=110, up=1, attrs={"t110":"Name"}), db_name="testdb")
    assert resp.status_code == status.HTTP_200_OK
    import json
    data = json.loads(resp.body)
    assert data["id"] == 777

@pytest.mark.asyncio
async def test_post_object_warning(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1, "role":"admin"}))
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (555, "warn_record_exists")
    mock_conn = AsyncMock()
    mock_conn.__aenter__.return_value.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn
    monkeypatch.setattr(objects, "engine", mock_engine)
    monkeypatch.setattr(db, "engine", mock_engine)

    resp = await objects.create_object(ObjectCreateRequest(id=110, up=1, attrs={"t110":"Another"}), db_name="testdb")
    assert isinstance(resp, objects.ObjectCreateResponse)
    assert resp.warning == "Record already exists"


def test_object_create_request_validation():
    with pytest.raises(ValueError):
        ObjectCreateRequest(id=1, up=1, attrs={})
