"""
Simple test runner for polygon geometry schema validation.

This script provides basic validation tests without requiring pytest,
useful for quick validation during development.
"""

import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator


def load_polygon_schema():
    """Load the polygon geometry schema."""
    schema_path = (
        Path(__file__).parent.parent
        / "schemas"
        / "base"
        / "polygon-geometry.schema.json"
    )
    with open(schema_path, "r") as f:
        return json.load(f)


def get_valid_polygon_data():
    """Return valid polygon geometry data structure."""
    return {
        "dimensions": {"node": 8, "polygon": 2},
        "variables": {
            "geometry_container": {
                "geometry_type": "polygon",
                "node_coordinates": "r z",
                "node_count": "polygon_node_count",
            },
            "r": {
                "dimensions": ["node"],
                "units": "m",
                "long_name": "Major radius coordinate",
                "_FillValue": -999.0,
            },
            "z": {
                "dimensions": ["node"],
                "units": "m",
                "long_name": "Vertical coordinate",
                "_FillValue": -999.0,
            },
            "polygon_node_count": {
                "dimensions": ["polygon"],
                "long_name": "count of nodes per polygon",
                "valid_min": 3,
            },
        },
        "global_attributes": {
            "title": "Test Polygon Geometry",
            "institution": "Test Institution",
            "conventions": "CF-1.8",
        },
    }


def test_valid_polygon():
    """Test that valid polygon data passes validation."""
    schema = load_polygon_schema()
    data = get_valid_polygon_data()

    try:
        validate(instance=data, schema=schema)
        print("✓ Valid polygon data validation passed")
        return True
    except ValidationError as e:
        print(f"✗ Valid polygon data validation failed: {e.message}")
        return False


def test_schema_validity():
    """Test that the schema itself is valid."""
    schema = load_polygon_schema()

    try:
        Draft7Validator.check_schema(schema)
        print("✓ Schema is valid JSON Schema Draft 7")
        return True
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        return False


def test_missing_required_field():
    """Test that missing required fields cause validation failure."""
    schema = load_polygon_schema()
    data = get_valid_polygon_data()

    # Remove required field
    del data["dimensions"]["node"]

    try:
        validate(instance=data, schema=schema)
        print(
            "✗ Missing required field test failed - should have raised ValidationError"
        )
        return False
    except ValidationError:
        print("✓ Missing required field correctly causes validation failure")
        return True


def test_invalid_geometry_type():
    """Test that invalid geometry type fails validation."""
    schema = load_polygon_schema()
    data = get_valid_polygon_data()

    # Set invalid geometry type
    data["variables"]["geometry_container"]["geometry_type"] = "line"

    try:
        validate(instance=data, schema=schema)
        print(
            "✗ Invalid geometry type test failed - should have raised ValidationError"
        )
        return False
    except ValidationError:
        print("✓ Invalid geometry type correctly causes validation failure")
        return True


def test_insufficient_nodes():
    """Test that insufficient nodes cause validation failure."""
    schema = load_polygon_schema()
    data = get_valid_polygon_data()

    # Set insufficient nodes (less than 3)
    data["dimensions"]["node"] = 2

    try:
        validate(instance=data, schema=schema)
        print("✗ Insufficient nodes test failed - should have raised ValidationError")
        return False
    except ValidationError:
        print("✓ Insufficient nodes correctly cause validation failure")
        return True


def test_minimal_valid_structure():
    """Test minimal valid polygon structure."""
    schema = load_polygon_schema()
    minimal_data = {
        "dimensions": {"node": 3, "polygon": 1},
        "variables": {
            "geometry_container": {
                "geometry_type": "polygon",
                "node_coordinates": "r z",
                "node_count": "polygon_node_count",
            },
            "r": {"dimensions": ["node"], "units": "m"},
            "z": {"dimensions": ["node"], "units": "m"},
            "polygon_node_count": {"dimensions": ["polygon"]},
        },
    }

    try:
        validate(instance=minimal_data, schema=schema)
        print("✓ Minimal valid structure validation passed")
        return True
    except ValidationError as e:
        print(f"✗ Minimal valid structure validation failed: {e.message}")
        return False


def main():
    """Run all basic tests."""
    print("Running polygon geometry schema validation tests...\n")

    tests = [
        test_schema_validity,
        test_valid_polygon,
        test_missing_required_field,
        test_invalid_geometry_type,
        test_insufficient_nodes,
        test_minimal_valid_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line for readability

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
