import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.api import health


@pytest.mark.asyncio
async def test_health_check_ok(monkeypatch):
    mock_conn = AsyncMock()
    mock_conn.__aenter__.return_value.execute.return_value = None
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    monkeypatch.setattr(health, "engine", mock_engine)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.json()["db"] == "connected"


@pytest.mark.asyncio
async def test_health_check_fail(monkeypatch):
    mock_conn = AsyncMock()
    mock_conn.__aenter__.side_effect = Exception("db fail")
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    monkeypatch.setattr(health, "engine", mock_engine)

    result = await health.check_database_connection()
    assert result.status == "error"
