"""
Starter conftest.py -- common fixtures for pytest.

Usage:
    Place this file at the root of your tests/ directory.
    pytest automatically discovers conftest.py and makes its fixtures
    available to all tests in the same directory and below.
"""

import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# If using FastAPI + httpx:
# from httpx import ASGITransport, AsyncClient
# from app.main import app

# If using SQLAlchemy:
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker
# from app.models import Base
# ---------------------------------------------------------------------------


# ==========================================================================
# Environment Variables
# ==========================================================================


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set safe default environment variables for all tests.

    autouse=True ensures this runs for every test automatically.
    monkeypatch restores original values after each test.
    """
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("SECRET_KEY", "test-secret-not-for-production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    # Remove any production secrets that should never leak into tests.
    monkeypatch.delenv("PRODUCTION_API_KEY", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)


# ==========================================================================
# Temporary Directory
# ==========================================================================


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory with input/output subdirectories."""
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    return tmp_path


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample text file for testing file operations."""
    f = tmp_path / "sample.txt"
    f.write_text("line 1\nline 2\nline 3\n")
    return f


# ==========================================================================
# Database Session (SQLAlchemy)
# ==========================================================================

# Uncomment this section if using SQLAlchemy.

# TEST_DATABASE_URL = os.getenv(
#     "TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_db"
# )
#
#
# @pytest.fixture(scope="session")
# def engine():
#     """Create database engine for the entire test session."""
#     eng = create_engine(TEST_DATABASE_URL)
#     yield eng
#     eng.dispose()
#
#
# @pytest.fixture(scope="session")
# def tables(engine):
#     """Create tables at start of session, drop at end."""
#     Base.metadata.create_all(engine)
#     yield
#     Base.metadata.drop_all(engine)
#
#
# @pytest.fixture
# def db_session(engine, tables) -> Generator[Session, None, None]:
#     """Transactional database session -- rolls back after each test."""
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = sessionmaker(bind=connection)()
#
#     yield session
#
#     session.close()
#     transaction.rollback()
#     connection.close()


# ==========================================================================
# HTTP Test Client (FastAPI)
# ==========================================================================

# Uncomment this section if using FastAPI.

# @pytest.fixture
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     """Async HTTP client for testing API endpoints."""
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as c:
#         yield c
#
#
# @pytest.fixture
# def auth_headers() -> dict[str, str]:
#     """Authorization headers with a test JWT token."""
#     from app.auth import create_access_token
#     token = create_access_token(data={"sub": "test-user", "role": "admin"})
#     return {"Authorization": f"Bearer {token}"}
#
#
# @pytest.fixture
# async def auth_client(auth_headers) -> AsyncGenerator[AsyncClient, None]:
#     """Authenticated async HTTP client."""
#     transport = ASGITransport(app=app)
#     async with AsyncClient(
#         transport=transport, base_url="http://test", headers=auth_headers
#     ) as c:
#         yield c


# ==========================================================================
# Mock External Services
# ==========================================================================


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Generic mock HTTP client with default 200/201 responses."""
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"status": "ok"},
    )
    client.post.return_value = MagicMock(
        status_code=201,
        json=lambda: {"id": "new-123"},
    )
    return client


# @pytest.fixture
# def mock_email_service():
#     """Mock email service to prevent real emails in tests."""
#     with patch("app.services.email.send_email") as mock_send:
#         mock_send.return_value = {"message_id": "test-msg-001"}
#         yield mock_send


# ==========================================================================
# Factory Fixtures
# ==========================================================================


# @pytest.fixture
# def make_user(db_session):
#     """Factory fixture: creates User instances with defaults."""
#     created = []
#
#     def _make_user(
#         name: str = "Test User",
#         email: str | None = None,
#         is_active: bool = True,
#     ):
#         from app.models import User
#         if email is None:
#             email = f"user-{len(created)}@test.com"
#         user = User(name=name, email=email, is_active=is_active)
#         db_session.add(user)
#         db_session.flush()
#         created.append(user)
#         return user
#
#     return _make_user
