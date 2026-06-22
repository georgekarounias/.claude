---
name: python-fastapi-testing-best-practices
description: "Testing best practices for Python FastAPI services. Use when writing or reviewing pytest tests for FastAPI: async test patterns, httpx AsyncClient with ASGITransport, dependency overrides (not monkeypatching), fixtures, SQLAlchemy test databases, and coverage expectations."
---

# Python FastAPI Testing Best Practices

## When to Use
- Writing new tests for FastAPI endpoints or services
- Reviewing test quality and coverage for a Python backend
- Setting up test infrastructure (`conftest.py`, fixtures, DB setup)

## Stack
- **pytest** + **pytest-asyncio** — async test execution
- **httpx** `AsyncClient` + `ASGITransport` — endpoint integration tests
- **pytest-cov** — coverage reporting
- Do **NOT** use `async_asgi_testclient` — it is unmaintained
- Do **NOT** use `httpx.TestClient` for async routes — use `AsyncClient`

## Set Up Async from Day 0

Wiring the event loop correctly from the start avoids hard-to-debug errors later.

In `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # no @pytest.mark.asyncio needed per test
```

## conftest.py Conventions

```python
import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.dependencies import get_db
from app.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
```

## Dependency Overrides — Don't Monkeypatch

Use `app.dependency_overrides` to swap any dependency (auth, DB, external clients).
Never monkeypatch internals — overrides are the official FastAPI mechanism.

```python
from src.auth.dependencies import parse_jwt_data
from src.main import app

def fake_user():
    return {"user_id": "00000000-0000-0000-0000-000000000001"}

@pytest.fixture(autouse=True)
def _override_auth():
    app.dependency_overrides[parse_jwt_data] = fake_user
    yield
    app.dependency_overrides.clear()
```

## Endpoint Tests

```python
async def test_create_post(client: AsyncClient):
    resp = await client.post("/posts", json={"title": "Hello"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Hello"
```

- Test **happy path**, **validation errors (422)**, and **not-found (404)** for every endpoint.
- Assert both status code and response body shape.

## Service Unit Tests

- Test service functions directly, passing in-memory or mock DB sessions.
- Do NOT invoke HTTP for service-layer tests — isolate from the transport layer.
- Use `unittest.mock.AsyncMock` for async collaborators.

```python
async def test_get_post_raises_when_not_found(db_session: AsyncSession):
    with pytest.raises(PostNotFound):
        await service.get_by_id(db_session, uuid4())
```

## Async Test Rules

- Never mix incompatible fixture scopes (e.g., session-scoped async fixture with function-scoped async test) — this causes event loop errors.
- Do NOT use `asyncio.get_event_loop()` in tests — use `asyncio_mode = "auto"`.
- Always clear `app.dependency_overrides` after each test (fixture teardown).

## Coverage Expectations

- Aim for ≥ 80% line coverage on service and router modules.
- All error paths (`HTTPException` raises, validation failures) must have at least one test.
- Exclude migrations, config, `__init__.py`, and generated files from coverage requirements.
- Track coverage in CI: `pytest --cov=src --cov-report=term-missing --cov-fail-under=80`
