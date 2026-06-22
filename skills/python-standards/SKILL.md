---
name: python-standards
description: "Python language standards and code style for FastAPI projects. Use when writing or reviewing Python code: type hints, PEP 8, import ordering, naming conventions, docstring style, and modern Python idioms (3.11+)."
---

# Python Standards

## When to Use
- Writing new Python modules, classes, or functions
- Reviewing Python code for style and standards compliance
- Onboarding to the Python coding conventions for this project

## Standards

### Type Hints
- All function signatures must have type hints (parameters and return type).
- Use `from __future__ import annotations` for forward references.
- Prefer `X | None` over `Optional[X]` (Python 3.10+).
- Use `list[T]`, `dict[K, V]` built-in generics (Python 3.9+), not `List`, `Dict` from `typing`.

### Naming Conventions
- Modules and packages: `snake_case`
- Classes: `PascalCase`
- Functions, methods, variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Imports
- Order: stdlib → third-party → local (separated by blank lines).
- Use `isort` or `ruff` for automatic ordering.
- Avoid wildcard imports (`from module import *`).

### Formatting
- Line length: 88 characters (ruff/Black default).
- Use **ruff** for both linting and formatting (replaces black, isort, autoflake; supports 600+ lint rules):
  ```sh
  ruff check --fix src
  ruff format src
  ```
- Configure in `pyproject.toml`:
  ```toml
  [tool.ruff]
  line-length = 88
  [tool.ruff.lint]
  select = ["E", "F", "I", "UP", "B", "SIM"]
  ```
- Use pre-commit hooks with ruff for consistent enforcement.

### Docstrings
- Public modules, classes, and functions must have docstrings.
- Use Google-style or NumPy-style consistently across the project.

### Error Handling
- Never catch bare `except:` — always specify exception type.
- Raise specific exceptions; avoid `raise Exception("message")`.
- Use custom exception classes for domain errors.

### Modern Idioms
- Prefer `pathlib.Path` over `os.path`.
- Use `dataclasses` or Pydantic models over plain dicts for structured data.
- Use f-strings for string formatting.
- Prefer `match` statements (Python 3.10+) over long `if/elif` chains where appropriate.
