"""
Standard Interfaces - NetCDF schemas for tokamak data interfaces

This package provides tools and schemas for standardizing data formats
in fusion/tokamak research applications.
"""

__version__ = "0.1.0"

from .cdl_to_json_schema import (
    CDLParser,
    CDLVariable,
    CDLDimension,
    JSONSchemaGenerator,
)
from .build import main as build_main, run_command

__all__ = [
    "CDLParser",
    "CDLVariable",
    "CDLDimension",
    "JSONSchemaGenerator",
    "build_main",
    "run_command",
    "__version__",
]
