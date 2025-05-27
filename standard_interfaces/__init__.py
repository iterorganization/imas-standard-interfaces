"""
Standard Interfaces - NetCDF schemas for tokamak data interfaces

This package provides tools and schemas for standardizing data formats
in fusion/tokamak research applications.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations
    try:
        from importlib.metadata import version
        __version__ = version("standard-interfaces")
    except Exception:
        __version__ = "unknown"

from .cdl_to_json_schema import (
    CDLParser,
    CDLVariable,
    CDLDimension,
    JSONSchemaGenerator,
)
from .build import main as build_main, run_command
from .schema_access import (
    load_schema,
    load_definition,
    get_schema_path,
    get_definition_path,
    list_schemas,
    list_definitions,
    get_schema_categories,
    get_definition_categories,
)

__all__ = [
    "CDLParser",
    "CDLVariable",
    "CDLDimension",
    "JSONSchemaGenerator",
    "build_main",
    "run_command",
    "load_schema",
    "load_definition",
    "get_schema_path",
    "get_definition_path",
    "list_schemas",
    "list_definitions",
    "get_schema_categories",
    "get_definition_categories",
    "__version__",
]
