"""Pytest configuration and shared fixtures for standard_interfaces tests.

This module provides common fixtures, test utilities, and configuration
for all test modules in the standard_interfaces package.
"""

import os
import sys
from pathlib import Path
import pytest
import xarray as xr
import numpy as np


def pytest_configure(config):
    """Configure pytest for continuous testing with environment persistence."""

    # Ensure we're using the Pixi Python interpreter
    project_root = Path(__file__).parent.parent
    pixi_python = project_root / ".pixi" / "envs" / "default" / "python.exe"

    if pixi_python.exists() and str(pixi_python) not in sys.executable:
        print(
            f"Warning: Using {sys.executable} instead of Pixi Python at {pixi_python}"
        )

    # Set environment variables for consistent test execution
    os.environ.setdefault("PYTHONPATH", str(project_root))
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("PIXI_PROJECT_ROOT", str(project_root))

    # Configure pytest for continuous testing
    config.option.verbose = max(config.option.verbose, 1)
    config.option.tb = "short"


def pytest_sessionstart(session):
    """Actions to perform at the start of a test session."""
    print("🔄 Starting pytest session with Pixi environment persistence")


def pytest_sessionfinish(session, exitstatus):
    """Actions to perform at the end of a test session."""
    if exitstatus == 0:
        print("✅ All tests passed - environment ready for next run")
    else:
        print(f"❌ Tests finished with exit status: {exitstatus}")


@pytest.fixture
def sample_data_array() -> xr.DataArray:
    """Create a sample DataArray for testing.

    Returns:
        xr.DataArray: Sample data array with coordinates and attributes.
    """
    data = np.random.rand(10, 5)
    coords = {"time": np.arange(10), "space": ["a", "b", "c", "d", "e"]}
    attrs = {"units": "meters", "description": "Sample test data"}

    return xr.DataArray(
        data=data,
        coords=coords,
        dims=["time", "space"],
        attrs=attrs,
        name="test_variable",
    )


@pytest.fixture
def sample_dataset() -> xr.Dataset:
    """Create a sample Dataset for testing.

    Returns:
        xr.Dataset: Sample dataset with multiple variables and coordinates.
    """
    time = np.arange(10)
    space = ["a", "b", "c", "d", "e"]

    # Create sample data variables
    temperature = xr.DataArray(
        data=20 + np.random.rand(10, 5) * 10,
        coords={"time": time, "space": space},
        dims=["time", "space"],
        attrs={"units": "celsius", "long_name": "Temperature"},
    )

    pressure = xr.DataArray(
        data=1013 + np.random.rand(10, 5) * 50,
        coords={"time": time, "space": space},
        dims=["time", "space"],
        attrs={"units": "hPa", "long_name": "Pressure"},
    )

    return xr.Dataset(
        data_vars={"temperature": temperature, "pressure": pressure},
        coords={
            "time": ("time", time, {"units": "seconds"}),
            "space": ("space", space, {"description": "spatial coordinates"}),
        },
        attrs={"title": "Test Dataset", "created_by": "pytest fixture"},
    )


@pytest.fixture
def coordinate_data() -> dict:
    """Create sample coordinate data for testing coordinate models.

    Returns:
        dict: Sample coordinate data structure.
    """
    return {
        "dims": ["x", "y", "z"],
        "coords": {
            "x": {
                "data": [0.0, 1.0, 2.0, 3.0, 4.0],
                "attrs": {
                    "units": "m",
                    "long_name": "x-coordinate in Cartesian system",
                    "axis": "X",
                },
            },
            "y": {
                "data": [0.0, 0.5, 1.0, 1.5, 2.0],
                "attrs": {
                    "units": "m",
                    "long_name": "y-coordinate in Cartesian system",
                    "axis": "Y",
                },
            },
            "z": {
                "data": [0.0, 10.0, 20.0, 30.0],
                "attrs": {
                    "units": "m",
                    "long_name": "z-coordinate in Cartesian system",
                    "axis": "Z",
                },
            },
        },
        "attrs": {
            "description": "Sample 3D coordinate system for testing",
        },
    }


@pytest.fixture
def polygon_geometry_data() -> dict:
    """Create sample polygon geometry data for testing.

    Returns:
        dict: Sample polygon geometry data structure.
    """
    return {
        "vertices": {"x": [0.0, 1.0, 1.0, 0.0, 0.0], "y": [0.0, 0.0, 1.0, 1.0, 0.0]},
        "attrs": {"description": "Unit square polygon", "area": 1.0},
    }


@pytest.fixture
def coil_geometry_data() -> dict:
    """Create sample coil geometry data for testing.

    Returns:
        dict: Sample coil geometry data structure.
    """
    return {
        "current": 1000.0,  # Amperes
        "turns": 10,
        "resistance": 0.05,  # Ohms
        "geometry": {"center": [0.0, 0.0, 0.0], "radius": 0.5, "height": 0.1},
        "attrs": {"coil_type": "circular", "material": "copper"},
    }


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically based on test names."""
    for item in items:
        # Add markers based on test file names
        if "geometry" in item.nodeid:
            item.add_marker(pytest.mark.geometry)
        if "pydantic" in item.nodeid:
            item.add_marker(pytest.mark.pydantic)
        if "schema" in item.nodeid:
            item.add_marker(pytest.mark.schema)

        # Add markers based on test function names
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
        if "network" in item.name:
            item.add_marker(pytest.mark.network)
        if "file" in item.name or "io" in item.name:
            item.add_marker(pytest.mark.file_io)


# Utility functions for tests
class TestHelpers:
    """Helper functions for tests."""

    @staticmethod
    def assert_data_array_equal(da1: xr.DataArray, da2: xr.DataArray, **kwargs):
        """Assert two DataArrays are equal with better error messages.

        Args:
            da1: First DataArray to compare.
            da2: Second DataArray to compare.
            **kwargs: Additional arguments passed to xarray.testing.assert_equal.
        """
        try:
            xr.testing.assert_equal(da1, da2, **kwargs)
        except AssertionError as e:
            # Add more context to the error message
            raise AssertionError(
                f"DataArrays are not equal:\n"
                f"First DataArray shape: {da1.shape}\n"
                f"Second DataArray shape: {da2.shape}\n"
                f"Original error: {e}"
            )

    @staticmethod
    def assert_dataset_structure(
        ds: xr.Dataset, expected_vars: list, expected_coords: list
    ):
        """Assert dataset has expected structure.

        Args:
            ds: Dataset to check.
            expected_vars: List of expected data variable names.
            expected_coords: List of expected coordinate names.
        """
        assert isinstance(ds, xr.Dataset), f"Expected Dataset, got {type(ds)}"

        # Check data variables
        missing_vars = set(expected_vars) - set(ds.data_vars.keys())
        assert not missing_vars, f"Missing data variables: {missing_vars}"

        # Check coordinates
        missing_coords = set(expected_coords) - set(ds.coords.keys())
        assert not missing_coords, f"Missing coordinates: {missing_coords}"


@pytest.fixture
def test_helpers() -> TestHelpers:
    """Provide test helper functions.

    Returns:
        TestHelpers: Instance of test helper class.
    """
    return TestHelpers()


@pytest.fixture
def sample_coordinate_array(coordinate_data) -> xr.DataArray:
    """Create a sample DataArray using the coordinate_data fixture.

    Args:
        coordinate_data: Coordinate data from the coordinate_data fixture.

    Returns:
        xr.DataArray: DataArray with proper coordinates and units.
    """
    coord_info = coordinate_data["coords"]
    dims = coordinate_data["dims"]

    # Determine shape from coordinate data lengths
    shape = tuple(len(coord_info[dim]["data"]) for dim in dims)

    # Create sample data
    data = np.random.rand(*shape)

    # Build coordinates dictionary
    coords = {}
    for dim in dims:
        if dim in coord_info:
            coords[dim] = ([dim], coord_info[dim]["data"], coord_info[dim]["attrs"])

    return xr.DataArray(
        data=data,
        coords=coords,
        dims=dims,
        attrs={
            "units": "1",  # CF convention for dimensionless
            "long_name": "Sample test data with proper coordinates",
            "description": "Generated for testing coordinate handling",
        },
        name="test_coordinate_variable",
    )
