from pint import UndefinedUnitError
from pydantic import ValidationError
import pytest
from typing import Any

from standard_interfaces.validator import CoordinateModel, StandardAttrs


class TestCoordinateModel:
    """Comprehensive tests for CoordinateModel validation."""

    def test_empty_coords(self):
        """Test that empty coordinates dictionary is valid."""
        model = CoordinateModel()
        assert model.coords == {}  # Should be empty dict

    def test_simple_format_coordinates(self):
        """Test coordinates using simple format (list of values)."""
        # Use Any to bypass strict type checking in tests
        coords: dict[str, Any] = {
            "time": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "x": [0, 1, 2, 3],
            "pressure": [1000.0, 850.0, 500.0],
        }
        model = CoordinateModel(coords=coords)
        assert model.coords == coords

    def test_coordinate_with_units_only(self):
        """Test coordinates with only units (no standard_name)."""
        coords: dict[str, Any] = {
            "pressure": ("level", [1000, 850, 500], {"units": "hPa"}),
        }
        model = CoordinateModel(coords=coords)
        assert model.coords == coords

    def test_coordinate_with_standard_name_and_units(self):
        """Test coordinate with valid standard_name and units."""
        coords: dict[str, Any] = {
            "temperature": (
                "x",
                [273.15, 283.15, 293.15],
                {"standard_name": "air_temperature", "units": "K"},
            ),
        }
        model = CoordinateModel(coords=coords)
        assert model.coords == coords

    def test_coordinate_standard_name_requires_units(self):
        """Test that standard_name requires units (CF convention)."""
        coords: dict[str, Any] = {
            "temp": (
                "temp",
                [273.15, 283.15],
                {"standard_name": "air_temperature"},  # Missing required units
            ),
        }
        with pytest.raises(
            ValidationError,
            match="units are required when standard_name is specified",
        ):
            CoordinateModel(coords=coords)

    def test_invalid_coordinate_format_string(self):
        """Test that string coordinate values are rejected."""
        coords: dict[str, Any] = {
            "invalid": "this_should_be_a_list_or_tuple",
        }
        with pytest.raises(
            ValidationError, match="Input should be a valid (list|tuple)"
        ):
            CoordinateModel(coords=coords)

    def test_invalid_coordinate_format_wrong_tuple_length(self):
        """Test that tuples with wrong length are rejected."""
        coords: dict[str, Any] = {
            "invalid": ("x", [1, 2]),  # Missing attrs (should be 3-tuple)
        }
        with pytest.raises(ValidationError, match="coords.invalid"):
            CoordinateModel(coords=coords)


class TestStandardAttrs:
    """Test the StandardAttrs validation separately."""

    def test_both_none_by_default(self):
        """Test that both fields default to None."""
        attrs = StandardAttrs(standard_name=None, units=None)
        assert attrs.standard_name is None
        assert attrs.units is None

    def test_only_units(self):
        """Test that only units without standard_name is valid."""
        attrs = StandardAttrs(standard_name=None, units="m")
        assert attrs.units == "m"
        assert attrs.standard_name is None

    def test_standard_name_requires_units(self):
        """Test CF convention: standard_name requires units."""
        with pytest.raises(ValueError, match="units are required"):
            StandardAttrs(standard_name="air_temperature", units=None)

    def test_both_provided(self):
        """Test that both standard_name and units work together."""
        attrs = StandardAttrs(standard_name="air_temperature", units="K")
        assert attrs.standard_name == "air_temperature"
        assert attrs.units == "K"

    def test_invalid_standard_name_format(self):
        """Test various invalid standard_name formats."""
        with pytest.raises(NameError, match="is \\*not\\* valid"):
            StandardAttrs(standard_name="Air Temperature", units="K")

    def test_valid_standard_name_format(self):
        """Test valid standard_name formats."""
        attrs = StandardAttrs(standard_name="air_temperature", units="K")
        assert attrs.standard_name == "air_temperature"

    def test_special_units(self):
        """Test allowed special units."""
        for unit in ["none", "", "undefined"]:
            attrs = StandardAttrs(standard_name="area_fraction", units=unit)
            assert attrs.units == unit

    def test_invalid_units(self):
        """Test invalid units."""
        with pytest.raises(
            UndefinedUnitError,
            match=r"'invalid_unit' is not defined in the unit registry",
        ):
            StandardAttrs(standard_name="air_temperature", units="invalid_unit")
