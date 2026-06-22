---
name: python-fastapi-best-practices
description: "FastAPI architecture and implementation best practices. Use when building or reviewing Python FastAPI services: domain-based project structure, async/sync route rules, Pydantic v2 schemas, dependency injection and chaining, SQLAlchemy async, BackgroundTasks guidance, Alembic migrations, and security."
---

# Python FastAPI Best Practices

## When to Use

- Implementing new FastAPI routers, endpoints, or services
- Reviewing FastAPI code for architecture and correctness
- Designing dependency injection chains or lifespan events

## Project Structure

Use **domain-based** structure (not file-type-based). File-type layout (crud/, routers/, models/) does not scale.
Inspired by Netflix Dispatch.

```
src/
├── main.py                # App factory, lifespan, middleware registration
├── config.py              # Global pydantic-settings BaseSettings
├── database.py            # DB engine, session factory
├── exceptions.py          # Global exception handlers
├── models.py              # Global shared SQLAlchemy base
├── {domain}/              # One folder per domain (auth, posts, billing…)
│   ├── router.py          # APIRouter — endpoints only, no business logic
│   ├── schemas.py         # Pydantic request/response models
│   ├── models.py          # SQLAlchemy ORM models
│   ├── service.py         # Business logic — no HTTP concerns
│   ├── dependencies.py    # FastAPI Depends() functions for this domain
│   ├── constants.py       # Domain-level enums and error codes
│   ├── exceptions.py      # Domain-specific exception classes
│   └── utils.py           # Non-business helpers (data shaping, enrichment)
alembic/
tests/
│   └── {domain}/          # Mirror src structure
```

When importing across domains, always use explicit module names:

```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
```

## Async vs Sync Routes

- **`async def`** — use for I/O-bound handlers that await coroutines (database, HTTP calls). The event loop must never block.
- **`def`** — FastAPI offloads sync routes to a threadpool automatically. Safe for blocking I/O, but threads have overhead and the pool is finite.
- **NEVER** call blocking code (`time.sleep`, synchronous ORM, sync HTTP) inside an `async def` route. It stalls the entire event loop.
- **CPU-intensive** work (image processing, ML inference, video transcoding) belongs in a separate worker process (Celery, ARQ) — not threads (GIL) and not async.
- If a sync SDK is unavoidable inside `async def`, use `run_in_threadpool` from Starlette:
  ```python
  from fastapi.concurrency import run_in_threadpool
  result = await run_in_threadpool(sync_client.call, data)
  ```

## Pydantic v2

- **Use Pydantic extensively** — regex, enums, `EmailStr`, `AnyUrl`, `Field(ge=…)`, pattern validators.
- Separate request schemas (input) from response schemas (output). Never expose ORM models as responses.
- Use `model_config = ConfigDict(from_attributes=True)` for ORM-to-schema conversion.
- Create a **custom base model** for app-wide defaults (datetime serialization, timezone, etc.):

  ```python
  from zoneinfo import ZoneInfo
  from pydantic import BaseModel, ConfigDict, field_serializer

  class AppModel(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      @field_serializer("*", when_used="json", check_fields=False)
      def _normalize_datetimes(self, value):
          if isinstance(value, datetime):
              if value.tzinfo is None:
                  value = value.replace(tzinfo=ZoneInfo("UTC"))
              return value.strftime("%Y-%m-%dT%H:%M:%S%z")
          return value
  ```

- **Decouple `BaseSettings` by domain** — one `AuthConfig`, one `DatabaseConfig`, etc. A single monolithic settings class becomes unmaintainable.
  ```python
  # src/auth/config.py
  from pydantic_settings import BaseSettings
  class AuthConfig(BaseSettings):
      JWT_SECRET: str
      JWT_EXP: int = 5
  auth_settings = AuthConfig()
  ```

## Dependency Injection

- Use `Depends()` for **request validation**, not just service injection. Check DB constraints, auth, ownership inside dependencies.
- **Chain dependencies** to avoid repetition:

  ```python
  async def valid_post_id(post_id: UUID4) -> Mapping:
      post = await service.get_by_id(post_id)
      if not post:
          raise PostNotFound()
      return post

  async def valid_owned_post(
      post: Mapping = Depends(valid_post_id),
      user: dict = Depends(parse_jwt_data),
  ) -> Mapping:
      if post["creator_id"] != user["user_id"]:
          raise UserNotOwner()
      return post
  ```

- FastAPI **caches dependency results per request** — decompose freely without performance cost.
- **Prefer `async` dependencies** even when not awaiting: sync deps run in the threadpool; small DI functions don't need that overhead.
- Use `yield` dependencies for resources with teardown (DB sessions).

## BackgroundTasks vs Task Queue

| Use `BackgroundTasks`             | Use a real task queue (Celery, ARQ)      |
| --------------------------------- | ---------------------------------------- |
| Task < 1 second                   | Task takes seconds or minutes            |
| Failure can be dropped silently   | You need retries or dead-letter handling |
| In-process: send email, log a row | CPU-heavy or needs a separate worker     |
| No scheduling needed              | Needs cron, ETA, or rate limiting        |

If you would page someone when the task is lost, use a real queue.

## Database

- Use **SQLAlchemy 2.0 async API** (`AsyncSession`, `async_sessionmaker`) for new projects.
- **SQL-first, Pydantic-second** — aggregate joins, JSON building, and filtering in SQL. CPython is slower than the database for set operations.
- Set explicit **naming conventions** in SQLAlchemy metadata:
  ```python
  from sqlalchemy import MetaData
  POSTGRES_INDEXES_NAMING_CONVENTION = {
      "ix": "%(column_0_label)s_idx",
      "uq": "%(table_name)s_%(column_0_name)s_key",
      "ck": "%(table_name)s_%(constraint_name)s_check",
      "fk": "%(table_name)s_%(column_0_name)s_fkey",
      "pk": "%(table_name)s_pkey",
  }
  metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
  ```

## Alembic Migrations

- Migrations must be **static and reversible**.
- Use descriptive names with a date prefix: `2024-08-24_post_content_idx.py`.
- Configure `alembic.ini`: `file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s`

## Configuration

- Never hardcode secrets or connection strings.
- Load settings once via a cached dependency: `@lru_cache def get_settings() -> Settings`.

## Error Handling

- Raise `HTTPException` for client errors (4xx).
- Register `@app.exception_handler` for domain exceptions to return structured JSON.
- Log server errors (5xx) before responding; never leak stack traces to clients.

## Security

- `CORSMiddleware`: configure `allow_origins` explicitly — never `["*"]` in production.
- Use OAuth2 + JWT via FastAPI's `Security()` / `OAuth2PasswordBearer`.
- Hide OpenAPI docs in production:
  ```python
  app = FastAPI(openapi_url=None)  # disable in prod
  ```

## Lifespan

- Use `@asynccontextmanager` lifespan (not deprecated `on_startup`/`on_shutdown`).
- Initialise DB pools and external clients in lifespan startup.
- Always release resources in the `finally` block.

## Tooling

- **ruff** for linting and formatting (replaces black, isort, autoflake; 600+ lint rules):
  ```sh
  ruff check --fix src
  ruff format src
  ```
- Use pre-commit hooks with ruff for consistent enforcement.
