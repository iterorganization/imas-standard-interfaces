# Tests

This directory contains test suites for validating JSON schemas used in the Standard Interfaces project.

## Test Files

- `test_polygon_geometry.py` - Comprehensive test suite using pytest for the base polygon geometry schema
- `test_polygon_basic.py` - Simple test runner that doesn't require pytest, useful for quick validation
- `__init__.py` - Makes this directory a Python package

## Running Tests

### Option 1: Simple Test Runner (No Dependencies)

Run the basic validation tests:

```bash
python tests/test_polygon_basic.py
```

This will validate the polygon geometry schema and test several validation scenarios.

### Option 2: Full Test Suite with pytest

First install pytest:

```bash
pip install pytest jsonschema
```

Then run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_polygon_geometry.py -v
```

## Test Coverage

The tests cover:

- **Schema Validity**: Ensures the JSON schema itself is valid
- **Valid Data**: Tests that properly structured polygon data validates successfully
- **Required Fields**: Tests that missing required fields cause validation failures
- **Data Types**: Tests that incorrect data types are rejected
- **Constraints**: Tests that business rules (e.g., minimum 3 nodes for polygons) are enforced
- **Optional Fields**: Tests that optional attributes work correctly
- **Edge Cases**: Tests minimal valid structures and boundary conditions

## Adding New Tests

When adding new schemas or modifying existing ones:

1. Create test files following the naming pattern `test_<schema_name>.py`
2. Include both positive tests (valid data should pass) and negative tests (invalid data should fail)
3. Test all required fields, constraints, and business rules
4. Add a basic test runner for quick validation during development

## Schema Validation

The tests use the `jsonschema` library to validate data against JSON Schema specifications. All schemas should follow JSON Schema Draft 7 specification.
