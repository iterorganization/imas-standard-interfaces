"""
Test suite for base polygon geometry schema validation.

This module tests the polygon-geometry.schema.json schema against various
valid and invalid polygon geometry data structures.
"""

import json
import pytest
from importlib.resources import files
from jsonschema import validate, ValidationError, Draft7Validator


@pytest.fixture
def polygon_schema():
    """Load the polygon geometry schema."""
    schema_resource = files("standard_interfaces.schemas.base") / "polygon-geometry.schema.json"
    return json.loads(schema_resource.read_text())


@pytest.fixture
def valid_polygon_data():
    """Valid polygon geometry data structure."""
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


class TestPolygonGeometrySchema:
    """Test cases for polygon geometry schema validation."""

    def test_valid_polygon_validates(self, polygon_schema, valid_polygon_data):
        """Test that valid polygon data passes validation."""
        validate(instance=valid_polygon_data, schema=polygon_schema)
        # Should not raise any exception

    def test_schema_is_valid_draft7(self, polygon_schema):
        """Test that the schema itself is valid JSON Schema Draft 7."""
        Draft7Validator.check_schema(polygon_schema)

    def test_missing_required_dimensions_fails(
        self, polygon_schema, valid_polygon_data
    ):
        """Test that missing required dimensions cause validation failure."""
        # Remove required 'node' dimension
        del valid_polygon_data["dimensions"]["node"]

        with pytest.raises(ValidationError, match="'node' is a required property"):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_insufficient_nodes_fails(self, polygon_schema, valid_polygon_data):
        """Test that polygons with less than 3 nodes fail validation."""
        valid_polygon_data["dimensions"]["node"] = 2

        with pytest.raises(ValidationError, match="2 is less than the minimum of 3"):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_missing_geometry_container_fails(self, polygon_schema, valid_polygon_data):
        """Test that missing geometry container causes validation failure."""
        del valid_polygon_data["variables"]["geometry_container"]

        with pytest.raises(
            ValidationError, match="'geometry_container' is a required property"
        ):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_invalid_geometry_type_fails(self, polygon_schema, valid_polygon_data):
        """Test that invalid geometry type fails validation."""
        valid_polygon_data["variables"]["geometry_container"]["geometry_type"] = "line"

        with pytest.raises(
            ValidationError, match="'line' is not one of \\['polygon'\\]"
        ):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_missing_coordinate_variables_fails(
        self, polygon_schema, valid_polygon_data
    ):
        """Test that missing coordinate variables fail validation."""
        del valid_polygon_data["variables"]["r"]

        with pytest.raises(ValidationError, match="'r' is a required property"):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_coordinate_variables_without_units_fail(
        self, polygon_schema, valid_polygon_data
    ):
        """Test that coordinate variables without units fail validation."""
        del valid_polygon_data["variables"]["r"]["units"]

        with pytest.raises(ValidationError, match="'units' is a required property"):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_invalid_node_coordinates_pattern_fails(
        self, polygon_schema, valid_polygon_data
    ):
        """Test that invalid node_coordinates pattern fails validation."""
        # Invalid pattern - should be space-separated variable names
        valid_polygon_data["variables"]["geometry_container"]["node_coordinates"] = (
            "r,z"
        )

        with pytest.raises(ValidationError, match="does not match"):
            validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_valid_alternative_coordinates(self, polygon_schema, valid_polygon_data):
        """Test that alternative coordinate systems (x,y) validate correctly."""
        # Change to Cartesian coordinates
        valid_polygon_data["variables"]["geometry_container"]["node_coordinates"] = (
            "x y"
        )

        # Replace r,z variables with x,y
        del valid_polygon_data["variables"]["r"]
        del valid_polygon_data["variables"]["z"]

        valid_polygon_data["variables"]["x"] = {
            "dimensions": ["node"],
            "units": "m",
            "long_name": "Horizontal coordinate",
        }
        valid_polygon_data["variables"]["y"] = {
            "dimensions": ["node"],
            "units": "m",
            "long_name": "Vertical coordinate",
        }

        validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_minimal_valid_structure(self, polygon_schema):
        """Test minimal valid polygon structure."""
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

        validate(instance=minimal_data, schema=polygon_schema)

    def test_with_optional_standard_name(self, polygon_schema, valid_polygon_data):
        """Test that optional standard_name attribute validates correctly."""
        valid_polygon_data["variables"]["r"]["standard_name"] = "major_radius"
        valid_polygon_data["variables"]["z"]["standard_name"] = "height"

        validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_with_additional_attributes(self, polygon_schema, valid_polygon_data):
        """Test that additional attributes are allowed."""
        # Add custom attributes
        valid_polygon_data["variables"]["r"]["custom_attribute"] = "custom_value"
        valid_polygon_data["global_attributes"]["custom_global"] = "global_value"

        validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_polygon_node_count_valid_min(self, polygon_schema, valid_polygon_data):
        """Test polygon_node_count with valid_min attribute."""
        valid_polygon_data["variables"]["polygon_node_count"]["valid_min"] = 4

        validate(instance=valid_polygon_data, schema=polygon_schema)

    def test_invalid_valid_min_fails(self, polygon_schema, valid_polygon_data):
        """Test that invalid valid_min (less than 3) fails validation."""
        valid_polygon_data["variables"]["polygon_node_count"]["valid_min"] = 2

        with pytest.raises(ValidationError, match="2 is less than the minimum of 3"):
            validate(instance=valid_polygon_data, schema=polygon_schema)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
