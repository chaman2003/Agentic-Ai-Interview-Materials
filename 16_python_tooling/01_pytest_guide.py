"""
PYTEST GUIDE - Fixtures, parametrize, marks, mocking, async, coverage
For: Python GenAI Developer interview
"""

# ============================================================
# 1. BASIC TEST STRUCTURE
# ============================================================
# Run tests: pytest
# Run with verbose: pytest -v
# Run specific file: pytest 01_pytest_guide.py
# Run specific test: pytest -k "test_add"
# Run with coverage: pytest --cov=. --cov-report=html

import pytest

# Simple test
def add(a, b):
    return a + b

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 5) == 5


# ============================================================
# 2. FIXTURES - Reusable setup/teardown
# ============================================================
# Fixtures run before tests that use them
# scope: "function" (default), "class", "module", "session"

@pytest.fixture
def sample_user():
    """Provides a sample user dict for tests"""
    return {"id": 1, "name": "Chaman", "role": "admin", "active": True}

@pytest.fixture
def sample_users():
    """Provides a list of users"""
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Carol", "role": "user"},
    ]

def test_user_has_name(sample_user):
    assert sample_user["name"] == "Chaman"

def test_user_is_admin(sample_user):
    assert sample_user["role"] == "admin"

def test_user_is_active(sample_user):
    assert sample_user["active"] is True

def test_users_count(sample_users):
    assert len(sample_users) == 3


# ============================================================
# 3. MODULE-SCOPED FIXTURE - Runs once per test file
# ============================================================

@pytest.fixture(scope="module")
def db_connection():
    """Simulates DB connection - setup once, teardown once"""
    print("\n[SETUP] Creating DB connection")
    connection = {"connected": True, "host": "localhost", "db": "test_db"}
    yield connection  # yield = teardown runs after tests
    print("\n[TEARDOWN] Closing DB connection")
    connection["connected"] = False

def test_db_is_connected(db_connection):
    assert db_connection["connected"] is True

def test_db_host(db_connection):
    assert db_connection["host"] == "localhost"


# ============================================================
# 4. PARAMETRIZE - Run same test with multiple inputs
# ============================================================

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
    (-5, -5, -10),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected


# Test edge cases with parametrize
def is_palindrome(s: str) -> bool:
    s = s.lower().replace(" ", "")
    return s == s[::-1]

@pytest.mark.parametrize("word, expected", [
    ("racecar", True),
    ("hello", False),
    ("A man a plan a canal Panama", True),
    ("", True),
    ("a", True),
])
def test_palindrome(word, expected):
    assert is_palindrome(word) == expected


# ============================================================
# 5. MARKS - Custom test categories
# ============================================================
# Register marks in pytest.ini or conftest.py to avoid warnings:
# [pytest]
# markers =
#     slow: marks tests as slow
#     integration: marks integration tests
#     unit: marks unit tests

@pytest.mark.slow
def test_slow_operation():
    """Use -m "not slow" to skip this"""
    result = sum(range(1000000))
    assert result > 0

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    assert False

@pytest.mark.skipif(True, reason="Skipping on this condition")
def test_conditional_skip():
    assert False

@pytest.mark.xfail(reason="Known bug - will be fixed in v2")
def test_known_bug():
    assert 1 == 2  # This will fail but pytest won't report as failure


# ============================================================
# 6. TESTING EXCEPTIONS
# ============================================================

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "Cannot divide by zero" in str(exc_info.value)

def test_divide_normal():
    assert divide(10, 2) == 5.0


# ============================================================
# 7. MOCKING WITH unittest.mock
# ============================================================
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# 7a. Basic Mock
def test_basic_mock():
    mock = Mock()
    mock.return_value = 42
    result = mock()
    assert result == 42
    mock.assert_called_once()

# 7b. Mock method on object
class UserService:
    def get_user(self, user_id: int) -> dict:
        # In real code, this would hit a DB
        raise NotImplementedError

    def is_admin(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        return user.get("role") == "admin"

def test_is_admin_true():
    service = UserService()
    service.get_user = Mock(return_value={"id": 1, "role": "admin"})
    assert service.is_admin(1) is True
    service.get_user.assert_called_once_with(1)

def test_is_admin_false():
    service = UserService()
    service.get_user = Mock(return_value={"id": 2, "role": "user"})
    assert service.is_admin(2) is False

# 7c. Patch - mock external module/function
import json

def load_config(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)

def test_load_config_with_patch():
    fake_config = {"db_url": "postgresql://localhost/test", "debug": True}
    with patch("builtins.open", create=True) as mock_open:
        with patch("json.load", return_value=fake_config):
            result = load_config("config.json")
    assert result["debug"] is True
    assert result["db_url"] == "postgresql://localhost/test"

# 7d. Patch as decorator
@patch("json.dumps")
def test_with_patch_decorator(mock_dumps):
    mock_dumps.return_value = '{"mocked": true}'
    result = json.dumps({"real": "data"})
    assert result == '{"mocked": true}'
    mock_dumps.assert_called_once_with({"real": "data"})

# 7e. Mock with side_effect
def test_mock_side_effect():
    mock_fn = Mock(side_effect=[1, 2, ValueError("error on 3rd call")])
    assert mock_fn() == 1
    assert mock_fn() == 2
    with pytest.raises(ValueError):
        mock_fn()

# 7f. Mock HTTP requests (common pattern for LLM/API testing)
def call_openai_api(prompt: str) -> str:
    import httpx  # Simulating an HTTP call
    # In real code: response = client.post(...)
    pass

def test_mock_api_call():
    with patch("httpx.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Mocked LLM response"}}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Now any code that calls httpx.post gets the mock
        result = mock_post("https://api.openai.com/v1/chat/completions", json={})
        assert result.status_code == 200
        assert result.json()["choices"][0]["message"]["content"] == "Mocked LLM response"


# ============================================================
# 8. ASYNC TESTS
# ============================================================
import asyncio

async def fetch_data(url: str) -> dict:
    # Simulates async HTTP call
    await asyncio.sleep(0.01)  # Simulate network delay
    return {"url": url, "data": "response"}

@pytest.mark.asyncio  # Requires: pip install pytest-asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com/data")
    assert result["data"] == "response"
    assert "url" in result

# Mock async functions
@pytest.mark.asyncio
async def test_async_with_mock():
    async def mock_fetch(url):
        return {"mocked": True, "url": url}

    result = await mock_fetch("https://example.com")
    assert result["mocked"] is True

# AsyncMock (Python 3.8+)
def test_async_mock():
    mock_fn = AsyncMock(return_value={"success": True})
    # In tests, you'd await this inside an async test
    assert mock_fn.return_value == {"success": True}


# ============================================================
# 9. TESTING LLM PIPELINES
# ============================================================

class LLMPipeline:
    def __init__(self, client):
        self.client = client

    def extract_entities(self, text: str) -> dict:
        response = self.client.chat(text)
        # Parse response
        return response

def test_llm_pipeline_with_mock():
    mock_client = Mock()
    mock_client.chat.return_value = {
        "entities": ["Alice", "Bob"],
        "intent": "query",
        "confidence": 0.95
    }

    pipeline = LLMPipeline(client=mock_client)
    result = pipeline.extract_entities("What did Alice and Bob discuss?")

    assert "entities" in result
    assert "Alice" in result["entities"]
    mock_client.chat.assert_called_once_with("What did Alice and Bob discuss?")


# ============================================================
# 10. CONFTEST.PY - Shared fixtures across files
# ============================================================
# Create conftest.py in your test directory:
"""
# conftest.py
import pytest
from myapp import create_app, db

@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    return app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)  # Runs for every test automatically
def reset_db(app):
    with app.app_context():
        db.create_all()
    yield
    with app.app_context():
        db.drop_all()
"""

# ============================================================
# 11. COVERAGE
# ============================================================
# Install: pip install pytest-cov
# Run: pytest --cov=. --cov-report=term-missing
# Run: pytest --cov=myapp --cov-report=html  (generates htmlcov/index.html)
#
# .coveragerc file:
# [run]
# source = myapp
# omit = tests/*, migrations/*
#
# [report]
# fail_under = 80  # Fail if coverage below 80%


# ============================================================
# QUICK REFERENCE
# ============================================================
"""
pytest commands:
  pytest                          # Run all tests
  pytest -v                       # Verbose
  pytest -s                       # Show print statements
  pytest -k "test_add"            # Run tests matching pattern
  pytest -m "not slow"            # Exclude marked tests
  pytest --tb=short               # Short traceback
  pytest -x                       # Stop on first failure
  pytest --lf                     # Only run last failed tests
  pytest --cov=. --cov-report=html  # Coverage report

Fixtures:
  @pytest.fixture                 # function scope (default)
  @pytest.fixture(scope="module") # once per file
  @pytest.fixture(scope="session")# once per test run
  yield in fixture = teardown code runs after

Mocking:
  Mock()                          # Basic mock
  Mock(return_value=x)           # Set return value
  Mock(side_effect=[1,2,err])    # Different each call
  patch("module.function")        # Replace function
  AsyncMock()                     # For async functions
  mock.assert_called_once()       # Verify it was called
  mock.assert_called_with(args)  # Verify call args
"""
