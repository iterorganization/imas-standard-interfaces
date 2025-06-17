from typing import Any, Dict, List, Union, Tuple, ClassVar

import xarray as xr
from pydantic import BaseModel, Field, field_validator, model_validator

from imas_standard_names.units import unit_registry


class StandardAttrs(BaseModel):
    """Model for validating optional standard_name and units."""

    ALLOWED_SPECIAL_UNITS: ClassVar[set[str]] = {"1", "none", "", "undefined"}

    standard_name: str | None = Field(None, description="Optional standard name")
    units: str | None = Field(None, description="Optional units")

    @field_validator("standard_name")
    @classmethod
    def validate_standard_name(cls, v: str | None) -> str | None:
        """
        Validate standard_name format if provided.

        Args:
            v: The standard_name value to validate

        Returns:
            str | None: The validated standard_name

        Raises:
            ValueError: If standard_name is invalid format
            NameError: If standard_name doesn't meet IMAS requirements
        """
        if v is None:
            return v

        if not isinstance(v, str) or not v.strip():
            raise ValueError("standard_name must be a non-empty string")

        if not (v.islower() and v[0].isalpha() and " " not in v):
            raise NameError(
                f"The proposed Standard Name **{v}** is *not* valid."
                "\n\nStandard names must:\n"
                "- be lowercase;\n"
                "- start with a letter;\n"
                "- and not contain whitespace."
            )

        return v

    @field_validator("units")
    @classmethod
    def validate_units(cls, v: str | None) -> str | None:
        """
        Validate units format if provided.

        Args:
            v: The units value to validate

        Returns:
            str | None: The validated units

        Raises:
            ValueError: If units are invalid
        """
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("units must be a string")

        if v.lower() not in cls.ALLOWED_SPECIAL_UNITS:
            pint_unit = f"{unit_registry.Unit(v):~U}"
            try:
                assert set(v.split(".")) == set(pint_unit.split("."))
            except Exception:
                raise ValueError(
                    f"units '{v}' must be a valid IMAS Standard Names unit "
                    f"such as {pint_unit} "
                    "following UDUNITS conventions or one of: "
                    f"{', '.join(cls.ALLOWED_SPECIAL_UNITS)}"
                )

        return v

    @model_validator(mode="after")
    def validate_fusion_convention(self) -> "StandardAttrs":
        """
        Enforce Fusion convention: units are required when standard_name is specified.

        Returns:
            StandardAttrs: The validated model instance

        Raises:
            ValueError: If standard_name is provided but units are missing
        """
        if self.standard_name is not None and self.units is None:
            raise ValueError(
                "units are required when standard_name is specified (Fusion convention)"
            )
        return self


CoordinateDict = Dict[
    str,
    Union[
        List[Union[str, int, float]],  # Simple 1D coordinate: coord_name -> [values]
        Tuple[
            Union[str, Tuple[str, ...]], List[Union[str, int, float]], Dict[str, Any]
        ],  # Full format: (dims, data, attrs)
    ],
]


class CoordinateModel(BaseModel):
    """
    Model for xarray-style coordinates using a simple dictionary pattern.

    Follows xarray's coordinate specification:
    coords = {
        'time': ['2020-01-01', '2020-01-02'],  # Simple format
        'lat': (['y', 'x'], lat_2d_array, {'units': 'degrees_north'})  # Full format
    }
    """

    coords: CoordinateDict = Field(
        default_factory=dict,
        description="Dictionary of coordinates following xarray pattern",
    )

    @field_validator("coords")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate coordinate dictionary structure"""
        for name, coord_def in v.items():
            if isinstance(coord_def, (list, tuple)) and not isinstance(coord_def, str):
                # Check if it's the full format tuple
                if (
                    isinstance(coord_def, tuple)
                    and len(coord_def) == 3
                    and isinstance(attrs := coord_def[2], dict)
                ):  # Full format: (dims, data, attrs)
                    StandardAttrs(
                        standard_name=attrs.get("standard_name"),
                        units=attrs.get("units"),
                    )
                    continue  # Valid full format
                elif isinstance(coord_def, list):
                    continue  # Valid simple format
            raise ValueError(f"Invalid coordinate definition for '{name}': {coord_def}")
        return v

    @property
    def dims(self) -> Tuple[str, ...]:
        """
        Get the dimension names from the coordinate dictionary.

        Returns:
            Tuple[str, ...]: Tuple of dimension names
        """
        return tuple(
            dim
            for coord in self.coords.values()
            if isinstance(coord, tuple)
            for dim in coord[0]
            if isinstance(coord[0], (tuple, list))
        )


class DataArrayModel(BaseModel):
    """
    Pydantic model for validating xarray DataArray objects.

    Attributes:
        dims: List of dimension names for the data array
        coords: CoordinateModel containing the coordinates
        attrs: Dictionary of data array attributes/metadata
        data: List containing the actual data values
    """

    dims: Tuple[str, ...] = Field(
        ...,
        description="List of dimension names",
        min_length=0,
    )
    coords: CoordinateModel = Field(
        default_factory=CoordinateModel,
        description="Coordinates following xarray pattern",
    )
    attrs: Dict[str, Any] = Field(
        ...,
        description="Data array attributes and metadata",
    )
    data: List[Any] = Field(
        ...,
        description="Data array values",
    )

    @field_validator("dims")
    @classmethod
    def validate_dims(cls, v: List[str]) -> List[str]:
        """Validate that all dimension names are non-empty strings."""
        if not all(isinstance(dim, str) and dim.strip() for dim in v):
            raise ValueError("All dimension names must be non-empty strings")
        return v

    @field_validator("attrs", mode="after")
    @classmethod
    def validate_standard_name(cls, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that attrs contains a valid standard_name."""  # Use StandardAttrs for validation
        StandardAttrs(
            standard_name=attrs.get("standard_name"), units=attrs.get("units")
        )
        return attrs


class DatasetModel(BaseModel):
    """
    Pydantic model for validating xarray Dataset objects.

    Attributes:
        dims: Dictionary mapping dimension names to their sizes
        coords: CoordinateModel containing the coordinates
        data_vars: Dictionary mapping variable names to DataArrayModel objects
        attrs: Dictionary of dataset attributes/metadata
    """

    dims: Dict[str, int] = Field(
        ...,
        description="Dictionary of dimension names and their sizes",
    )
    coords: CoordinateModel = Field(
        default_factory=CoordinateModel,
        description="Coordinates following xarray pattern",
    )
    data_vars: Dict[str, DataArrayModel] = Field(
        ...,
        description="Dictionary of data variables",
        min_length=0,
    )
    attrs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dataset attributes and metadata",
    )

    @field_validator("dims")
    @classmethod
    def validate_dims(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate that all dimension sizes are non-negative integers."""
        for name, size in v.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Dimension names must be non-empty strings")
            if not isinstance(size, int) or size < 0:
                raise ValueError(
                    f"Dimension '{name}' size must be a non-negative integer"
                )
        return v


# Mapping from xarray object types to their corresponding Pydantic models
_XARRAY_MODEL_MAP = {
    xr.DataArray: DataArrayModel,
    xr.Dataset: DatasetModel,
}


def validate_xarray_object(obj: Union[xr.DataArray, xr.Dataset]) -> bool:
    """
    Validate xarray object using the appropriate Pydantic model.

    Args:
        obj: The xarray DataArray or Dataset object to validate

    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Automatically determine the correct model class using type mapping
        model_class = _XARRAY_MODEL_MAP.get(type(obj))
        if model_class is None:
            raise TypeError(f"Unsupported object type: {type(obj)}")

        data_dict = obj.to_dict()
        model_class(**data_dict)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


if __name__ == "__main__":
    from standard_interfaces.definitions import Definitions

    definitions = Definitions()

    with definitions.as_xarray("pf_active", "coil-geometry") as ds:
        validate_xarray_object(ds)
