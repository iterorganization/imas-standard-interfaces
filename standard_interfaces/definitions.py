import pathlib
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Final, Literal

import netCDF4
import xarray as xr
from IPython.display import HTML, display

from standard_interfaces.resources import Resource


class Definitions(Resource):
    """Manage Standard Interface Common Data Language (CDL) definitions."""

    RESOURCE_TYPE: Final[Literal["definitions"]] = "definitions"
    FILE_EXTENSION: Final[Literal[".cdl"]] = ".cdl"

    @property
    def resource_type(self) -> Literal["definitions"]:
        """Return the type of resource."""
        return self.RESOURCE_TYPE

    @property
    def file_extension(self) -> Literal[".cdl"]:
        """Return the file extension for this resource type."""
        return self.FILE_EXTENSION

    @contextmanager
    def _to_netcdf(self, cdl_file: str):
        """
        Context manager to convert CDL file to a netCDF file.

        Args:
            cdl_file: The CDL file path

        Yields:
            str: The temporary path to the converted netCDF file."""
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp_file:
            temp_file_path = pathlib.Path(temp_file.name)
            nc_file = temp_file_path.as_posix()
            with netCDF4.Dataset.fromcdl(cdl_file, ncfilename=nc_file):
                pass
            yield nc_file
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)

    @contextmanager
    def as_xarray(self, category: str, filename: str):
        """
        Context manager to convert CDL file directly to an xarray Dataset.
        
        Args:
            cdl_file: The CDL file path
            
        Yields:
            xr.Dataset: The xarray dataset
        """
        cdl_file = self.get_file(category, filename)
        with self._to_netcdf(cdl_file) as nc_filename:
            result = subprocess.run(['ncdump', '-h', nc_filename], capture_output=True, text=True, check=True)
            print(f"ncdump output for {nc_filename}:")
            print(result.stdout)
            with xr.open_dataset(nc_filename, engine="netcdf4") as ds:
                yield ds

    @contextmanager 
    def as_html(self, category: str, filename: str):
        """
        Context manager to convert CDL file to HTML.
        
        Args:
            cdl_file: The CDL file path
            
        Yields:
            HTML: The HTML representation of the dataset
        """
        with self.as_xarray(category, filename) as ds:
            yield ds._repr_html_()
    

if __name__ == "__main__":
    definitions = Definitions()

    with definitions.as_xarray("pf_active", "coil-current") as ds:
        print(ds)

    with definitions.as_html("pf_active", "coil-current") as html:
        display(HTML(html))
