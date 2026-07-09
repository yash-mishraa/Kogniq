"""Tests for the database foundation module."""

from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from apps.api.app.config import APISettings
from apps.api.app.db.base import Base, TimestampMixin, UUIDMixin
from apps.api.app.db.engine import get_engine, get_session_factory
from apps.api.app.db.health import check_database_health
from apps.api.app.db.repositories.base import BaseRepository, SQLAlchemyRepository
from apps.api.app.db.unit_of_work import SQLAlchemyUnitOfWork, UnitOfWork


def test_database_url_generation() -> None:
    settings = APISettings(
        postgres_host="test-host",
        postgres_port=5432,
        postgres_db="test-db",
        postgres_user="test-user",
        postgres_password="test-password",
    )
    url = str(settings.database_url)
    assert url == "postgresql+asyncpg://test-user:test-password@test-host:5432/test-db"


def test_engine_and_session_factory_creation() -> None:
    settings = APISettings()
    engine = get_engine(settings)
    assert isinstance(engine, AsyncEngine)

    session_factory = get_session_factory(engine)
    assert isinstance(session_factory, async_sessionmaker)


@pytest.mark.asyncio
async def test_database_health_check_success(mocker: Any) -> None:
    """Test that check_database_health returns True when query succeeds."""
    mock_engine = mocker.AsyncMock(spec=AsyncEngine)
    mock_conn = mocker.AsyncMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn

    result = await check_database_health(mock_engine)
    assert result is True
    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_database_health_check_failure(mocker: Any) -> None:
    """Test that check_database_health returns False when query fails."""
    mock_engine = mocker.AsyncMock(spec=AsyncEngine)
    mock_conn = mocker.AsyncMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn
    mock_conn.execute.side_effect = Exception("Connection refused")

    result = await check_database_health(mock_engine)
    assert result is False


def test_base_abstractions_exist() -> None:
    """Verify abstract classes exist and are properly structured."""
    assert issubclass(SQLAlchemyRepository, BaseRepository)
    assert issubclass(SQLAlchemyUnitOfWork, UnitOfWork)


def test_base_mixins_exist() -> None:
    """Verify SQLAlchemy base structures exist."""

    class DummyModel(Base, UUIDMixin, TimestampMixin):
        __tablename__ = "dummy"

    assert hasattr(DummyModel, "id")
    assert hasattr(DummyModel, "created_at")
    assert hasattr(DummyModel, "updated_at")
