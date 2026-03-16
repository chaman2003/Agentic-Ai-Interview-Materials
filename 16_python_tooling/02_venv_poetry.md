# Python Virtual Environments & Dependency Management

## Why Virtual Environments?
- Isolate project dependencies (avoid conflicts between projects)
- Reproducible builds (exact same packages on every machine)
- Clean separation from system Python

---

## VENV (Built-in Python)

### Create & Activate
```bash
# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# You'll see (venv) in your prompt
(venv) $ python --version
```

### Install & Manage Packages
```bash
pip install flask               # Install package
pip install flask==2.3.0        # Install specific version
pip install "flask>=2.0,<3.0"  # Version range

pip list                        # Show installed packages
pip freeze                      # Show with exact versions
pip freeze > requirements.txt   # Save to file
pip install -r requirements.txt # Install from file

pip uninstall flask             # Remove package
pip show flask                  # Package info
```

### Deactivate
```bash
deactivate  # Exit virtual environment
```

---

## POETRY (Modern Dependency Management)

Poetry handles: venv creation + dependency resolution + packaging + publishing

### Install Poetry
```bash
# Install (recommended way)
curl -sSL https://install.python-poetry.org | python3 -

# Or with pip
pip install poetry
```

### Start a New Project
```bash
poetry new myproject        # Creates project structure
cd myproject

# OR initialize in existing directory
poetry init                 # Interactive setup - creates pyproject.toml
```

### pyproject.toml (Poetry's config file)
```toml
[tool.poetry]
name = "case-management-api"
version = "0.1.0"
description = "Case Management API"
authors = ["Chaman <chaman@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
pydantic = "^2.0"
sqlalchemy = "^2.0"
langchain = "^0.1.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.21"
httpx = "^0.25"         # For FastAPI test client

[build-system]
requires = ["poetry-core"]
build-backend = "poetry-core.masonry.api"
```

### Add & Remove Packages
```bash
poetry add fastapi              # Add to dependencies
poetry add pydantic@^2.0       # Specific version
poetry add --dev pytest         # Add to dev dependencies (--dev or -D)
poetry add httpx --dev

poetry remove flask             # Remove package
poetry update                   # Update all dependencies
poetry update fastapi           # Update specific package
```

### Install & Run
```bash
poetry install                  # Install all dependencies from poetry.lock
poetry install --no-dev         # Skip dev dependencies (production)

poetry run python main.py       # Run command in venv
poetry run pytest               # Run pytest
poetry run uvicorn main:app     # Run FastAPI

poetry shell                    # Activate venv in new shell
exit                            # Deactivate
```

### Useful Commands
```bash
poetry env info                 # Show venv info
poetry env list                 # List all envs
poetry show                     # List installed packages
poetry show --tree              # Dependency tree
poetry check                    # Validate pyproject.toml
poetry export -f requirements.txt > requirements.txt  # Export to requirements.txt
```

---

## requirements.txt vs poetry.lock

| Feature | requirements.txt | poetry.lock |
|---------|-----------------|-------------|
| Format | Simple list | Detailed lock file |
| Transitive deps | Manual | Automatic |
| Version resolution | Manual | Automatic |
| Hash verification | Optional | Built-in |
| Dev/prod split | Manual | `--dev` flag |

---

## Common Workflows

### New Project (FastAPI + GenAI style)
```bash
mkdir my-genai-api && cd my-genai-api
poetry init -n
poetry add fastapi uvicorn langchain openai pydantic-settings
poetry add --dev pytest pytest-asyncio httpx pytest-cov
poetry run uvicorn main:app --reload
```

### Clone Existing Project
```bash
git clone https://github.com/org/project
cd project
poetry install          # Installs exact versions from poetry.lock
poetry run pytest       # Run tests
```

### Venv with Venv (if not using Poetry)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Interview Questions

**Q: venv vs conda vs poetry?**
- **venv**: built-in, lightweight, only manages packages for current Python
- **conda**: manages Python versions + packages, good for data science/ML (handles non-Python deps)
- **poetry**: best for web apps — handles packaging + publishing + reproducible builds

**Q: What is poetry.lock?**
Exact snapshot of all installed packages including transitive dependencies with hashes. Guarantees reproducible installs. Never edit it manually. Commit it to git.

**Q: When would you use --no-dev in poetry install?**
In production Docker builds — skip test/dev dependencies to keep image smaller.

**Q: What's pyproject.toml?**
The modern Python project config file (PEP 518). Replaces setup.py, setup.cfg, requirements.txt. Used by Poetry, Flit, PDM, and many tools.
