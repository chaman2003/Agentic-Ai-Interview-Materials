# Python Tooling — Advanced Q&A

---

## LINTING AND FORMATTING TOOLS

**Q: What is Black and how does it differ from other formatters?**
A: Black is an opinionated, uncompromising Python code formatter. It produces deterministic output — same input always produces identical output regardless of how it was originally formatted. No configuration options for style (intentional). One style, no debates.
```toml
# pyproject.toml
[tool.black]
line-length = 88          # Black's default, slightly wider than PEP8's 79
target-version = ["py311"]
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | .venv
)/
'''
```
```bash
black .                   # format all files in place
black --check .           # check without modifying (CI use)
black --diff src/          # show what would change
```

**Q: What is Ruff and why is it rapidly replacing flake8 + isort + pylint?**
A: Ruff is a fast Python linter and formatter written in Rust. It reimplements rules from flake8, isort, pylint, pyupgrade, and 50+ other tools — 10–100x faster than running them separately.
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes (unused imports, undefined names)
    "I",    # isort (import ordering)
    "N",    # pep8-naming
    "UP",   # pyupgrade (use modern Python syntax)
    "B",    # flake8-bugbear (likely bugs)
    "S",    # bandit (security issues)
    "C90",  # mccabe complexity
]
ignore = ["E501"]   # handled by Black's line length

[tool.ruff.lint.isort]
known-first-party = ["myapp"]
force-sort-within-sections = true

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]    # allow assert in tests
```
```bash
ruff check .              # lint
ruff check --fix .        # auto-fix safe fixes
ruff format .             # format (Black-compatible)
```

**Q: What is isort and how do you configure it alongside Black?**
A: isort sorts Python imports into sections (stdlib, third-party, first-party) and within sections alphabetically. Use `--profile black` to match Black's style.
```toml
[tool.isort]
profile = "black"                  # compatible with Black formatting
known_first_party = ["myapp"]
known_third_party = ["fastapi", "sqlalchemy", "pydantic"]
line_length = 88
```
```python
# Before isort
import os
from myapp.models import User
import fastapi
import sys

# After isort
import os
import sys

import fastapi

from myapp.models import User
```

**Q: What is flake8 and how do you configure it?**
A: A wrapper around PyFlakes (undefined names, unused imports) + pycodestyle (PEP 8 style). More configurable than Ruff but slower. Configuration goes in `setup.cfg` or `.flake8` (does NOT support pyproject.toml natively).
```ini
# .flake8 or setup.cfg [flake8]
[flake8]
max-line-length = 88
extend-ignore =
    E203,    # whitespace before ':' (Black compatibility)
    E501,    # line too long (handled by Black)
    W503,    # line break before binary operator
exclude =
    .git,
    __pycache__,
    .venv,
    migrations
per-file-ignores =
    tests/*:F401,F811
```

---

## TYPE CHECKING WITH MYPY

**Q: How do you add type annotations and run mypy?**
A:
```python
# Basic annotations
def greet(name: str, times: int = 1) -> str:
    return (name + " ") * times

# Union types (Python 3.10+ syntax)
def process(value: int | str | None) -> str:
    if value is None:
        return "empty"
    return str(value)

# Collections
from typing import Optional
def find_user(user_id: int) -> Optional[dict]:
    ...

# Python 3.9+ built-in generics (no need to import from typing)
def get_names(users: list[dict[str, str]]) -> list[str]:
    return [u["name"] for u in users]
```
```toml
[tool.mypy]
python_version = "3.11"
strict = true                # enables: disallow-untyped-defs, no-implicit-optional, etc.
ignore_missing_imports = true
exclude = ["migrations/", "tests/"]
```
```bash
mypy src/                 # check all files in src/
mypy --strict src/app.py  # strictest checking on one file
```

**Q: What are Generics in Python typing?**
A: Allows you to write functions/classes that work on any type while maintaining type safety.
```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

int_stack: Stack[int] = Stack()
int_stack.push(42)       # OK
int_stack.push("hello")  # mypy error: str vs int

# Generic functions
def first(items: list[T]) -> T:
    return items[0]
```

**Q: What are Protocols in Python?**
A: Structural subtyping ("duck typing" for mypy). An object satisfies a Protocol if it has the required methods/attributes — no explicit inheritance needed.
```python
from typing import Protocol, runtime_checkable

@runtime_checkable  # allows isinstance() checks at runtime
class Drawable(Protocol):
    def draw(self) -> None: ...
    def get_color(self) -> str: ...

class Circle:
    def draw(self) -> None: print("drawing circle")
    def get_color(self) -> str: return "red"

class Square:
    def draw(self) -> None: print("drawing square")
    def get_color(self) -> str: return "blue"

def render(shape: Drawable) -> None:  # accepts Circle, Square, any Drawable
    shape.draw()

render(Circle())   # OK — structurally compatible
render(Square())   # OK — no inheritance required
```

**Q: What is TypedDict?**
A: A way to type-annotate dictionaries with specific keys and value types. Better than `dict[str, Any]`.
```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: NotRequired[int]    # optional key (Python 3.11+)

def create_user(data: UserDict) -> UserDict:
    return data

# mypy validates at call sites
user: UserDict = {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

---

## PRE-COMMIT HOOKS

**Q: What is pre-commit and how do you set it up?**
A: `pre-commit` is a framework for managing git hooks. Define hooks in `.pre-commit-config.yaml`; they run automatically before each commit.
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace    # remove trailing whitespace
      - id: end-of-file-fixer      # ensure files end with newline
      - id: check-yaml             # validate YAML syntax
      - id: check-merge-conflict   # catch unresolved conflict markers
      - id: detect-private-key     # prevent committing private keys
      - id: check-added-large-files
        args: ["--maxkb=500"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-redis]
```
```bash
pip install pre-commit
pre-commit install           # installs the git hook
pre-commit run --all-files   # run manually on all files (first time / CI)
pre-commit autoupdate        # update hook versions to latest
```

**Q: How do you integrate pre-commit in CI/CD?**
A:
```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: pre-commit/action@v3.0.1   # official pre-commit GitHub Action
        # Runs pre-commit run --all-files
```

---

## MAKEFILE PATTERNS

**Q: How do you use a Makefile to standardize Python project commands?**
A:
```makefile
# Makefile
.DEFAULT_GOAL := help
.PHONY: install lint format test coverage clean build

help:              ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:           ## Install all dependencies
	pip install -e ".[dev]"
	pre-commit install

lint:              ## Run linters (ruff + mypy)
	ruff check .
	mypy src/

format:            ## Auto-format code
	ruff format .
	ruff check --fix .

test:              ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast:         ## Run tests excluding slow/integration
	pytest tests/ -v -m "not slow and not integration"

coverage:          ## Open HTML coverage report
	open htmlcov/index.html    # macOS
	# xdg-open htmlcov/index.html  # Linux

clean:             ## Remove build artifacts
	rm -rf .pytest_cache __pycache__ dist build *.egg-info htmlcov .mypy_cache

build:             ## Build distribution packages
	python -m build

release: clean test build   ## Full release pipeline
	twine upload dist/*
```

---

## TOX FOR MULTI-ENVIRONMENT TESTING

**Q: What is tox and when do you need it?**
A: tox automates testing across multiple Python versions and configurations. Essential for libraries that must support Python 3.9, 3.10, 3.11, 3.12.
```ini
# tox.ini  (or [tool.tox] in pyproject.toml)
[tox]
envlist = py39, py310, py311, py312, lint, type

[testenv]
deps =
    pytest
    pytest-cov
    pytest-asyncio
commands =
    pytest tests/ --cov=src --cov-report=term-missing

[testenv:lint]
deps = ruff
commands =
    ruff check .
    ruff format --check .

[testenv:type]
deps =
    mypy
    types-requests
commands =
    mypy src/
```
```bash
tox                  # run all environments
tox -e py311        # run only Python 3.11
tox -e lint,type    # run specific environments
tox -p auto         # run in parallel
```

---

## PERFORMANCE PROFILING

**Q: How do you profile Python code with cProfile?**
A:
```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()
my_slow_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')   # sort by cumulative time in function
stats.print_stats(20)            # show top 20 functions

# From command line
python -m cProfile -s cumulative my_script.py | head -30

# Profile and save for snakeviz visualization
python -m cProfile -o output.prof my_script.py
snakeviz output.prof   # pip install snakeviz — opens visual browser
```

**Q: What is line_profiler and when do you use it over cProfile?**
A: `line_profiler` profiles line-by-line within a function. Use when cProfile identifies the slow function but you need to know WHICH LINES are slow.
```python
# pip install line_profiler
from line_profiler import LineProfiler

def slow_function(data):
    result = []
    for item in data:
        result.append(item ** 2)       # is this slow?
    return sorted(result)              # or this?

profiler = LineProfiler()
profiler.add_function(slow_function)
profiler.runcall(slow_function, range(100000))
profiler.print_stats()

# Command line with @profile decorator:
# kernprof -l -v my_script.py
```

**Q: How do you profile memory usage?**
A:
```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def load_and_process():
    data = [i for i in range(1_000_000)]   # line 2: +7.6 MiB
    processed = list(map(str, data))        # line 3: +32.1 MiB
    del data                               # line 4: -7.6 MiB
    return processed

# Output shows memory usage per line:
# Line #    Mem usage    Increment   Line Contents
# 2         45.2 MiB    +7.6 MiB    data = ...

# For a quick snapshot without decorator
import tracemalloc
tracemalloc.start()
result = process_data()
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current/1024/1024:.1f}MB, Peak: {peak/1024/1024:.1f}MB")
tracemalloc.stop()
```

---

## PYTEST ADVANCED

**Q: What is @pytest.mark.parametrize in depth?**
A:
```python
import pytest

# Basic: test with multiple input/expected pairs
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("not-an-email",     False),
    ("@no-user.com",     False),
    ("user@.com",        False),
])
def test_email_validation(email, is_valid):
    assert validate_email(email) == is_valid

# Multiple parameters (IDs help in test output)
@pytest.mark.parametrize("n,expected", [
    pytest.param(0, 1,  id="zero"),
    pytest.param(1, 1,  id="one"),
    pytest.param(5, 120, id="five"),
], ids=str)   # auto-generate IDs from param values
def test_factorial(n, expected):
    assert factorial(n) == expected

# Cross-product parametrize (stacked decorators)
@pytest.mark.parametrize("username", ["alice", "bob"])
@pytest.mark.parametrize("role",     ["admin", "user"])
def test_permissions(username, role):
    # runs 4 combinations: alice/admin, alice/user, bob/admin, bob/user
    ...
```

**Q: What are factory fixtures and how do you use them?**
A: A fixture that returns a factory function. Allows creating multiple independent instances in the same test with different configurations.
```python
import pytest
from myapp.models import User

@pytest.fixture
def make_user(db_session):
    """Factory fixture: call it multiple times for distinct users"""
    created = []
    def _make(name="Alice", role="user", **kwargs):
        user = User(name=name, role=role, **kwargs)
        db_session.add(user)
        db_session.flush()
        created.append(user)
        return user
    yield _make
    # Cleanup all created users
    for u in created:
        db_session.delete(u)
    db_session.commit()

def test_admin_can_view_all_users(make_user):
    admin = make_user(name="Admin", role="admin")
    user1 = make_user(name="Alice")
    user2 = make_user(name="Bob")
    assert admin.can_view(user1)
    assert admin.can_view(user2)
```

**Q: What is snapshot testing in pytest?**
A: Test that a function's output matches a previously-approved "snapshot" stored on disk. Great for complex outputs (API responses, rendered HTML, data transformations) where writing manual assertions is tedious.
```python
# pip install syrupy
from syrupy.assertion import SnapshotAssertion

def test_serialize_order(snapshot: SnapshotAssertion):
    order = create_test_order()
    assert serialize(order) == snapshot  # first run: creates snapshot file

# Update snapshots when output intentionally changes:
# pytest --snapshot-update
```

---

## DEBUGGING TOOLS

**Q: How do you use pdb and ipdb for debugging?**
A:
```python
# Insert breakpoint (Python 3.7+)
breakpoint()   # equivalent to import pdb; pdb.set_trace()

# ipdb: prettier, tab-completion, syntax highlighting
import ipdb; ipdb.set_trace()

# Common pdb commands:
# n (next)     — step over, execute current line
# s (step)     — step into function call
# c (continue) — continue until next breakpoint
# l (list)     — show surrounding code
# p expr       — print expression value
# pp expr      — pretty-print
# w (where)    — show call stack
# u/d          — move up/down the call stack
# q (quit)     — exit debugger
# b file:line  — set conditional breakpoint
# b func_name  — break at function entry
```

```python
# Post-mortem debugging: start debugger after an unhandled exception
import pdb
try:
    risky_function()
except Exception:
    pdb.post_mortem()   # inspect state at crash point

# From command line:
python -m pdb script.py
```

**Q: What are effective logging strategies for Python applications?**
A:
```python
import logging
import structlog   # pip install structlog — structured JSON logging

# Basic structured logging with stdlib
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
)

# Better: structlog for JSON output
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # JSON for prod
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger()

def process_order(order_id: str, user_id: str):
    log.info("processing_order", order_id=order_id, user_id=user_id)
    try:
        result = do_work(order_id)
        log.info("order_processed", order_id=order_id, duration_ms=result.duration)
    except PaymentError as e:
        log.error("payment_failed", order_id=order_id, error=str(e), exc_info=True)
        raise
```

---

## DEPENDENCY MANAGEMENT COMPARISON

**Q: Compare pip, pipenv, poetry, and uv.**
A:

| Tool    | Lockfile | Venv mgmt | Build/Publish | Speed  | Config file      |
|---------|----------|-----------|---------------|--------|------------------|
| pip     | No       | No        | No            | Fast   | requirements.txt |
| pipenv  | Yes      | Yes       | No            | Slow   | Pipfile          |
| poetry  | Yes      | Yes       | Yes           | Medium | pyproject.toml   |
| uv      | Yes      | Yes       | Yes           | 10-100x| pyproject.toml   |

**pip:** The baseline. Install packages. No real dependency resolution (can install incompatible versions). Use `pip-tools` to add lockfiles (`pip-compile` generates `requirements.txt` from `requirements.in`).

**pipenv:** Adds Pipfile + Pipfile.lock for deterministic installs. Slow resolution, largely superseded by poetry and uv. Still found in older projects.

**poetry:** Current standard for serious Python projects. Automatic dependency resolution, lockfile, virtualenv management, building wheels, publishing to PyPI.
```bash
poetry new myproject          # create project structure
poetry add fastapi            # add dependency
poetry add --group dev pytest # add dev dependency
poetry install --no-dev       # production install (skip dev deps)
poetry run pytest             # run in virtual env
poetry build && poetry publish # build and upload to PyPI
```

**uv (by Astral, 2024):** Rewrite in Rust. 10-100x faster than pip and poetry. Drop-in replacement for pip, pip-tools, and poetry workflows. Growing rapidly.
```bash
uv pip install fastapi        # like pip but faster
uv sync                       # install from lockfile (like poetry install)
uv run pytest                 # run in virtual env
uv add fastapi                # add to pyproject.toml
```

---

## DOCKER + PYTHON BEST PRACTICES

**Q: What is a multi-stage Docker build for Python?**
A: Use multiple FROM stages to separate build dependencies from the final runtime image. Keeps the production image small and free of build tools.
```dockerfile
# Stage 1: build dependencies (larger image, has gcc, git, etc.)
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry==1.8.0 && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --without dev

# Stage 2: runtime image (lean, no build tools)
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \   # don't write .pyc files
    PYTHONUNBUFFERED=1 \          # don't buffer stdout/stderr (important for logs)
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy only the virtual env from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy source code last (changes frequently, cache earlier layers)
COPY src/ ./src/

# Run as non-root user (security best practice)
RUN adduser --system --no-create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Q: What should be in .dockerignore for a Python project?**
A:
```
.git
.gitignore
.venv
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.ruff_cache
htmlcov
dist
build
*.egg-info
.env
.env.local
*.env
tests/
docs/
README.md
Makefile
docker-compose*.yml
```

**Q: What are the key Python Docker environment variables?**
A:
```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1   # prevents writing .pyc bytecode files
ENV PYTHONUNBUFFERED=1          # flushes stdout/stderr immediately (essential for docker logs)
ENV PYTHONFAULTHANDLER=1        # dump Python traceback on crashes (useful for prod debugging)
ENV PYTHONHASHSEED=0            # deterministic hash seed (for reproducible tests)
```

---

## CI/CD FOR PYTHON

**Q: Write a complete GitHub Actions workflow for a Python project.**
A:
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports: ["5432:5432"]

      redis:
        image: redis:7
        ports: ["6379:6379"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install poetry
          poetry install --with dev

      - name: Lint with Ruff
        run: poetry run ruff check .

      - name: Type-check with mypy
        run: poetry run mypy src/

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
        run: |
          poetry run pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing \
            --junitxml=test-results.xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: test-results.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: pre-commit/action@v3.0.1

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
```

**Q: How do you add a coverage badge to your README?**
A: Three approaches:
1. **Codecov** — Upload `coverage.xml` in CI, Codecov generates a dynamic badge URL: `[![codecov](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)`
2. **Shields.io with Codecov** — same data, customizable badge styling
3. **genbadge** — generate a local badge from coverage.xml and commit it: `genbadge coverage -i coverage.xml -o coverage-badge.svg`
