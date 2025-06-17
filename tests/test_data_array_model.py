"""Tests for DataArrayModel validation."""

from pint import UndefinedUnitError
import pytest
from pydantic import ValidationError

from standard_interfaces.validator import DataArrayModel, CoordinateModel


class TestDataArrayModelValidation:
    """Test cases for DataArrayModel validation."""

    def test_valid_data_array_model_minimal(self):
        """Test creation of valid DataArrayModel with minimal required fields."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "magnetic_field_strength", "units": "T"},
            "data": [1.0, 2.0, 3.0],
        }

        model = DataArrayModel(**data)

        assert model.dims == ("time",)
        assert model.attrs["standard_name"] == "magnetic_field_strength"
        assert model.attrs["units"] == "T"
        assert model.data == [1.0, 2.0, 3.0]
        assert isinstance(model.coords, CoordinateModel)

    def test_valid_data_array_model_with_coordinates(self):
        """Test DataArrayModel with coordinates."""
        data = {
            "dims": ("time", "space"),
            "coords": CoordinateModel(
                coords={
                    "time": [0, 1, 2, 3],
                    "space": (("space",), ["a", "b", "c"], {"units": "none"}),
                }
            ),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [[273.15, 274.15, 275.15], [276.15, 277.15, 278.15]],
        }

        model = DataArrayModel(**data)

        assert model.dims == ("time", "space")
        assert "time" in model.coords.coords
        assert "space" in model.coords.coords
        assert model.attrs["standard_name"] == "temperature"

    def test_valid_data_array_model_complex_data(self):
        """Test DataArrayModel with complex nested data."""
        data = {
            "dims": ("x", "y", "z"),
            "coords": CoordinateModel(
                coords={
                    "x": [0.0, 1.0, 2.0],
                    "y": [0.0, 0.5, 1.0],
                    "z": (
                        ("z",),
                        [0, 10, 20],
                        {"units": "m", "standard_name": "height"},
                    ),
                }
            ),
            "attrs": {
                "standard_name": "electric_field_strength",
                "units": "V.m^-1",
                "long_name": "Electric field strength in 3D space",
            },
            "data": [
                [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]],
                [[13.0, 14.0, 15.0], [16.0, 17.0, 18.0]],
            ],
        }

        model = DataArrayModel(**data)

        assert model.dims == ("x", "y", "z")
        assert len(model.data) == 3
        assert model.attrs["long_name"] == "Electric field strength in 3D space"

    def test_empty_dims_validation(self):
        """Test that empty dims raises ValidationError."""
        data = {
            "dims": (),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        DataArrayModel(**data)

    def test_invalid_dims_type_validation_error(self):
        """Test that non-string dims raise ValidationError."""
        data = {
            "dims": (123, "time"),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(ValidationError, match="Input should be a valid string"):
            DataArrayModel(**data)

    def test_empty_string_dims_validation_error(self):
        """Test that empty string dims raise ValidationError."""
        data = {
            "dims": ("time", ""),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(ValidationError, match="non-empty strings"):
            DataArrayModel(**data)

    def test_whitespace_only_dims_validation_error(self):
        """Test that whitespace-only dims raise ValidationError."""
        data = {
            "dims": ("time", "   "),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(ValidationError, match="non-empty strings"):
            DataArrayModel(**data)

    def test_missing_attrs_validation_error(self):
        """Test that missing attrs raises ValidationError."""
        data = {
            "dims": ("time",),
            "data": [1.0, 2.0, 3.0],
            # Missing attrs
        }

        with pytest.raises(ValidationError, match="Field required"):
            DataArrayModel(**data)

    def test_missing_data_validation_error(self):
        """Test that missing data raises ValidationError."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "temperature", "units": "K"},
            # Missing data
        }

        with pytest.raises(ValidationError, match="Field required"):
            DataArrayModel(**data)

    def test_invalid_standard_name_in_attrs(self):
        """Test that invalid standard_name in attrs raises ValidationError."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "Invalid Name With Spaces", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(
            NameError,
            match=(
                r"The proposed Standard Name \*\*Invalid Name With Spaces\*\* "
                r"is \*not\* valid\."
            ),
        ):
            DataArrayModel(**data)

    def test_invalid_units_in_attrs(self):
        """Test that invalid units in attrs raises ValidationError."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "temperature", "units": "invalid_unit_xyz"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(
            UndefinedUnitError,
            match=r"\'invalid_unit_xyz\' is not defined in the unit registry",
        ):
            DataArrayModel(**data)

    def test_missing_units_with_standard_name(self):
        """Test that missing units with standard_name raises ValidationError."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "temperature"},  # Missing units
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(
            ValidationError, match="units are required when standard_name"
        ):
            DataArrayModel(**data)

    def test_valid_special_units(self):
        """Test that special units like 'none' are accepted."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "dimensionless_quantity", "units": "none"},
            "data": [1.0, 2.0, 3.0],
        }

        model = DataArrayModel(**data)

        assert model.attrs["units"] == "none"

    def test_attrs_without_standard_name_and_units(self):
        """Test that attrs without standard_name and units are valid."""
        data = {
            "dims": ("time",),
            "attrs": {"long_name": "Test variable", "description": "A test variable"},
            "data": [1.0, 2.0, 3.0],
        }

        model = DataArrayModel(**data)

        assert model.attrs["long_name"] == "Test variable"
        assert model.attrs["description"] == "A test variable"

    def test_single_dimension_array(self):
        """Test DataArrayModel with single dimension."""
        data = {
            "dims": ("x",),
            "attrs": {"standard_name": "position", "units": "m"},
            "data": [0.0, 1.0, 2.0, 3.0, 4.0],
        }

        model = DataArrayModel(**data)

        assert len(model.dims) == 1
        assert model.dims[0] == "x"
        assert len(model.data) == 5

    def test_multidimensional_array(self):
        """Test DataArrayModel with multiple dimensions."""
        data = {
            "dims": ("time", "space", "depth"),
            "attrs": {"standard_name": "sea_water_temperature", "units": "C"},
            "data": [
                [[15.0, 14.0], [13.0, 12.0]],
                [[16.0, 15.0], [14.0, 13.0]],
                [[17.0, 16.0], [15.0, 14.0]],
            ],
        }

        model = DataArrayModel(**data)

        assert len(model.dims) == 3
        assert "time" in model.dims
        assert "space" in model.dims
        assert "depth" in model.dims

    def test_mixed_data_types(self):
        """Test DataArrayModel with mixed data types."""
        data = {
            "dims": ("mixed",),
            "attrs": {"description": "Mixed data types"},
            "data": [1, 2.5, "string", True, None],
        }

        model = DataArrayModel(**data)

        assert model.data == [1, 2.5, "string", True, None]

    def test_default_coordinate_model(self):
        """Test that default CoordinateModel is created when coords not provided."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "temperature", "units": "K"},
            "data": [1.0, 2.0, 3.0],
        }

        model = DataArrayModel(**data)

        assert isinstance(model.coords, CoordinateModel)
        assert len(model.coords.coords) == 0  # Empty coords dict by default

    def test_coordinate_model_integration(self):
        """Test integration with CoordinateModel."""
        data = {
            "dims": ("time", "space"),
            "coords": CoordinateModel(
                coords={
                    "time": (
                        ("time",),
                        [0, 1, 2],
                        {"standard_name": "time", "units": "s"},
                    ),
                    "space": ["x", "y", "z"],
                }
            ),
            "attrs": {"standard_name": "velocity", "units": "m.s^-1"},
            "data": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        }

        model = DataArrayModel(**data)

        assert model.dims == ("time", "space")
        assert len(model.coords.coords) == 2

    def test_attrs_validation_with_capital_standard_name(self):
        """Test attrs validation using invalid fixture."""
        data = {
            "dims": ("time",),
            "attrs": {"standard_name": "Invalid", "units": "s"},
            "data": [1.0, 2.0, 3.0],
        }

        with pytest.raises(
            NameError,
            match=r"The proposed Standard Name \*\*Invalid\*\* is \*not\* valid.",
        ):
            DataArrayModel(**data)
