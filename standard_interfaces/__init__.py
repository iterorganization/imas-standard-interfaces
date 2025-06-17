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

        __version__ = version("imas-standard-interfaces")
    except Exception:
        __version__ = "unknown"
