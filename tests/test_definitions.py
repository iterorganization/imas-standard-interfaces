import os
import tempfile
import textwrap
from functools import wraps
from pathlib import Path

import pytest
import xarray as xr


def as_file(func):
    """
    Decorator that converts a CDL string generator function into a temporary file.

    Wraps functions that return CDL strings and converts their output to
    temporary files for use with parsers that expect file paths.

    Args:
        func: Function that returns a CDL string

    Returns:
        Function that returns a temporary file path containing the CDL content
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        cdl_content = func(*args, **kwargs)

        # Create temporary file with CDL content using NamedTemporaryFile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cdl", delete=False
        ) as tmp_file:
            tmp_file.write(cdl_content)
            return tmp_file.name

    return wrapper


@pytest.fixture
def coil_current_cdl():
    """
    Fixture that provides minimal working CDL content for coil current definition.

    Based on the coil-current.cdl structure with essential netCDF elements
    formatted as CDL text that can be written to a temporary file stream.

    Returns:
        str: CDL text content representing a simplified coil current definition
             suitable for testing schema generation.
    """
    return textwrap.dedent(
        """
        netcdf pf_active_coil_current {

        // Global attributes
        :title = "PF Active Coil Current" ;
        :institution = "ITER Organization" ;
        :source = "IMAS pf_active IDS current subset" ;
        :conventions = "CF-1.8, IMAS-3.0" ;
        :comment = "Poloidal field coil current time series and control data" ;
        :_FillValue_policy = "Standard netCDF fill values used for all time-series data (1.e+20 for double)" ;

        dimensions:
            time = UNLIMITED ;
            coil = UNLIMITED ;

        variables:
            double time(time) ;
                time:units = "s" ;
                time:long_name = "time coordinate" ;
                time:standard_name = "time" ;
                time:axis = "T" ;
                
            string coil_name(coil) ;
                coil_name:long_name = "coil identifier name" ;
                coil_name:description = "Human readable coil identifier (e.g., PF1, PF2, etc.)" ;

            double coil_current(time, coil) ;
                coil_current:units = "A" ;
                coil_current:long_name = "PF coil current" ;
                coil_current:standard_name = "electric_current" ;
                coil_current:coordinates = "time" ;
                coil_current:description = "Time-dependent current in each PF coil" ;

            double coil_current_reference(time, coil) ;
                coil_current_reference:units = "A" ;
                coil_current_reference:long_name = "PF coil reference current" ;
                coil_current_reference:standard_name = "electric_current" ;
                coil_current_reference:coordinates = "time" ;
                coil_current_reference:description = "Commanded/reference current for PF coils" ;

            double coil_resistance(coil) ;
                coil_resistance:units = "Ohm" ;
                coil_resistance:long_name = "PF coil resistance" ;
                coil_resistance:description = "DC resistance of each coil" ;
                coil_resistance:valid_min = 0.0 ;
        }
        """
    ).strip()


@pytest.fixture
@as_file
def minimal_cdl():
    """
    Fixture that provides minimal CDL content for testing.

    Returns:
        str: Path to temporary file containing minimal CDL content suitable
             for basic testing scenarios.
    """
    return textwrap.dedent(
        """
        netcdf minimal_coil_current {
            dimensions:
                time = UNLIMITED ;
                coil = 1 ;

            variables:
                double time(time) ;
                    time:units = "s" ;

                double coil_current(time, coil) ;
                    coil_current:units = "A" ;
            }
        """
    ).strip()

