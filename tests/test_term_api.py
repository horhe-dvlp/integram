import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status

from app.api import terms
from app.middleware import auth_middleware
from app.db import db

MOCKED_TERM = {
    "id": 64,
    "up": 0,
    "base": 3,
    "obj": "Пользователь",
    "uniq": 1,
    "req_id": None,
    "req_t": None,
    "req_val": None,
    "ref_val": None,
    "default_val": None,
    "mods": None,
    "attrs": None,
    "ref_id": None,
    "ord": None,
}


def setup_engine_mock(rows):
    mock_engine = MagicMock()
    mock_conn = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = rows
    mock_conn.__aenter__.return_value.execute.return_value = mock_result
    mock_engine.connect.return_value = mock_conn
    mock_engine.begin.return_value = mock_conn
    return mock_engine

@pytest.mark.asyncio
async def test_get_all_terms(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1,"role":"admin"}))
    monkeypatch.setattr(terms, "engine", setup_engine_mock([MOCKED_TERM]))
    monkeypatch.setattr(db, "engine", setup_engine_mock([MOCKED_TERM]))
    resp = await terms.get_all_terms(db_name="testdb")
    assert resp.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_term_by_id(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1,"role":"admin"}))
    monkeypatch.setattr(terms, "engine", setup_engine_mock([MOCKED_TERM]))
    monkeypatch.setattr(db, "engine", setup_engine_mock([MOCKED_TERM]))
    resp = await terms.get_term(term_id=64, db_name="testdb")
    assert resp.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_term_by_id_not_found(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1,"role":"admin"}))
    monkeypatch.setattr(terms, "engine", setup_engine_mock([]))
    monkeypatch.setattr(db, "engine", setup_engine_mock([]))
    with pytest.raises(Exception):
        await terms.get_term(term_id=999, db_name="testdb")

@pytest.mark.asyncio
async def test_create_term_warning(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1,"role":"admin"}))
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (42, "warn_term_exists")
    mock_conn = AsyncMock()
    mock_conn.__aenter__.return_value.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn
    monkeypatch.setattr(terms, "engine", mock_engine)
    monkeypatch.setattr(db, "engine", mock_engine)
    payload = terms.TermCreateRequest(val="Test", t=3, mods={})
    resp = await terms.create_term(payload, db_name="testdb")
    assert resp.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_post_term_mocked(monkeypatch):
    monkeypatch.setattr(auth_middleware, "verify_token", AsyncMock(return_value={"user_id":1,"role":"admin"}))
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (123, "1")
    mock_conn = AsyncMock()
    mock_conn.__aenter__.return_value.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn
    monkeypatch.setattr(terms, "engine", mock_engine)
    monkeypatch.setattr(db, "engine", mock_engine)
    payload = terms.TermCreateRequest(val="Оператор", t=3, mods={"UNIQUE":"", "ALIAS":"Operator"})
    resp = await terms.create_term(payload, db_name="testdb")
    assert resp.status_code == status.HTTP_200_OK
