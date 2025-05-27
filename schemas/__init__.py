"""
Schemas module for Standard Interfaces.

This module provides access to JSON schema files for validation
of scientific data structures.
"""

from pathlib import Path

# Get the path to the project root schemas directory
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_SCHEMAS_DIR = _PROJECT_ROOT / "schemas"

__all__ = []
