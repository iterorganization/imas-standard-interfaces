# Development Guide

This guide covers how to contribute to and develop with Standard Interfaces.

## Setup Development Environment

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/standard_interfaces.git
   cd standard_interfaces
   ```

2. **Install dependencies:**

   ```bash
   # Install all dependency groups
   uv sync --all-groups

   # Or install specific groups
   uv sync --group dev --group docs
   ```

3. **Verify installation:**
   ```bash
   uv run python -c "import jsonschema; print('✅ Setup complete')"
   ```

## Working with Schemas

### Schema Development Workflow

1. **Create/modify schemas** in `standard_interfaces/schemas/`
2. **Run validation tests** with `uv run pytest`
3. **Generate documentation** with `python docs.py generate`
4. **Preview documentation** with `python docs.py dev-serve`

### Schema Best Practices

#### Naming Conventions

- Use kebab-case for file names: `coil-current.schema.json`
- Use camelCase for property names: `longName`
- Use snake_case for dimension names: `time_index`

#### Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.standard-interfaces.org/category/name.schema.json",
  "title": "Descriptive Title",
  "description": "Clear description of what this schema represents",
  "type": "object",
  "properties": {
    "dimensions": {
      "type": "object",
      "description": "Dimension definitions"
    },
    "variables": {
      "type": "object",
      "description": "Variable definitions"
    },
    "attributes": {
      "type": "object",
      "description": "Global attributes"
    }
  },
  "required": ["dimensions", "variables"]
}
```

#### Documentation

- Always include `title` and `description`
- Use clear, concise descriptions for all properties
- Include units in variable descriptions
- Provide examples where helpful

### Schema Categories

#### Base Schemas (`schemas/base/`)

Fundamental structures used across categories:

- Geometric primitives
- Common data types
- Shared utilities

#### Domain-Specific Schemas

- `pf_active/` - Poloidal field active coils
- `tf_active/` - Toroidal field active coils
- Add new categories as needed

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=standard_interfaces

# Run specific test file
uv run pytest tests/test_polygon_geometry.py -v
```

### Writing Tests

Create test files in `tests/` following this pattern:

```python
import json
import pytest
import jsonschema
from pathlib import Path

class TestSchemaName:
    @pytest.fixture
    def schema(self):
        schema_path = Path("standard_interfaces/schemas/category/name.schema.json")
        with open(schema_path) as f:
            return json.load(f)

    @pytest.fixture
    def valid_data(self):
        return {
            "dimensions": {"time": 10},
            "variables": {
                "time": {
                    "dimensions": ["time"],
                    "data": list(range(10))
                }
            }
        }

    def test_schema_is_valid(self, schema):
        """Test that the schema itself is valid."""
        # This will raise an exception if schema is invalid
        jsonschema.Draft7Validator.check_schema(schema)

    def test_valid_data_passes(self, schema, valid_data):
        """Test that valid data passes."""
        jsonschema.validate(valid_data, schema)

    def test_missing_required_fails(self, schema):
        """Test that missing required properties fail."""
        invalid_data = {"dimensions": {"time": 10}}  # missing variables

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_data, schema)
```

## Documentation

### Building Documentation

```bash
# Generate schema docs from JSON files
python docs.py generate

# Serve locally for development
python docs.py dev-serve

# Build static site
python docs.py build

# Deploy with versioning (requires git repo)
python docs.py deploy --version 1.0 --alias latest
```

### Documentation Structure

```
docs/
├── index.md              # Homepage
├── examples.md           # Usage examples
├── development.md        # This file
└── schemas/
    ├── index.md          # Schema overview
    ├── base.md           # Base schemas
    ├── pf_active.md      # PF active schemas
    └── *.md              # Auto-generated schema docs
```

### Writing Documentation

- Use clear, actionable language
- Include code examples
- Link between related concepts
- Update when schemas change

## Release Process

### Version Management with mike

1. **Prepare release:**

   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md   # Run tests and generate docs
   uv run pytest
   uv run python -m standard_interfaces.docs.generate
   ```

2. **Deploy documentation:**

   ```bash
   # Deploy new version
   uv run mike deploy --push --update-aliases 1.1 latest

   # Set as default
   uv run mike set-default --push latest
   ```

3. **Create GitHub release:**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

### Semantic Versioning

- **Major** (1.0.0): Breaking schema changes
- **Minor** (1.1.0): New schemas, backward-compatible changes
- **Patch** (1.1.1): Bug fixes, documentation updates

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Run tests
        run: uv run pytest --cov=standard_interfaces

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  docs:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: uv sync --group docs      - name: Generate and deploy docs        run: |
          python docs.py generate
          uv run mike deploy --push --update-aliases main latest
```

## Code Quality

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Linting

```bash
# Format code
uv run black .

# Check linting
uv run flake8 standard_interfaces/ tests/ scripts/

# Type checking
uv run mypy standard_interfaces/
```

## Troubleshooting

### Common Issues

#### Schema Validation Errors

- Check JSON syntax with `python -m json.tool schema.json`
- Validate schema structure with online JSON Schema validator
- Review error messages carefully - they point to specific issues

#### Documentation Build Failures

- Ensure all referenced files exist
- Check that markdown is properly formatted
- Verify that `python docs.py generate` runs without errors

#### Import Errors

- Run `uv sync` to ensure dependencies are installed
- Check that you're using the right Python environment
- Verify file paths are correct

### Getting Help

- Check existing [GitHub Issues](https://github.com/your-username/standard_interfaces/issues)
- Review this documentation
- Ask questions in discussions
- Contribute improvements back to the project!
