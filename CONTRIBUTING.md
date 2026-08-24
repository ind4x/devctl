# Contributing to devctl

Thank you for your interest in contributing to `devctl`! We welcome contributions from the community to make this tool even better.

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/devctl.git
   cd devctl
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies in editable mode**:
   ```bash
   pip install -e .
   ```
4. **Run tests**:
   ```bash
   pytest
   ```

---

## Project Structure Overview

```text
devctl/
├── commands/            # Typer CLI subcommands (init, add, run, docker, deploy, tui)
├── generators/          # Self-contained framework generator packages
│   ├── angular/
│   ├── django/
│   ├── docker/
│   ├── fastapi/
│   ├── go_fiber/
│   ├── nestjs/
│   ├── nextjs/
│   ├── nodejs/
│   ├── react/
│   ├── spring/
│   ├── svelte/
│   └── vue/
├── orchestrator/        # Scanner, process manager, and environment launcher
├── tui/                 # Textual terminal user interface
└── utils/               # Cross-platform helpers and dependency checkers
```

---

## How to Add a New Framework / Generator

`devctl` uses a **100% self-contained package structure** for every supported framework. Follow these step-by-step instructions to add support for a new framework (e.g. `myframework`):

### Step 1: Create the Framework Package Directory

Create a new directory inside `devctl/generators/` with `templates/` and `tests/` subdirectories:

```bash
mkdir -p devctl/generators/myframework/templates/config
mkdir -p devctl/generators/myframework/templates/resource
mkdir -p devctl/generators/myframework/tests
touch devctl/generators/myframework/tests/__init__.py
```

### Step 2: Add Jinja2 Template Files (`.j2`)

Store boilerplate and resource stubs as Jinja2 templates:
- `devctl/generators/myframework/templates/config/` for setup files (e.g., `main.py.j2`, `config.json.j2`)
- `devctl/generators/myframework/templates/resource/` for resource/scaffolding stubs (e.g., `router.py.j2`, `model.py.j2`)

### Step 3: Implement `generator.py` and `scaffolder.py`

1. **`generator.py`**: Implements project initialization (`generate_myframework_boilerplate`).
   ```python
   import os
   import typer
   from jinja2 import Environment, FileSystemLoader


   def generate_myframework_boilerplate(project_name: str) -> bool:
       # Render templates from local templates/config folder
       templates_dir = os.path.join(os.path.dirname(__file__), "templates", "config")
       env = Environment(loader=FileSystemLoader(templates_dir))
       # File generation & setup steps...
       return True
   ```

2. **`scaffolder.py`**: Implements entity/resource scaffolding (`generate_myframework_resource`).
   ```python
   import os
   import typer
   from jinja2 import Environment, FileSystemLoader


   def generate_myframework_resource(resource_name: str, fields_str: str, root_path: str = "."):
       templates_dir = os.path.join(os.path.dirname(__file__), "templates", "resource")
       env = Environment(loader=FileSystemLoader(templates_dir))
       # Resource generation logic...
   ```

### Step 4: Expose the Public API in `__init__.py`

Create `devctl/generators/myframework/__init__.py`:

```python
"""
MyFramework generator and scaffolder.
"""

from devctl.generators.myframework.generator import generate_myframework_boilerplate
from devctl.generators.myframework.scaffolder import generate_myframework_resource

__all__ = [
    "generate_myframework_boilerplate",
    "generate_myframework_resource",
]
```

### Step 5: Add Local Unit Tests inside `tests/`

Create `devctl/generators/myframework/tests/test_myframework.py` to test boilerplate generation and scaffolding locally within the framework package:

```python
from typer.testing import CliRunner

from devctl.generators.myframework import generate_myframework_boilerplate

runner = CliRunner()


def test_init_myframework(tmp_path): ...


def test_add_resource_myframework(tmp_path): ...
```

### Step 6: Register the Framework in Commands & Scanner

1. **Update Scanner** (`devctl/orchestrator/scanner.py`): Add detection logic for your framework (e.g., checking for specific config files).
2. **Register Init Command** (`devctl/commands/init.py`): Add `@app.command("myframework")`.
3. **Register Add Resource Command** (`devctl/commands/add.py`): Add detection check and handler invocation.

---

## Code Quality & Formatting

We use `ruff` for linting and formatting, and `pytest` for testing:

```bash
# Check code style & linter rules
ruff check devctl test

# Format code automatically
ruff format devctl test

# Run full test suite
pytest
```

---

## Submitting Pull Requests

1. Fork the repository & create a feature branch (`git checkout -b feature/add-myframework`).
2. Ensure all tests pass (`pytest`) and code formatting is clean (`ruff check`).
3. Open a Pull Request with a summary of changes and framework capabilities.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
