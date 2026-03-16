# Python Tooling Q&A — pytest, venv, poetry

---

## PYTEST QUESTIONS

**Q1: What is pytest and why use it over unittest?**
pytest is a testing framework. Advantages over unittest:
- Simpler syntax — just `assert`, no `self.assertEqual`
- Better error messages
- Powerful fixtures system
- Parametrize for data-driven tests
- Rich plugin ecosystem (pytest-asyncio, pytest-cov, pytest-mock)

**Q2: What are fixtures in pytest?**
Reusable setup/teardown functions. Pytest injects them as function parameters:
```python
@pytest.fixture
def db():
    conn = create_connection()
    yield conn      # teardown runs after yield
    conn.close()

def test_query(db):  # db fixture injected automatically
    result = db.execute("SELECT 1")
    assert result is not None
```

**Q3: What is conftest.py?**
Special file pytest auto-discovers. Fixtures defined here are available to all tests in same directory and subdirectories without imports. Common for: app factory, DB connection, test client.

**Q4: Explain fixture scopes**
- `function` (default): runs before/after each test function
- `class`: runs once per test class
- `module`: runs once per test file
- `session`: runs once for entire test run

Use `session` for expensive setup (DB connection, app startup). Use `function` for things that need cleanup per test.

**Q5: What is parametrize?**
Run same test with multiple input/output pairs:
```python
@pytest.mark.parametrize("input, expected", [
    ("racecar", True),
    ("hello", False),
])
def test_palindrome(input, expected):
    assert is_palindrome(input) == expected
```
Same test runs twice. Avoids code duplication.

**Q6: How do you test that a function raises an exception?**
```python
with pytest.raises(ValueError) as exc_info:
    divide(10, 0)
assert "Cannot divide by zero" in str(exc_info.value)
```

**Q7: What is mocking and when do you use it?**
Replacing real dependencies with fake ones during tests. Use when:
- Testing code that calls external APIs (OpenAI, databases, HTTP)
- Want to test how code responds to errors/specific responses
- Tests should be fast and not depend on external services

**Q8: Difference between Mock and patch?**
- `Mock()`: creates a mock object you configure manually
- `patch()`: temporarily replaces a real module/function with a mock

```python
# Mock: create fake object
service.get_user = Mock(return_value={"role": "admin"})

# Patch: replace real import
with patch("myapp.openai_client.chat") as mock_chat:
    mock_chat.return_value = "mocked response"
    result = my_function()
```

**Q9: How do you mock async functions?**
Use `AsyncMock` (Python 3.8+):
```python
from unittest.mock import AsyncMock
mock_fn = AsyncMock(return_value={"data": "result"})
result = await mock_fn()
```

**Q10: How do you test FastAPI endpoints?**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_cases():
    response = client.get("/cases")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Q11: What is pytest-cov? How do you generate coverage?**
Plugin for measuring test coverage:
```bash
pytest --cov=myapp --cov-report=term-missing
pytest --cov=. --cov-report=html  # Generates HTML report
```
Coverage tells you which lines/branches are NOT tested.

**Q12: What are pytest marks?**
Tags for test categorization and selection:
```python
@pytest.mark.slow      # Custom mark
@pytest.mark.skip      # Always skip
@pytest.mark.skipif(condition, reason="...")
@pytest.mark.xfail     # Expected to fail
```
Run selective: `pytest -m "not slow"` or `pytest -m "integration"`

---

## VENV QUESTIONS

**Q13: What is a virtual environment?**
Isolated Python environment with its own packages, separate from system Python and other projects. Prevents version conflicts.

**Q14: How do you create and activate a venv?**
```bash
python -m venv venv        # Create
source venv/bin/activate   # Activate (Linux/Mac)
venv\Scripts\activate      # Activate (Windows)
deactivate                 # Exit
```

**Q15: What is requirements.txt and how do you use it?**
Plain text file listing package dependencies:
```bash
pip freeze > requirements.txt  # Save current env
pip install -r requirements.txt  # Restore
```

---

## POETRY QUESTIONS

**Q16: What is Poetry and how does it differ from pip?**
Poetry is a complete dependency management tool:
- Resolves dependency conflicts automatically
- Generates poetry.lock (reproducible installs)
- Handles virtual environment creation
- Can build and publish packages

pip only installs packages — doesn't do dependency resolution or locking.

**Q17: What is pyproject.toml?**
Modern Python project config file. Replaces setup.py. Contains: project metadata, dependencies, dev dependencies, build config, tool configs (black, pytest, mypy).

**Q18: What is poetry.lock and should you commit it?**
Exact snapshot of all installed packages with versions and hashes. YES, always commit it. Guarantees all team members and CI/CD get identical environments.

**Q19: How do you add a dev dependency in Poetry?**
```bash
poetry add --dev pytest pytest-asyncio pytest-cov
# or newer syntax:
poetry add pytest --group dev
```
Dev dependencies don't get installed in production (`poetry install --no-dev`).

**Q20: Common poetry commands?**
```bash
poetry init              # Create pyproject.toml
poetry add fastapi       # Add dependency
poetry add --dev pytest  # Add dev dependency
poetry install           # Install all from lock file
poetry run pytest        # Run in venv
poetry shell             # Activate venv
poetry show --tree       # Show dependency tree
```
